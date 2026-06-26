from schemas.models import AnalysisResult, ScoreResult
from services.input_classifier import classify_input
from services.resume_parser import ResumeParser
from services.jd_parser import JDParser
from services.evidence_matcher import EvidenceMatcher
from services.score_engine import ScoreEngine
from services.report_generator import ReportGenerator
from services.utils import dumps, normalize_text


class CareerFitRouter:
    def __init__(self):
        self.rp = ResumeParser()
        self.jp = JDParser()
        self.em = EvidenceMatcher()
        self.sc = ScoreEngine()
        self.rg = ReportGenerator()

    def analyze(self, user_input):
        text = normalize_text(user_input)
        c = classify_input(text)
        # 短输入处理：信息不足，给出引导（方案11.2）
        if len(text) < 10 and c["input_type"] == "unknown":
            zero_score = ScoreResult(
                overall_score=0,
                recommendation="信息不足，无法计算匹配度",
                score_breakdown={
                    "core_skill_match": 0,
                    "project_experience_match": 0,
                    "responsibility_match": 0,
                    "resume_expression_quality": 0,
                    "risk_control": 0,
                },
                level="unknown",
                summary="当前信息不足，无法生成精确匹配报告。",
            )
            return AnalysisResult(
                c,
                {},
                {},
                [],
                zero_score,
                "# 输入信息不足\n\n当前信息不足，无法生成精确匹配报告。系统可以先给出初步建议，但建议补充以下信息：\n\n1. 目标岗位\n2. 技能栈\n3. 项目经历\n4. 工作或学习经历\n5. 岗位 JD\n\n你可以按照以下格式输入：\n\n【简历】\n你的简历内容...\n\n【岗位JD】\n目标岗位描述...",
            )
        resume = self.rp.parse(c.get("resume_text", ""))
        job = self.jp.parse(c.get("jd_text", ""))
        matches = []
        score = self.sc.calculate([], "")
        report = ""
        try:
            if c["input_type"] == "resume_and_jd":
                matches = self.em.match(job, resume)
                score = self.sc.calculate(matches, resume.raw_text)
                report = (
                    self.rg.recruiter(resume, job, matches, score)
                    if c.get("task_mode") == "recruiter_eval" or c.get("user_role") == "recruiter"
                    else self.rg.candidate(resume, job, matches, score)
                )
            elif c["input_type"] == "resume_only":
                report = self.rg.resume_only(resume)
            elif c["input_type"] == "jd_only":
                report = self.rg.jd_only(job)
            else:
                report = "# 输入信息不足\n\n当前未检测到完整简历或岗位 JD。请按【简历】和【岗位JD】格式补充。"
        except Exception:
            report = "# 报告生成异常\n\n系统在处理过程中遇到异常，请检查输入格式后重试。如问题持续，建议按【简历】和【岗位JD】格式重新输入。"
        return AnalysisResult(
            c,
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
            if output_format == "json":
                return dumps({"error": str(e), "message": "系统处理异常，请检查输入后重试"})
            return f"# 系统异常\n\n处理过程中发生异常：{str(e)}\n\n请检查输入内容后重试。"
