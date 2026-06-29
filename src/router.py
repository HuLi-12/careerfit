"""动态任务路由入口 — 使用 TaskRouter 决策 + 各服务执行"""

import os
import traceback

from schemas.models import AnalysisResult, ScoreResult
from services.resume_parser import ResumeParser
from services.jd_parser import JDParser
from services.evidence_matcher import EvidenceMatcher
from services.score_engine import ScoreEngine
from services.report_generator import ReportGenerator
from services.task_router import TaskRouter
from services.llm_enhancer import LLMEnhancer
from services.utils import load_json, dumps, normalize_text
from config import DATA_DIR

DEBUG = os.getenv("CAREERFIT_DEBUG") == "1"


class CareerFitRouter:
    def __init__(self):
        self.router = TaskRouter()
        self.rp = ResumeParser()
        self.jp = JDParser()
        self.em = EvidenceMatcher()
        self.sc = ScoreEngine()
        self.rg = ReportGenerator()
        self.enhancer = LLMEnhancer()
        self.capabilities = load_json(DATA_DIR / "capability_registry.json", {}).get("capabilities", [])

    def _capability_for_mode(self, mode: str) -> dict:
        """从 capability_registry 查找当前任务模式对应的能力配置"""
        for cap in self.capabilities:
            if mode in cap.get("task_modes", []):
                return cap
        return {}

    def analyze(self, user_input):
        text = normalize_text(user_input)
        decision = self.router.decide(text)

        if len(text) < 10 and decision.mode == "unknown":
            zero_score = ScoreResult(
                overall_score=0,
                recommendation="信息不足，无法计算匹配度",
                score_breakdown={
                    "core_skill_match": 0, "project_experience_match": 0,
                    "responsibility_match": 0, "resume_expression_quality": 0,
                    "risk_control": 0,
                },
                level="unknown",
                summary="当前信息不足，无法生成精确匹配报告。",
            )
            return AnalysisResult(
                {"input_type": "unknown", "task_mode": "unknown"},
                {}, {}, [], zero_score,
                "# 输入信息不足\n\n当前信息不足，无法生成精确匹配报告。系统可以先给出初步建议，但建议补充以下信息：\n\n1. 目标岗位\n2. 技能栈\n3. 项目经历\n4. 工作或学习经历\n5. 岗位 JD\n\n你可以按照以下格式输入：\n\n【简历】\n你的简历内容...\n\n【岗位JD】\n目标岗位描述...",
            )

        resume = self.rp.parse(decision.resume_text)
        job = self.jp.parse(decision.jd_text)
        matches = []
        score = self.sc.calculate([], "")
        report = ""

        # 获取能力配置（确定 scoring_strategy）
        cap = self._capability_for_mode(decision.mode)
        strategy_name = cap.get("scoring_strategy", "standard_match")

        try:
            if decision.mode in ("resume_jd_match", "recruiter_eval"):
                strategy = "recruiter_eval" if decision.mode == "recruiter_eval" else strategy_name
                matches = self.em.match(job, resume)
                score = self.sc.calculate(matches, resume.raw_text, strategy_name=strategy)
                base_report = (
                    self.rg.candidate(resume, job, matches, score)
                    if decision.mode == "resume_jd_match"
                    else self.rg.recruiter(resume, job, matches, score)
                )
                report = self.enhancer.enhance_report(base_report) if self.enhancer.available else base_report
            elif decision.mode == "interview_prepare":
                matches = self.em.match(job, resume)
                score = self.sc.calculate(matches, resume.raw_text, strategy_name=strategy_name)
                report = self.rg.interview_only(resume, job, matches)
            elif decision.mode == "skill_gap_plan":
                matches = self.em.match(job, resume)
                score = self.sc.calculate(matches, resume.raw_text, strategy_name=strategy_name)
                report = self.rg.skill_gap_only(decision.mode, matches)
            elif decision.mode == "resume_optimize":
                matches = self.em.match(job, resume) if decision.has_jd else []
                report = self.rg.resume_optimize_only(resume, matches)
            elif decision.mode == "resume_only":
                report = self.rg.resume_only(resume)
            elif decision.mode == "jd_only":
                report = self.rg.jd_only(job)
            else:
                report = "# 输入信息不足\n\n当前未检测到完整简历或岗位 JD。请按【简历】和【岗位JD】格式补充。"
        except Exception as e:
            if DEBUG:
                report = "# 报告生成异常\n\n```text\n" + traceback.format_exc() + "\n```"
            else:
                report = "# 报告生成异常\n\n系统在处理过程中遇到异常，请检查输入格式后重试。如问题持续，建议按【简历】和【岗位JD】格式重新输入。"

        return AnalysisResult(
            {"input_type": decision.mode, "task_mode": decision.mode},
            resume.to_dict(),
            job.to_dict(),
            [m.to_dict() for m in matches if isinstance(m, object) and hasattr(m, "to_dict")],
            score.to_dict() if hasattr(score, "to_dict") else score,
            report,
        )

    def run(self, user_input, output_format="markdown"):
        try:
            res = self.analyze(user_input)
            return dumps(res.to_dict()) if output_format == "json" else res.report_markdown
        except Exception as e:
            if DEBUG:
                return dumps({"error": str(e), "traceback": traceback.format_exc()}) if output_format == "json" else f"# 系统异常\n\n```text\n{traceback.format_exc()}\n```"
            if output_format == "json":
                return dumps({"error": str(e), "message": "系统处理异常，请检查输入后重试"})
            return f"# 系统异常\n\n处理过程中发生异常：{str(e)}\n\n请检查输入内容后重试。"
