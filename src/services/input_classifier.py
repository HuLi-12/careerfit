from services.utils import normalize_text, contains_any, extract_between

RESUME_HINTS = [
    "简历",
    "教育经历",
    "工作经历",
    "项目经历",
    "技能",
    "证书",
    "自我评价",
    "resume",
    "education",
    "experience",
    "project",
    "skills",
]
JD_HINTS = [
    "岗位jd",
    "jd",
    "职位描述",
    "任职要求",
    "岗位职责",
    "招聘",
    "职位要求",
    "job description",
    "requirements",
    "responsibilities",
]
RECRUITER_HINTS = ["我是招聘方", "招聘方", "候选人", "初筛", "是否进入面试", "评估候选人"]
OPTIMIZE_HINTS = ["优化简历", "润色简历", "改简历", "简历优化", "帮我改"]


def split_resume_and_jd(text):
    text = normalize_text(text)
    resume = extract_between(
        text,
        ["【简历】", "[简历]", "简历：", "简历:"],
        ["【岗位JD】", "【JD】", "[岗位JD]", "[JD]", "岗位JD：", "岗位JD:", "JD：", "JD:"],
    )
    jd = extract_between(
        text,
        ["【岗位JD】", "【JD】", "[岗位JD]", "[JD]", "岗位JD：", "岗位JD:", "JD：", "JD:"],
        ["【简历】", "[简历]"],
    )
    if not resume and not jd:
        low = text.lower()
        pos = []
        for m in ["岗位jd", "jd", "职位描述", "任职要求", "岗位职责", "招聘"]:
            p = low.find(m.lower())
            if p != -1:
                pos.append(p)
        if pos:
            c = min(pos)
            resume = text[:c].strip()
            jd = text[c:].strip()
        else:
            resume = (
                text
                if contains_any(text, RESUME_HINTS) and not contains_any(text, JD_HINTS)
                else ""
            )
            jd = text if contains_any(text, JD_HINTS) and not resume else ""
    return {"resume_text": resume, "jd_text": jd}


def classify_input(user_input):
    text = normalize_text(user_input)
    if not text or len(text) < 10:
        return {
            "input_type": "unknown",
            "has_resume": False,
            "has_jd": False,
            "task_mode": "unknown",
            "user_role": "unknown",
            "missing_fields": ["有效输入内容"],
            "resume_text": "",
            "jd_text": "",
        }
    parts = split_resume_and_jd(text)
    resume = parts["resume_text"]
    jd = parts["jd_text"]
    has_resume = bool(resume) or contains_any(text, RESUME_HINTS)
    has_jd = bool(jd) or contains_any(text, JD_HINTS)
    recruiter = contains_any(text, RECRUITER_HINTS)
    opt = contains_any(text, OPTIMIZE_HINTS)
    if has_resume and has_jd:
        it = "resume_and_jd"
        mode = "recruiter_eval" if recruiter else "match_analysis"
    elif has_resume:
        it = "resume_only"
        mode = "resume_optimization" if opt else "career_planning"
        resume = resume or text
    elif has_jd:
        it = "jd_only"
        mode = "jd_optimization"
        jd = jd or text
    else:
        it = "unknown"
        mode = "unknown"
    miss = []
    if it == "resume_only":
        miss = ["岗位JD"]
    if it == "jd_only":
        miss = ["候选人简历"]
    if it == "unknown":
        miss = ["简历", "岗位JD"]
    return {
        "input_type": it,
        "has_resume": has_resume,
        "has_jd": has_jd,
        "task_mode": mode,
        "user_role": "recruiter" if recruiter else "candidate",
        "missing_fields": miss,
        "resume_text": resume,
        "jd_text": jd,
    }
