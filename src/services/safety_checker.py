SENSITIVE_KEYWORDS=['性别','年龄','民族','婚育','已婚','未婚','宗教','政治面貌','外貌','身高','体重','健康状况','家庭背景','地域歧视']
class SafetyChecker:
    def scan(self,text):
        found=[k for k in SENSITIVE_KEYWORDS if k in text]
        return {'contains_sensitive_terms':bool(found),'sensitive_terms':found,'policy':'敏感信息不参与匹配评分，仅基于岗位相关能力、经历、技能和成果进行分析。'}
    def disclaimer(self): return '本报告仅作为岗位匹配、简历优化和求职准备辅助，不构成最终录用或淘汰决策。招聘方应结合面试表现、作品集、实际业务需求和合规招聘流程综合判断。'
