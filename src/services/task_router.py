"""动态任务路由 — 根据用户输入判断任务模式并返回执行决策"""

from dataclasses import dataclass, field
from typing import List

from services.input_classifier import classify_input, split_resume_and_jd
from services.utils import normalize_text, contains_any

# ── 任务模式常量 ──
RESUME_JD_MATCH = "resume_jd_match"
RECRUITER_EVAL = "recruiter_eval"
RESUME_ONLY = "resume_only"
JD_ONLY = "jd_only"
INTERVIEW_PREPARE = "interview_prepare"
RESUME_OPTIMIZE = "resume_optimize"
SKILL_GAP_PLAN = "skill_gap_plan"
UNKNOWN = "unknown"

# ── 触发关键词 ──
INTERVIEW_HINTS = [
    "面试准备", "面试预测", "面试追问", "面试题", "会问什么",
    "面试官", "面试问题", "面试模拟", "mock interview",
]
RESUME_OPTIMIZE_HINTS = [
    "优化简历", "润色简历", "改简历", "简历优化", "帮我改",
    "简历修改", "简历建议",
]
SKILL_GAP_HINTS = [
    "补差", "技能差距", "学习路线", "补强", "技术短板",
    "学习计划", "提升计划", "skill gap", "learning path",
]
RECRUITER_HINTS = ["我是招聘方", "招聘方", "候选人", "初筛", "是否进入面试", "评估候选人"]


@dataclass
class TaskDecision:
    """任务路由决策结果"""
    mode: str = UNKNOWN
    user_role: str = "candidate"
    has_resume: bool = False
    has_jd: bool = False
    resume_text: str = ""
    jd_text: str = ""
    missing_fields: List[str] = field(default_factory=list)
    raw_text: str = ""


class TaskRouter:
    """动态任务路由：分析用户输入 → 判断任务模式 → 返回执行决策"""

    @staticmethod
    def decide(text: str) -> TaskDecision:
        raw = normalize_text(text)
        if not raw or len(raw) < 10:
            return TaskDecision(mode=UNKNOWN, missing_fields=["有效输入内容"], raw_text=raw)

        # 1. 基础输入分类（判断有无简历/JD）
        c = classify_input(raw)
        it = c["input_type"]
        low = raw.lower()

        # 2. 由 input_type 推导基础模式
        if it == "resume_and_jd":
            mode = RECRUITER_EVAL if contains_any(raw, RECRUITER_HINTS) else RESUME_JD_MATCH
        elif it == "resume_only":
            mode = RESUME_ONLY
        elif it == "jd_only":
            mode = JD_ONLY
        else:
            mode = UNKNOWN

        # 3. 精细模式覆盖：面试/优化/补差
        if contains_any(raw, INTERVIEW_HINTS) and it != "jd_only":
            mode = INTERVIEW_PREPARE
        elif contains_any(raw, SKILL_GAP_HINTS) and it != "jd_only":
            mode = SKILL_GAP_PLAN
        elif contains_any(raw, RESUME_OPTIMIZE_HINTS) and it != "jd_only":
            mode = RESUME_OPTIMIZE

        return TaskDecision(
            mode=mode,
            user_role="recruiter" if contains_any(raw, RECRUITER_HINTS) else "candidate",
            has_resume=c["has_resume"],
            has_jd=c["has_jd"],
            resume_text=c.get("resume_text", ""),
            jd_text=c.get("jd_text", ""),
            missing_fields=c.get("missing_fields", []),
            raw_text=raw,
        )

    @staticmethod
    def is_match(mode: str) -> bool:
        return mode in (RESUME_JD_MATCH, RECRUITER_EVAL)

    @staticmethod
    def requires_resume(mode: str) -> bool:
        return mode in (RESUME_JD_MATCH, RECRUITER_EVAL, RESUME_ONLY,
                        INTERVIEW_PREPARE, RESUME_OPTIMIZE, SKILL_GAP_PLAN)

    @staticmethod
    def requires_jd(mode: str) -> bool:
        return mode in (RESUME_JD_MATCH, RECRUITER_EVAL, JD_ONLY)
