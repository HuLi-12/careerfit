from services.resume_optimizer import ResumeOptimizer
from services.interview_generator import InterviewGenerator
from services.safety_checker import SafetyChecker
class ReportGenerator:
    def __init__(self): self.opt=ResumeOptimizer(); self.iv=InterviewGenerator(); self.safe=SafetyChecker()
    def candidate(self,resume,job,matches,score):
        strengths=[m for m in matches if m.match_level=='strong']; risks=[m for m in matches if m.risk_level in ['red','yellow']]
        lines=['# 简历-JD匹配诊断报告','','## 1. 综合结论','',f'综合匹配度：**{score.overall_score}/100**  ',f'推荐结论：**{score.recommendation}**  ','',score.summary,'','---','','## 2. 岗位核心要求拆解','','| 要求 | 类型 | 优先级 |','|---|---|---|']
        for r in job.must_have_requirements+job.nice_to_have_requirements: lines.append(f'| {r.requirement} | {r.type} | {r.priority} |')
        lines += ['','---','','## 3. 证据链匹配表','','| JD要求 | 简历证据 | 匹配等级 | 风险等级 | 建议 |','|---|---|---|---|---|']
        for m in matches:
            ev='<br>'.join(m.resume_evidence) if m.resume_evidence else '未发现明确证据'; lines.append(f'| {m.requirement} | {ev} | {m.match_level} | {m.risk_level} | {m.suggestion} |')
        lines += ['','---','','## 4. 分项评分','','| 维度 | 得分 |','|---|---:|']
        names={'core_skill_match':'核心技能匹配','project_experience_match':'项目经验匹配','responsibility_match':'岗位职责匹配','resume_expression_quality':'简历表达质量','risk_control':'风险控制'}
        for k,v in score.score_breakdown.items(): lines.append(f'| {names.get(k,k)} | {v} |')
        lines += ['','','## 5. 主要优势',''] + ([f'{i+1}. {m.requirement}：{m.reason}' for i,m in enumerate(strengths[:5])] or ['当前简历中暂未形成强证据项，建议优先补充项目职责、技术方案和结果指标。'])
        lines += ['','','## 6. 主要风险',''] + ([f'{i+1}. 【{m.risk_level}】{m.requirement}：{m.reason}' for i,m in enumerate(risks[:6])] or ['未发现明显红色风险，但仍建议强化项目结果和职责边界。'])
        lines += ['','---','','## 7. 简历优化建议','']
        for i,item in enumerate(self.opt.optimize(resume,matches),1):
            lines += [f'### 建议 {i}：{item["target"]}','','【原始内容】',item['original'],'','【存在问题】',item['problem'],'','【优化版本】',item['optimized_text'],'','【优化理由】',item['reason'],'']
        lines += ['---','','## 8. 面试预测问题',''] + [f'{i+1}. {q}' for i,q in enumerate(self.iv.generate(job,resume,matches))]
        lines += ['','---','','## 9. 技能补差路线','']
        for i,m in enumerate(risks[:5],1):
            lines.append(f'### 阶段{i}：补齐"{m.requirement}"')
            lines.append(f'第1步：学习基础概念和核心知识点')
            lines.append(f'第2步：完成一个小型项目案例，应用所学知识')
            lines.append(f'第3步：将项目证据补充到简历中，准备面试回答')
            lines.append('')
        if not risks:
            lines.append('1. 将现有强匹配项目补充技术难点、结果指标和面试复盘答案。')
            lines.append('2. 深入学习岗位涉及的核心技术，关注源码和底层原理。')
            lines.append('3. 准备项目深挖问题的 STAR 结构回答。')
        lines += ['','---','','## 10. 安全合规说明','',self.safe.disclaimer()]
        return '\n'.join(lines)
    def recruiter(self,resume,job,matches,score):
        strengths=[m for m in matches if m.match_level=='strong']; risks=[m for m in matches if m.risk_level in ['red','yellow']]
        lines=['# 候选人岗位匹配评估报告','','## 1. 初筛结论','',f'建议：**{score.recommendation}**  ',f'匹配度：**{score.overall_score}/100**','',score.summary,'','---','','## 2. 候选人优势','']
        lines += [f'{i+1}. {m.requirement}：{m.reason}' for i,m in enumerate(strengths[:5])] or ['暂未发现强匹配证据，建议要求候选人补充项目说明。']
        lines += ['','','## 3. 候选人风险','','| 风险 | 等级 | 说明 |','|---|---|---|']
        if risks:
            for m in risks[:8]: lines.append(f'| {m.requirement} | {m.risk_level} | {m.reason} |')
        else: lines.append('| 暂无明显风险 | green | 仍需面试验证项目真实性和表达能力 |')
        lines += ['','','## 4. 建议面试追问',''] + [f'{i+1}. {q}' for i,q in enumerate(self.iv.generate(job,resume,matches)[:10])]
        lines += ['','','## 5. 面试评分表','','| 维度 | 建议考察点 | 分值 |','|---|---|---:|','| 核心技能 | 语言、框架、数据库和工具能力 | 30 |','| 项目能力 | 项目职责、技术难点、个人贡献和结果指标 | 30 |','| 问题解决 | 调试、优化、线上问题定位和复盘能力 | 20 |','| 沟通表达 | 是否能清晰讲述复杂问题和协作过程 | 10 |','| 岗位动机 | 对岗位内容、业务场景和发展方向的理解 | 10 |','','---','','## 6. 安全合规说明','',self.safe.disclaimer()]
        return '\n'.join(lines)
    def resume_only(self,resume):
        skills=resume.skills.get('all',[]); lines=['# 职业方向与简历优化初步报告','','## 1. 当前能力画像','',f'- 技能关键词：{", ".join(skills) if skills else "未检测到明确技能关键词"}',f'- 项目数量：{len(resume.project_experience)}',f'- 自我评价：{resume.self_evaluation[:200] if resume.self_evaluation else "未检测到自我评价"}','','## 2. 推荐岗位方向','']
        if any(s in skills for s in ['Java','Spring Boot','MySQL']): lines.append('1. Java后端开发：简历中已有 Java/Spring Boot/MySQL 相关基础，适合投递后端开发岗位。')
        if any(s in skills for s in ['Python','PyTorch','TensorFlow','机器学习','深度学习']): lines.append('2. 算法/AI应用开发：简历中存在 Python 或 AI 相关能力，可考虑数据方向。')
        if any(s in skills for s in ['Vue','React','JavaScript','TypeScript']): lines.append('3. 前端开发：简历中存在前端框架或 JavaScript 技能，适合投递前端岗位。')
        if len(skills)<3: lines.append('1. 可先补充目标岗位 JD，以便生成更准确的人岗匹配报告。')
        lines += ['','## 3. 简历问题诊断','','1. 项目经历建议使用"背景-职责-技术方案-结果"结构。','2. 技能栏建议按语言、框架、数据库、工具分组。','3. 每个项目至少补充个人负责模块和可验证结果。','4. 增加量化数据，如接口数、用户量、响应时间、并发数。']
        if resume.self_evaluation: lines.append(f'5. 自我评价当前内容偏笼统，建议结合具体技能和项目亮点改写。')
        lines += ['','## 4. 职位方向建议','','建议补充目标岗位 JD，系统可以帮你：','1. 生成人岗匹配度评分','2. 识别能力差距','3. 定向优化简历','4. 预测面试问题','5. 制定学习路线']
        return '\n'.join(lines)
    def jd_only(self,job):
        lines=['# JD优化与候选人画像报告','','## 1. 岗位基础信息','',f'- 岗位名称：{job.position_name}',f'- 岗位级别：{job.seniority_level}',f'- 关键词：{", ".join(job.evaluation_keywords) if job.evaluation_keywords else "未检测到明确关键词"}','','## 2. 岗位核心要求','','| 要求 | 类型 | 优先级 |','|---|---|---|']
        for r in job.must_have_requirements: lines.append(f'| {r.requirement} | {r.type} | {r.priority} |')
        lines += ['','## 3. 加分项','','| 要求 | 类型 | 优先级 |','|---|---|---|']
        for r in job.nice_to_have_requirements: lines.append(f'| {r.requirement} | {r.type} | {r.priority} |')
        lines += ['','## 4. 隐含要求','']+[f'- {r}' for r in job.hidden_requirements]+['','## 5. 候选人画像','']+[f'- 候选人需具备：{r.requirement}' for r in job.must_have_requirements[:6]]
        lines += ['','## 6. 面试筛选建议','','1. 先验证候选人是否有与核心技能相关的真实项目证据。','2. 针对 JD 中的高优先级要求设计项目深挖题。','3. 对加分项只作为排序依据，不建议作为硬性淘汰条件。','4. 避免使用年龄、性别、婚育等敏感信息进行筛选。','5. 建议要求候选人提供项目成果或作品集。']
        return '\n'.join(lines)
