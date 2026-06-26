from config import MATCH_SCORE, SCORE_WEIGHTS, RECOMMENDATION_LEVELS
from schemas.models import ScoreResult
class ScoreEngine:
    def calculate(self,matches,resume_text=''):
        if not matches:
            return ScoreResult(0,'信息不足，无法计算匹配度',{'core_skill_match':0,'project_experience_match':0,'responsibility_match':0,'resume_expression_quality':0,'risk_control':0},'unknown','当前缺少可评分的岗位要求或简历证据。')
        bd={'core_skill_match':self.dim(matches,['hard_skill','framework','database','tool'],30),'project_experience_match':self.dim(matches,['project_experience'],25),'responsibility_match':self.dim(matches,['responsibility','soft_skill'],20),'resume_expression_quality':self.expr(resume_text,15),'risk_control':self.risk(matches,10)}
        total=max(0,min(100,round(sum(bd.values())))); return ScoreResult(total,self.rec(total),bd,self.lv(total),self.summary(total,matches))
    def dim(self,ms,types,w):
        t=[m for m in ms if m.requirement_type in types]
        if not t: return round(w*0.6)
        vals=[min(1.0, MATCH_SCORE.get(m.match_level,0)*(1.1 if m.priority=='high' else 1.0)) for m in t]
        return round(sum(vals)/len(vals)*w)
    def expr(self,text,w):
        if not text: return 0
        s=.45
        if any(k in text for k in ['负责','参与','实现','设计','完成']): s+=.2
        if any(k in text for k in ['提升','降低','优化','效率','性能','%','稳定']): s+=.2
        if any(k in text for k in ['项目','系统','平台','模块']): s+=.1
        if len(text)>300: s+=.05
        return round(min(1,s)*w)
    def risk(self,ms,w):
        red=sum(1 for m in ms if m.risk_level=='red'); yellow=sum(1 for m in ms if m.risk_level=='yellow')
        return round(max(0,1-(red+yellow*.45)/max(1,len(ms)))*w)
    def rec(self,total):
        for th,txt in RECOMMENDATION_LEVELS:
            if total>=th: return txt
    def lv(self,total): return 'high' if total>=85 else 'medium_high' if total>=70 else 'medium_low' if total>=55 else 'low'
    def summary(self,total,ms):
        strong=sum(1 for m in ms if m.match_level=='strong'); red=sum(1 for m in ms if m.risk_level=='red')
        if total>=85: return f'候选人与岗位高度匹配，共有 {strong} 项要求具备较强证据。'
        if total>=70: return f'候选人与岗位具备较好匹配度，但仍有 {red} 项明显风险。'
        if total>=55: return '候选人与岗位存在一定相关性，但证据链不够充分，需要补强核心短板。'
        return '候选人与岗位匹配度较低，当前简历中缺少多项核心要求证据。'
