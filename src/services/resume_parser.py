import re
from schemas.models import ResumeProfile, ProjectExperienceItem
from services.skill_normalizer import SkillNormalizer
from services.utils import normalize_text, split_lines, unique

PROGRAMMING = [
    "Java",
    "Python",
    "C++",
    "C#",
    "Go",
    "Golang",
    "JavaScript",
    "TypeScript",
    "SQL",
    "HTML",
    "CSS",
]
FRAMEWORKS = [
    "Spring Boot",
    "Spring",
    "MyBatis",
    "Django",
    "Flask",
    "Vue",
    "React",
    "Node.js",
    "PyTorch",
    "TensorFlow",
    "FastAPI",
]
DATABASES = [
    "MySQL",
    "Redis",
    "PostgreSQL",
    "MongoDB",
    "Oracle",
    "SQLite",
    "Elasticsearch",
]
TOOLS = [
    "Git",
    "Docker",
    "Linux",
    "Nginx",
    "Maven",
    "Gradle",
    "Kubernetes",
    "Jenkins",
    "Figma",
    "Axure",
]
DOMAIN = ["电商", "金融", "教育", "医疗", "招聘", "人力资源", "AI", "机器学习", "深度学习", "数据分析", "智慧城市"]
SOFT = ["沟通", "协作", "团队", "抗压", "学习能力", "责任心", "执行力", "问题排查"]
EDU_KEYWORDS = ["大学", "学院", "本科", "硕士", "博士", "专科", "MBA"]
WORK_KEYWORDS = ["公司", "实习", "工程师", "产品", "运营", "经理", "主管", "专员"]


