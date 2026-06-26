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
        if risks:
            lines.append('### 当前技能差距')
            for i,m in enumerate(risks[:5],1):
                t=m.requirement.replace('具备 ','').replace(' 相关能力','').replace(' 相关经验优先','')
                lines.append(f'{i}. {t}：{m.reason}')
            lines.append('')
            lines.append('### 7天补强路线')
            steps={
                'general':['第1天：学习相关基础概念、核心知识点和使用场景。','第2天：完成一个小型项目案例，将所学知识应用到实践中。','第3天：深入研究常见难点和面试高频问题。','第4天：整理项目中的相关实践点和优化经验。','第5天：将项目经历改写为 STAR 结构，突出个人职责和结果。','第6天：准备项目深挖问题的完整答案。','第7天：整体复盘，将学习成果补充到简历中。'],
                'Redis':['第1天：学习 Redis 基础数据结构和缓存使用场景。','第2天：完成 Spring Boot 集成 Redis 的小案例。','第3天：学习缓存穿透、缓存击穿、缓存雪崩。','第4天：补充一个登录验证码或热点数据缓存案例。','第5天：整理项目中的数据库查询优化点。','第6天：将项目经历改写为 STAR 结构。','第7天：根据目标 JD 准备 10 个项目深挖问题答案。'],
                'MySQL':['第1天：学习 MySQL 索引类型、SQL 执行流程和优化器原理。','第2天：学习事务隔离级别、锁机制和 MVCC。','第3天：练习慢查询分析和 explain 执行计划解读。','第4天：整理项目中的数据库设计和 SQL 优化案例。','第5天：学习分库分表、读写分离等架构方案。','第6天：将数据库相关经验补充到简历中。','第7天：准备数据库面试题和技术深挖答案。'],
                '高并发':['第1天：学习并发编程基础和线程模型。','第2天：学习缓存、消息队列等常见高并发方案。','第3天：学习性能测试和调优方法论。','第4天：完成一个高并发场景的小型模拟项目。','第5天：将并发相关经验整理到简历中。','第6天：准备高并发场景面试题。','第7天：整体复盘，串联完整技术方案。'],
                '接口开发':['第1天：学习 RESTful API 设计规范。','第2天：学习接口文档编写和前后端联调流程。','第3天：学习接口安全、鉴权、限流方案。','第4天：整理项目中的接口设计经验。','第5天：将接口职责和技术方案补充到简历。','第6天：准备接口设计相关面试问题。','第7天：总结接口优化的经验和案例。'],
            }
            used_steps = set()
            for m in risks[:3]:
                for keyword, plan_steps in steps.items():
                    if keyword != 'general' and keyword.lower() in m.requirement.lower() or any(k in m.requirement for k in [keyword]):
                        if keyword not in used_steps:
                            used_steps.add(keyword)
                            lines.append('')
                            for s in plan_steps:
                                lines.append(s)
                            break
                    elif keyword == 'general' and len(used_steps) == 0:
                        pass
            if not used_steps:
                lines.append('')
                for s in steps['general']:
                    lines.append(s)
        else:
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
