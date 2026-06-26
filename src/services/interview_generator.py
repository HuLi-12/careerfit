class InterviewGenerator:
    def generate(self,job,resume,matches):
        qs=[]
        # 技术基础题
        for r in job.must_have_requirements[:5]:
            t=r.requirement.replace('具备 ','').replace(' 相关能力','').replace(' 相关经验优先','')
            qs.append(f'请结合项目说明你对"{t}"的实际使用经验。')
        # 项目深挖题
        for p in resume.project_experience[:2]:
            n=p.project_name or '你的项目'
            tc=', '.join(p.tech_stack[:3]) if p.tech_stack else '相关技术'
            qs += [f'你在《{n}》中具体负责哪些模块？', f'《{n}》中使用了{tc}，请说明技术选型和方案设计思路。', f'《{n}》中最复杂的技术问题是什么？你是如何解决的？']
        # 风险追问题
        for m in matches:
            if m.risk_level=='red': qs.append(f'简历中没有看到"{m.requirement}"的直接证据，如果岗位需要，你会如何补齐或应对？')
            elif m.risk_level=='yellow': qs.append(f'你与"{m.requirement}"相关的经历证据不够充分，能否具体说明个人贡献？')
        # HR问题
        qs += ['你为什么选择投递这个岗位？','你如何看待自己的职业发展方向？','如果入职后发现业务复杂度高于预期，你会如何快速熟悉系统？','你期望的工作环境和团队协作方式是怎样的？']
        # 反问建议
        qs += ['你可以反问面试官：这个岗位的团队目前面临的最大技术挑战是什么？','你可以反问面试官：团队的技术栈和开发流程是怎样的？','你可以反问面试官：入职后前三个月的重点目标是什么？']
        seen=set(); out=[]
        for q in qs:
            if q not in seen: seen.add(q); out.append(q)
        return out[:15]
