from schemas.models import EvidenceMatch, EvidenceBlock
from services.skill_normalizer import SkillNormalizer
from services.utils import unique


class EvidenceMatcher:
    """对齐方案5.5匹配流程：技能标准化→关键词匹配→同义技能映射→证据强度判断→匹配等级判定→风险等级判定

    证据等级体系（Evidence Level）：
        A — 强直接证据：技能栏明确出现 + 项目有明确实践且有结果指标
        B — 较强证据：技能栏出现 + 项目有相关描述
        C — 一般证据：技能栏出现但无项目支撑，或项目描述相关但无技能栏
        D — 弱证据：只有相近经历或弱语义映射匹配
        E — 无证据：未发现任何证据
    """

    def __init__(self):
        self.norm = SkillNormalizer()
        self.semantic_rules = self._load_semantic_rules()

    @staticmethod
    def _load_semantic_rules():
        from config import DATA_DIR
        from services.utils import load_json
        return load_json(DATA_DIR / "semantic_match_rules.json", {})

    def match(self, job, resume):
        out = []
        for req in job.must_have_requirements + job.nice_to_have_requirements:
            blocks = self.find_blocks(req, resume)
            level = self.match_level_from_blocks(blocks)
            risk = self.risk(req, level)
            confidence = self.compute_confidence(blocks, level)
            ev_texts = [b.source_detail for b in blocks]
            out.append(
                EvidenceMatch(
                    requirement=req.requirement,
                    requirement_type=req.type,
                    priority=req.priority,
                    resume_evidence=ev_texts,
                    evidence_blocks=blocks,
                    confidence=confidence,
                    match_level=level,
                    risk_level=risk,
                    reason=self.reason(req, level, blocks),
                    suggestion=self.suggest(req, level),
                )
            )
        return out

    def find_blocks(self, req, resume):
        """返回结构化证据块列表，每块自带 evidence_level"""
        blocks = []
        keys = req.keywords or [req.requirement]
        skills = resume.skills.get("all", [])
        norm_skills = {self.norm.key(s): s for s in skills}

        skill_matches = []
        for kw in keys:
            kw_norm = self.norm.key(kw)
            for s in skills:
                if kw.lower() == s.lower() or kw.lower() in s.lower() or s.lower() in kw.lower():
                    skill_matches.append(s)
            if kw_norm in norm_skills:
                skill_matches.append(norm_skills[kw_norm])

        skill_matches = unique(skill_matches)
        has_skill = len(skill_matches) > 0

        # 项目证据
        has_project = False
        has_result = False
        for p in resume.project_experience:
            norm_tech = self.norm.many(p.tech_stack)
            txt = " ".join(
                [
                    p.project_name,
                    " ".join(p.tech_stack),
                    " ".join(norm_tech),  # 归一化后别名（如 k8s→Kubernetes）
                    " ".join(p.tasks),
                    " ".join(p.results),
                    p.raw_text,
                ]
            )
            for kw in keys:
                kw_lower = kw.lower()
                if kw_lower in txt.lower() or kw in txt:
                    has_project = True
                    blocks.append(
                        EvidenceBlock(
                            source_type="project_experience",
                            source_name=p.project_name or "未命名项目",
                            source_detail=f"项目《{p.project_name or '未命名项目'}》：{self.short(txt)}",
                            matched_keywords=[kw],
                            relevance=0.9,
                            confidence=0.85,
                            evidence_level="B",
                        )
                    )
                    # 检查是否有量化结果
                    if any(k in txt for k in ["提升", "降低", "优化", "%", "效率", "性能", "稳定性"]):
                        has_result = True
                    break
                # 同义映射
                kw_norm = self.norm.key(kw)
                if kw_norm and kw_norm in txt.lower().replace(" ", "").replace("-", "").replace(
                    "_", ""
                ):
                    has_project = True
                    blocks.append(
                        EvidenceBlock(
                            source_type="project_experience",
                            source_name=p.project_name or "未命名项目",
                            source_detail=f"项目《{p.project_name or '未命名项目'}》同义匹配：{self.short(txt)}",
                            matched_keywords=[kw],
                            relevance=0.7,
                            confidence=0.7,
                            evidence_level="C",
                        )
                    )
                    break

        # 技能栏证据
        if has_skill:
            blocks.append(
                EvidenceBlock(
                    source_type="skill_section",
                    source_name="技能栏",
                    source_detail=f"技能栏出现：{'、'.join(skill_matches[:5])}",
                    matched_keywords=skill_matches[:3],
                    relevance=0.8,
                    confidence=0.9,
                    evidence_level="C",  # 后续升级
                )
            )

        # 升级证据等级
        for b in blocks:
            if b.source_type == "skill_section" and has_project and has_result:
                b.evidence_level = "A"
                b.relevance = 1.0
                b.confidence = 0.95
            elif b.source_type == "skill_section" and has_project:
                b.evidence_level = "B"
                b.relevance = 0.9
                b.confidence = 0.85
            elif b.source_type == "project_experience" and not has_skill:
                b.evidence_level = "C"
                b.relevance = 0.7
                b.confidence = 0.7
            elif b.evidence_level == "C" and has_project and has_result:
                b.evidence_level = "B"
                b.relevance = 0.9
                b.confidence = 0.85

        if not blocks:
            # 弱语义匹配
            weak_ev = self.weak(req, resume)
            for w in weak_ev:
                blocks.append(
                    EvidenceBlock(
                        source_type="weak_semantic",
                        source_name="弱语义匹配",
                        source_detail=w,
                        matched_keywords=[w.split("出现")[-1].strip('"')] if "出现" in w else [],
                        relevance=0.3,
                        confidence=0.3,
                        evidence_level="D",
                    )
                )

        return blocks[:5]

    def weak(self, req, resume):
        raw = resume.raw_text
        for kw in req.keywords + [req.requirement]:
            for k, rule in self.semantic_rules.items():
                aliases = rule.get("aliases", [])
                if k in kw or kw in k:
                    for a in aliases:
                        if a.lower() in raw.lower() or a in raw:
                            return [f'存在相关但不充分的经历描述：出现"{a}"']
        return []

    def match_level_from_blocks(self, blocks):
        """根据证据块判定 match_level
        A → strong, B/C → medium, D → weak, 无 → none
        """
        if not blocks:
            return "none"
        levels = [b.evidence_level for b in blocks]
        if "A" in levels:
            return "strong"
        if "B" in levels or "C" in levels:
            return "medium"
        if "D" in levels:
            return "weak"
        return "none"

    def risk(self, req, level):
        if level == "strong":
            return "green"
        if level == "medium":
            return "yellow"
        if level == "weak":
            return "red" if req.priority == "high" else "yellow"
        # level == "none"
        return "red" if req.priority in ("high", "medium") else "yellow"

    def compute_confidence(self, blocks, level):
        """综合置信度：基于最高证据块和匹配等级"""
        if not blocks:
            return 0.0
        max_conf = max(b.confidence for b in blocks)
        base = {"strong": 0.85, "medium": 0.65, "weak": 0.4, "none": 0.0}.get(level, 0.0)
        return round((max_conf * 0.6 + base * 0.4), 2)

    def reason(self, req, level, blocks=None):
        if level == "none":
            return f'简历中未发现能够支撑"{req.requirement}"的明确证据。'
        if blocks:
            levels_str = "/".join(sorted(set(b.evidence_level for b in blocks)))
            return f"简历中存在{len(blocks)}条证据（证据等级：{levels_str}），整体判定为{level}匹配。"
        return {
            "strong": f'简历中存在与"{req.requirement}"直接相关的技能或项目证据。',
            "medium": f'简历中出现与"{req.requirement}"相关的信息，但项目细节或成果仍不够充分。',
            "weak": f'简历中存在与"{req.requirement}"相近的经历，但缺少直接证明。',
            "none": f'简历中未发现能够支撑"{req.requirement}"的明确证据。',
        }[level]

    def suggest(self, req, level):
        t = req.requirement.replace("具备 ", "").replace(" 相关能力", "").replace(" 相关经验优先", "")
        if level == "strong":
            return f'建议继续强化"{t}"在项目中的职责、技术难点和结果指标。'
        if level == "medium":
            return f'建议补充"{t}"对应的项目场景、个人负责部分、技术方案和业务结果。'
        if level == "weak":
            return f'建议将相近经历改写为与"{t}"更直接相关的证据。'
        return f'建议通过学习、项目实践或简历补充，建立"{t}"相关证据。'

    def short(self, txt, n=120):
        txt = " ".join(txt.split())
        return txt[:n] + ("..." if len(txt) > n else "")
