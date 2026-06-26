from config import MATCH_SCORE, RECOMMENDATION_LEVELS
from schemas.models import ScoreResult


class ScoreEngine:
    """评分引擎 — 基于证据链的加权评分，无默认补分逻辑

    评分公式：
        must_have_base = Σ(证据分 × 优先级系数) / 要求数 × 100
        nice_to_have_bonus = Σ(证据分 × 优先级系数) / 要求数 × 10 (封顶)
        risk_penalty = red_count × 8 + yellow_count × 3
        overall = must_have_base + nice_to_have_bonus - risk_penalty

    优先级系数：high=1.0, medium=0.8, low=0.6
    """

    def calculate(self, matches, resume_text=""):
        if not matches:
            return ScoreResult(
                overall_score=0,
                recommendation="信息不足，无法计算匹配度",
                score_breakdown={
                    "core_skill_match": 0,
                    "project_experience_match": 0,
                    "responsibility_match": 0,
                    "resume_expression_quality": 0,
                    "risk_control": 0,
                },
                level="unknown",
                summary="当前缺少可评分的岗位要求或简历证据。",
            )

        must_have = [m for m in matches if m.priority == "high"]
        nice_have = [m for m in matches if m.priority != "high"]

        # 1. must-have 基础分
        must_have_score = self._dimension_score(must_have, weight=100)

        # 2. nice-to-have 加分（最多 +10）
        nice_to_have_bonus = min(self._dimension_score(nice_have, weight=10), 10.0)

        # 3. 风险扣分
        risk_penalty = self._risk_penalty(matches)

        # 4. 总分
        raw_total = must_have_score + nice_to_have_bonus - risk_penalty
        overall = max(0, min(100, round(raw_total)))

        # 5. 分项评分
        bd = {
            "core_skill_match": self.dim_by_type(
                matches, ["hard_skill", "framework", "database", "tool"], 30
            ),
            "project_experience_match": self.dim_by_type(matches, ["project_experience"], 25),
            "responsibility_match": self.dim_by_type(matches, ["responsibility", "soft_skill"], 20),
            "resume_expression_quality": self.expr(resume_text, 15),
            "risk_control": self.risk_dim(matches, 10),
        }

        # 6. 置信度 & 信息完整度
        confidence = self._compute_confidence(matches, resume_text)
        info_completeness = self._compute_info_completeness(matches)

        return ScoreResult(
            overall_score=overall,
            recommendation=self.rec(overall),
            score_breakdown=bd,
            level=self.lv(overall),
            summary=self.summary(overall, must_have_score, risk_penalty, matches),
            must_have_score=round(must_have_score, 1),
            nice_to_have_bonus=round(nice_to_have_bonus, 1),
            risk_penalty=round(risk_penalty, 1),
            confidence=round(confidence, 2),
            information_completeness=round(info_completeness, 2),
        )

    def _dimension_score(self, items, weight):
        """计算一组要求的加权得分 — 无默认补分"""
        if not items:
            return 0.0
        priority_weight = {"high": 1.0, "medium": 0.8, "low": 0.6}
        scores = []
        for m in items:
            ev_score = MATCH_SCORE.get(m.match_level, 0.0)
            pri = priority_weight.get(m.priority, 0.8)
            conf = getattr(m, "confidence", 0.5) if hasattr(m, "confidence") else 0.5
            scores.append(ev_score * pri * (0.8 + 0.2 * conf))
        avg = sum(scores) / len(scores)
        return round(avg * weight, 1)

    def _risk_penalty(self, matches):
        """风险扣分：red 每项 -8，yellow 每项 -3，上限 20"""
        red = sum(1 for m in matches if m.risk_level == "red")
        yellow = sum(1 for m in matches if m.risk_level == "yellow")
        return min(red * 8.0 + yellow * 3.0, 20.0)

    def _compute_confidence(self, matches, resume_text):
        """置信度：基于有证据的要求比例和证据质量"""
        if not matches:
            return 0.0
        with_evidence = sum(1 for m in matches if m.match_level != "none")
        evidence_ratio = with_evidence / len(matches)
        avg_conf = 0.0
        conf_count = 0
        for m in matches:
            conf = getattr(m, "confidence", 0) if hasattr(m, "confidence") else 0
            if conf > 0:
                avg_conf += conf
                conf_count += 1
        avg_conf = avg_conf / conf_count if conf_count > 0 else 0.3
        return evidence_ratio * 0.6 + avg_conf * 0.4

    def _compute_info_completeness(self, matches):
        """信息完整度：每条要求的证据覆盖程度"""
        if not matches:
            return 0.0
        strong = sum(1 for m in matches if m.match_level == "strong")
        medium = sum(1 for m in matches if m.match_level == "medium")
        weak = sum(1 for m in matches if m.match_level == "weak")
        total = len(matches)
        return (strong * 1.0 + medium * 0.6 + weak * 0.3) / total

    def dim_by_type(self, ms, types, w):
        """分维度评分 — 无默认补分，改为纯证据驱动"""
        t = [m for m in ms if m.requirement_type in types]
        if not t:
            return 0
        vals = [
            min(
                1.0,
                MATCH_SCORE.get(m.match_level, 0.0) * (1.1 if m.priority == "high" else 1.0),
            )
            for m in t
        ]
        return round(sum(vals) / len(vals) * w)

    def expr(self, text, w):
        """简历表达质量分（辅助分，非岗位匹配分，仅衡量文本完整度）"""
        if not text:
            return 0
        s = 0.45
        if any(k in text for k in ["负责", "参与", "实现", "设计", "完成"]):
            s += 0.2
        if any(k in text for k in ["提升", "降低", "优化", "效率", "性能", "%", "稳定"]):
            s += 0.2
        if any(k in text for k in ["项目", "系统", "平台", "模块"]):
            s += 0.1
        if len(text) > 300:
            s += 0.05
        return round(min(1, s) * w)

    def risk_dim(self, ms, w):
        red = sum(1 for m in ms if m.risk_level == "red")
        yellow = sum(1 for m in ms if m.risk_level == "yellow")
        return round(max(0, 1 - (red + yellow * 0.45) / max(1, len(ms))) * w)

    def rec(self, total):
        for th, txt in RECOMMENDATION_LEVELS:
            if total >= th:
                return txt
        return RECOMMENDATION_LEVELS[-1][1]

    def lv(self, total):
        return (
            "high"
            if total >= 85
            else "medium_high"
            if total >= 70
            else "medium_low"
            if total >= 55
            else "low"
        )

    def summary(self, total, must_have_score, risk_penalty, matches):
        strong = sum(1 for m in matches if m.match_level == "strong")
        red = sum(1 for m in matches if m.risk_level == "red")
        yellow = sum(1 for m in matches if m.risk_level == "yellow")
        if total >= 85:
            return f"候选人与岗位高度匹配（must-have基础分{must_have_score:.0f}），" f"共有 {strong} 项要求具备较强证据。"
        if total >= 70:
            return f"候选人与岗位具备较好匹配度，" f"但仍有 {red} 项红色风险和 {yellow} 项黄色风险。"
        if total >= 55:
            return (
                f"候选人与岗位存在一定相关性，但证据链不够充分"
                f"（must-have基础分{must_have_score:.0f}，风险扣分{risk_penalty:.0f}），"
                f"需补强核心短板。"
            )
        return (
            f"候选人与岗位匹配度较低"
            f"（must-have基础分{must_have_score:.0f}，风险扣分{risk_penalty:.0f}），"
            f"当前简历中缺少多项核心要求证据。"
        )