class ResumeParser:
    SECTION_HEADS = [
        "教育经历",
        "工作经历",
        "实习经历",
        "项目经历",
        "项目经验",
        "技能",
        "专业技能",
        "证书",
        "奖项",
        "自我评价",
        "个人总结",
    ]

    def __init__(self):
        self.norm = SkillNormalizer()

    def parse(self, text):
        text = normalize_text(text)
        p = ResumeProfile(raw_text=text)
        if not text:
            return p
        p.basic_info = self.basic(text)
        p.project_experience = self.projects(text)
        p.skills = self.skills(text)
        p.education = self.education(text)
        p.work_experience = self.work(text)
        p.self_evaluation = self.self_eval(text)
        p.certificates = self.certs(text)
        p.awards = self.awards(text)
        return p

    def basic(self, text):
        info = {"name": "", "target_position": "", "location": "", "contact": ""}
        pats = {
            "name": [r"姓名[:：]\s*([^\n，, ]+)"],
            "target_position": [r"目标岗位[:：]\s*([^\n]+)", r"求职意向[:：]\s*([^\n]+)"],
            "location": [r"(?:所在|现居|所在地|城市)[:：]\s*([^\n，, ]+)"],
            "contact": [
                r"邮箱[:：]\s*([A-Za-z0-9_.+-]+@[A-Za-z0-9_.-]+)",
                r"电话[:：]\s*([0-9\-+ ]+)",
                r"mail[:：]\s*([A-Za-z0-9_.+-]+@[A-Za-z0-9_.-]+)",
            ],
        }
        for k, ps in pats.items():
            for pat in ps:
                m = re.search(pat, text, re.I)
                if m:
                    info[k] = m.group(1).strip()
                    break
        return info

    def section(self, text, names):
        lines = text.splitlines()
        start = None
        for i, l in enumerate(lines):
            if any(n in l for n in names):
                start = i + 1
                break
        if start is None:
            return ""
        end = len(lines)
        for j in range(start, len(lines)):
            if any(h in lines[j] for h in self.SECTION_HEADS):
                end = j
                break
        return "\n".join(lines[start:end])

    def education(self, text):
        sec = self.section(text, ["教育经历", "教育背景"])
        if not sec:
            return []
        lines = split_lines(sec)
        out = []
        for line in lines:
            if not any(k in line for k in EDU_KEYWORDS):
                continue
            item = {
                "school": self.extract_school(line),
                "major": self.extract_major(line),
                "degree": self.extract_degree(line),
                "time": self.extract_time(line),
                "highlights": [
                    x for x in lines if x != line and any(k in x for k in ["GPA", "绩点", "排名", "荣誉"])
                ][:5],
            }
            out.append(item)
        return out[:3]

    def extract_school(self, text):
        m = re.search(r"([一-鿿A-Za-z0-9]+(?:大学|学院|学校))", text)
        return m.group(1) if m else ""

    def extract_major(self, text):
        m = re.search(r"(?:专业|主修)[:：]\s*([^\s，,；;]+)", text)
        if not m:
            m = re.search(r"(?:计算机|软件|电子|通信|数学|物理|化学|金融|经济|管理|文学|外语|法学|医学|艺术|教育)[一-龥]*", text)
        return m.group(0) if m else ""

    def extract_degree(self, text):
        degs = {
            "博士": "博士",
            "硕士": "硕士",
            "研究生": "硕士",
            "本科": "本科",
            "学士": "本科",
            "专科": "专科",
            "MBA": "MBA",
        }
        for k, v in degs.items():
            if k in text:
                return v
        return ""

    def extract_time(self, text):
        for pat in [
            r"(\d{4}\s*[年/.-]\s*\d{0,2})\s*(?:[至\-~—到]\s*\d{4}\s*[年/.-]\s*\d{0,2})?",
            r"(\d{4})\s*(?:[至\-~—到]\s*\d{4})?",
        ]:
            m = re.search(pat, text)
            if m:
                return m.group(0).strip()
        return ""

    def work(self, text):
        sec = self.section(text, ["工作经历", "实习经历"])
        if not sec:
            return []
        lines = split_lines(sec)
        out = []
        for line in lines:
            if not any(k in line for k in WORK_KEYWORDS):
                continue
            item = {
                "company": self.extract_company(line),
                "position": self.extract_position(line),
                "time": self.extract_time(line),
                "responsibilities": [
                    x
                    for x in lines
                    if x != line and any(k in x for k in ["负责", "参与", "实现", "开发", "设计", "完成"])
                ][:8],
                "achievements": [
                    x
                    for x in lines
                    if x != line
                    and any(k in x for k in ["提升", "降低", "优化", "%", "效率", "稳定", "性能", "获得", "奖项"])
                ][:5],
            }
            out.append(item)
        return out[:5]

    def extract_company(self, text):
        m = re.search(r"([一-龥A-Za-z0-9]+(?:公司|集团|科技|有限|股份|工作室))", text)
        return m.group(1) if m else text.split()[0][:20] if text.split() else ""

    def extract_position(self, text):
        m = re.search(r"([一-龥]+(?:工程师|开发|经理|主管|专员|助理|实习生|产品|运营|设计|架构师))", text)
        return m.group(1) if m else ""

    def self_eval(self, text):
        sec = self.section(text, ["自我评价", "个人总结", "个人评价"])
        return sec[:500] if sec else ""

    def projects(self, text):
        sec = self.section(text, ["项目经历", "项目经验", "项目"])
        if not sec and any(k in text for k in ["项目", "系统", "平台", "小程序"]):
            sec = text
        lines = split_lines(sec)
        chunks = []
        cur = []
        for line in lines:
            is_new = bool(re.match(r"^(\d+[.、]|项目[一二三四五六七八九十\d]*[:：])", line)) or (
                "系统" in line and len(line) < 60
            )
            if is_new and cur:
                chunks.append(cur)
                cur = [line]
            else:
                cur.append(line)
        if cur:
            chunks.append(cur)
        return [self.project(c) for c in chunks[:5]]

    def project(self, lines):
        raw = "\n".join(lines)
        first = lines[0] if lines else ""
        name = re.sub(r"^(\d+[.、]|项目[一二三四五六七八九十\d]*[:：])", "", first).strip()[:40]
        sk = self.extract_skills(raw)
        tasks = [
            x for x in lines if any(k in x for k in ["负责", "参与", "实现", "开发", "设计", "完成", "联调"])
        ][:8]
        res = [x for x in lines if any(k in x for k in ["提升", "降低", "优化", "%", "效率", "稳定", "性能"])][
            :5
        ]
        return ProjectExperienceItem(
            project_name=name, tech_stack=sk, tasks=tasks, results=res, raw_text=raw
        )

    def extract_skills(self, text):
        found = []
        low = text.lower()
        for s in PROGRAMMING + FRAMEWORKS + DATABASES + TOOLS + DOMAIN + SOFT:
            if s.lower() in low or s in text:
                found.append(s)
        return self.norm.many(found)

    def skills(self, text):
        all_sk = self.extract_skills(text)
        return {
            "programming": self.norm.many([s for s in all_sk if s in PROGRAMMING]),
            "frameworks": self.norm.many([s for s in all_sk if s in FRAMEWORKS]),
            "tools": self.norm.many([s for s in all_sk if s in TOOLS]),
            "database": self.norm.many([s for s in all_sk if s in DATABASES]),
            "domain_knowledge": self.norm.many([s for s in all_sk if s in DOMAIN]),
            "soft_skills": self.norm.many([s for s in all_sk if s in SOFT]),
            "all": all_sk,
        }

    def certs(self, text):
        lines = split_lines(text)
        sec = self.section(text, ["证书", "资格证书"])
        if sec:
            lines = split_lines(sec)
        return unique(
            [x for x in lines if any(k in x for k in ["证书", "认证", "CET", "软考", "等级"])][:10]
        )

    def awards(self, text):
        lines = split_lines(text)
        sec = self.section(text, ["奖项", "荣誉"])
        if sec:
            lines = split_lines(sec)
        return unique([x for x in lines if any(k in x for k in ["奖", "竞赛", "比赛", "优秀", "荣誉"])][:10])
