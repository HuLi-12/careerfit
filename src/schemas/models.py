from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List


@dataclass
class ProjectExperienceItem:
    project_name: str = ""
    role: str = ""
    tech_stack: List[str] = field(default_factory=list)
    tasks: List[str] = field(default_factory=list)
    results: List[str] = field(default_factory=list)
    raw_text: str = ""


@dataclass
class ResumeProfile:
    basic_info: Dict[str, str] = field(
        default_factory=lambda: {
            "name": "",
            "target_position": "",
            "location": "",
            "contact": "",
        }
    )
    education: List[Dict[str, Any]] = field(default_factory=list)
    work_experience: List[Dict[str, Any]] = field(default_factory=list)
    project_experience: List[ProjectExperienceItem] = field(default_factory=list)
    skills: Dict[str, List[str]] = field(
        default_factory=lambda: {
            "programming": [],
            "frameworks": [],
            "tools": [],
            "database": [],
            "domain_knowledge": [],
            "soft_skills": [],
            "all": [],
        }
    )
    certificates: List[str] = field(default_factory=list)
    awards: List[str] = field(default_factory=list)
    self_evaluation: str = ""
    raw_text: str = ""

    def to_dict(self):
        return asdict(self)


@dataclass
class RequirementItem:
    requirement: str
    type: str = "hard_skill"
    priority: str = "medium"
    keywords: List[str] = field(default_factory=list)


@dataclass
class JobProfile:
    position_name: str = ""
    seniority_level: str = "unknown"
    must_have_requirements: List[RequirementItem] = field(default_factory=list)
    nice_to_have_requirements: List[RequirementItem] = field(default_factory=list)
    responsibilities: List[str] = field(default_factory=list)
    hidden_requirements: List[str] = field(default_factory=list)
    evaluation_keywords: List[str] = field(default_factory=list)
    raw_text: str = ""

    def to_dict(self):
        return asdict(self)


@dataclass
class EvidenceBlock:
    """结构化证据块 — 证据等级 A/B/C/D/E"""

    source_type: str = ""  # skill_section / project_experience / work_experience / weak_semantic
    source_name: str = ""  # 来源名称（如项目名、技能栏标签）
    source_detail: str = ""  # 具体证据文本
    matched_keywords: List[str] = field(default_factory=list)  # 命中的关键词
    relevance: float = 0.0  # 0.0–1.0
    confidence: float = 0.0  # 0.0–1.0
    evidence_level: str = "E"  # A / B / C / D / E

    def to_dict(self):
        return asdict(self)


@dataclass
class EvidenceMatch:
    requirement: str
    requirement_type: str
    priority: str
    resume_evidence: List[str] = field(default_factory=list)
    evidence_blocks: List[EvidenceBlock] = field(default_factory=list)
    confidence: float = 0.0
    match_level: str = "none"
    risk_level: str = "red"
    reason: str = ""
    suggestion: str = ""

    def to_dict(self):
        return asdict(self)


@dataclass
class ScoreResult:
    overall_score: int
    recommendation: str
    score_breakdown: Dict[str, int]
    level: str
    summary: str
    must_have_score: float = 0.0
    nice_to_have_bonus: float = 0.0
    risk_penalty: float = 0.0
    confidence: float = 0.0
    information_completeness: float = 0.0

    def to_dict(self):
        return asdict(self)


@dataclass
class AnalysisResult:
    input_type: Dict[str, Any]
    resume_profile: Dict[str, Any]
    job_profile: Dict[str, Any]
    evidence_matches: List[Dict[str, Any]]
    score: Dict[str, Any]
    report_markdown: str

    def to_dict(self):
        return asdict(self)
