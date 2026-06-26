from schemas.models import EvidenceMatch
from services.skill_normalizer import SkillNormalizer
from services.utils import unique

class EvidenceMatcher:
    """对齐方案5.5匹配流程：技能标准化→关键词匹配→同义技能映射→证据强度判断→匹配等级判定→风险等级判定"""

    def __init__(self):
        self.norm = SkillNormalizer()

    def match(self, job, resume):
        out = []
        for req in job.must_have_requirements + job.nice_to_have_requirements:
            ev = self.find(req, resume)
            level = self.level(ev, resume)
            risk = self.risk(req, level)
            out.append(EvidenceMatch(
                req.requirement, req.type, req.priority,
                ev, level, risk,
                self.reason(req, level),
                self.suggest(req, level)
            ))
        return out

    def find(self, req, resume):
        """从简历中寻找匹配证据，整合技能标准化和同义映射"""
        ev = []
        keys = req.keywords or [req.requirement]
        skills = resume.skills.get('all', [])
        # 标准化技能列表以便同义匹配
        norm_skills = {self.norm.key(s): s for s in skills}

        for kw in keys:
            kw_norm = self.norm.key(kw)
            # 1. 关键词匹配：精确匹配技能栏
            for s in skills:
                if kw.lower() == s.lower() or kw.lower() in s.lower() or s.lower() in kw.lower():
                    ev.append(f'技能栏出现：{s}')
            # 2. 同义技能映射：技能 normalized 后匹配
            if kw_norm in norm_skills:
                matched = norm_skills[kw_norm]
                if f'技能栏出现：{matched}' not in ev:
                    ev.append(f'技能栏出现：{matched}')
            # 3. 检查同义词链：keyword 的标准化 key 是否在标准化技能中
            for nk, ns in norm_skills.items():
                if kw_norm == nk or kw_norm in nk or nk in kw_norm:
                    if f'技能栏出现：{ns}' not in ev:
                        ev.append(f'技能栏出现：{ns}')

        # 4. 项目经验匹配
        for p in resume.project_experience:
            txt = ' '.join([p.project_name, ' '.join(p.tech_stack),
                           ' '.join(p.tasks), ' '.join(p.results), p.raw_text])
            for kw in keys:
                # 标准化项目文本和关键词后再匹配
                if kw.lower() in txt.lower() or kw in txt:
                    ev.append(f"项目《{p.project_name or '未命名项目'}》体现：{self.short(txt)}")
                    break
                # 同义映射：将关键词标准化后在项目文本中查找
                kw_norm = self.norm.key(kw)
                if kw_norm and kw_norm in txt.lower().replace(' ', '').replace('-', '').replace('_', ''):
                    ev.append(f"项目《{p.project_name or '未命名项目'}》体现（同义映射）：{self.short(txt)}")
                    break

        if not ev:
            ev += self.weak(req, resume)
        return unique(ev)[:5]

    def weak(self, req, resume):
        """相近但不精确的匹配（方案中weak匹配来源）"""
        raw = resume.raw_text
        mapping = {
            '接口开发': ['后端', '接口', 'API', '服务端'],
            '数据库设计': ['MySQL', 'SQL', '表', '数据库'],
            '缓存': ['Redis', '缓存', 'Cache'],
            '高并发': ['性能', '优化', '并发', 'QPS', '高可用'],
            '沟通协作': ['团队', '协作', '联调', '跨部门'],
            '项目经验': ['项目', '系统', '平台'],
            '性能优化': ['优化', '性能', '响应', '延迟', '吞吐'],
            '系统设计': ['架构', '设计', '模块', '分层'],
        }
        for kw in req.keywords + [req.requirement]:
            for k, aliases in mapping.items():
                if k in kw or kw in k:
                    for a in aliases:
                        if a.lower() in raw.lower() or a in raw:
                            return [f'存在相关但不充分的经历描述：出现"{a}"']
        return []

    def level(self, ev, resume):
        """匹配等级判定（方案5.5匹配等级表）"""
        if not ev:
            return 'none'
        has_proj = any('项目' in e or '工作' in e for e in ev)
        has_skill = any('技能栏' in e for e in ev)
        has_result = any(k in resume.raw_text for k in
                         ['提升', '降低', '优化', '%', '效率', '性能', '稳定性'])
        if has_proj and (has_skill or has_result):
            return 'strong'
        if has_proj or has_skill:
            return 'medium'
        return 'weak'

    def risk(self, req, level):
        """风险等级判定（方案5.5：green/yellow/red）"""
        return 'green' if level == 'strong' else (
            'yellow' if level in ['medium', 'weak'] or req.priority != 'high' else 'red'
        )

    def reason(self, req, level):
        return {
            'strong': f'简历中存在与"{req.requirement}"直接相关的技能或项目证据。',
            'medium': f'简历中出现与"{req.requirement}"相关的信息，但项目细节或成果仍不够充分。',
            'weak': f'简历中存在与"{req.requirement}"相近的经历，但缺少直接证明。',
            'none': f'简历中未发现能够支撑"{req.requirement}"的明确证据。'
        }[level]

    def suggest(self, req, level):
        t = req.requirement.replace('具备 ', '').replace(' 相关能力', '').replace(' 相关经验优先', '')
        if level == 'strong':
            return f'建议继续强化"{t}"在项目中的职责、技术难点和结果指标。'
        if level == 'medium':
            return f'建议补充"{t}"对应的项目场景、个人负责部分、技术方案和业务结果。'
        if level == 'weak':
            return f'建议将相近经历改写为与"{t}"更直接相关的证据。'
        return f'建议通过学习、项目实践或简历补充，建立"{t}"相关证据。'

    def short(self, txt, n=120):
        txt = ' '.join(txt.split())
        return txt[:n] + ('...' if len(txt) > n else '')
