import re
from schemas.models import JobProfile, RequirementItem
from services.skill_normalizer import SkillNormalizer
from services.utils import normalize_text, split_lines, unique

TYPE = {
    "Java": "hard_skill",
    "Python": "hard_skill",
    "Go": "hard_skill",
    "JavaScript": "hard_skill",
    "Spring Boot": "framework",
    "Spring": "framework",
    "MyBatis": "framework",
    "Vue": "framework",
    "React": "framework",
    "MySQL": "database",
    "Redis": "database",
    "PostgreSQL": "database",
    "MongoDB": "database",
    "Git": "tool",
    "Docker": "tool",
    "Linux": "tool",
    "接口开发": "project_experience",
    "数据库设计": "project_experience",
    "系统设计": "project_experience",
    "高并发": "project_experience",
    "缓存": "database",
    "性能优化": "project_experience",
    "沟通协作": "soft_skill",
}
COMMON = list(TYPE.keys()) + ["SQL", "权限管理", "机器学习", "深度学习", "数据分析"]


class JDParser:
    def __init__(self):
        self.norm = SkillNormalizer()

    def parse(self, text):
        text = normalize_text(text)
        p = JobProfile(raw_text=text)
        if not text:
            return p
        p.position_name = self.position(text)
        p.seniority_level = self.level(text)
        keys = self.keys(text)
        p.evaluation_keywords = keys
        p.must_have_requirements = self.reqs(text, keys, True)
        p.nice_to_have_requirements = self.reqs(text, keys, False)
        p.responsibilities = [
            l
            for l in split_lines(text)
            if any(k in l for k in ["负责", "参与", "完成", "设计", "开发", "维护", "优化", "协作"])
        ][:10]
        p.hidden_requirements = self.hidden(text, keys)
        return p

    def position(self, text):
        for pat in [
            r"岗位名称[:：]\s*([^\n]+)",
            r"职位[:：]\s*([^\n]+)",
            r"招聘\s*([^，,\n。]+)",
            r"([A-Za-z]+|Java|Python|前端|后端|算法|产品|运营|测试|数据).{0,12}(工程师|开发|经理|实习生)",
        ]:
            m = re.search(pat, text, re.I)
            if m:
                return "".join(m.groups()).strip()[:40]
        return "未明确岗位"

    def level(self, text):
        if any(k in text for k in ["实习", "应届", "校招"]):
            return "实习/应届"
        if any(k in text for k in ["高级", "专家", "架构师", "5年以上"]):
            return "高级"
        if any(k in text for k in ["3年以上", "中级"]):
            return "中级"
        if any(k in text for k in ["1年", "初级", "初中级"]):
            return "初中级"
        return "unknown"

    def keys(self, text):
        low = text.lower()
        return self.norm.many([s for s in COMMON if s.lower() in low or s in text])

    def reqs(self, text, keys, must):
        lines = split_lines(text)
        target = [
            l
            for l in lines
            if any(
                k in l
                for k in (
                    ["要求", "必须", "熟悉", "掌握", "负责", "能够", "具备"] if must else ["优先", "加分", "更佳", "最好"]
                )
            )
        ]
        out = []
        for kw in keys:
            hit = any(kw.lower() in l.lower() or kw in l for l in target)
            if hit or (must and not target):
                out.append(
                    RequirementItem(
                        f"具备 {kw} 相关{'能力' if must else '经验优先'}",
                        TYPE.get(kw, "hard_skill"),
                        "high"
                        if must and kw in ["Java", "Python", "Spring Boot", "MySQL", "接口开发"]
                        else "medium",
                        [kw],
                    )
                )
        if must and not out:
            out = [
                RequirementItem("具备岗位相关项目经验", "project_experience", "high", ["项目经验"]),
                RequirementItem("能够理解岗位职责并独立完成任务", "responsibility", "medium", ["岗位职责"]),
            ]
        return out[:12]

    def hidden(self, text, keys):
        h = []
        if any(k in keys for k in ["接口开发", "Spring Boot", "Java", "Python"]):
            h.append("需要具备接口设计、分层开发和问题排查能力")
        if any(k in keys for k in ["MySQL", "Redis", "数据库设计", "缓存"]):
            h.append("需要具备数据建模、查询优化和缓存设计意识")
        if any(k in text for k in ["沟通", "协作", "跨部门", "团队"]):
            h.append("需要具备跨角色沟通和团队协作能力")
        if not h:
            h.append("需要能将岗位要求转化为可交付任务并清晰复盘工作成果")
        return unique(h)
