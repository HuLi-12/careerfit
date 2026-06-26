"""多场景匹配测试 — Redis缺失、中等匹配、弱匹配、项目缺失、技能栏缺失"""
import sys, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from router import CareerFitRouter
from services.score_engine import ScoreEngine
from schemas.models import EvidenceMatch


class MatchScenariosTest(unittest.TestCase):
    def test_redis_missing_risk(self):
        """Redis缺失 — 应为红色风险"""
        text = "【简历】技能：Java、Spring Boot、MySQL。项目：用户系统。【岗位JD】招聘Java后端，要求Spring Boot、MySQL，熟悉Redis。"
        out = CareerFitRouter().run(text)
        # 报告应指出风险
        self.assertIn("风险", out)

    def test_skill_section_missing(self):
        """技能栏缺失 — 不应崩溃"""
        text = "【简历】姓名：张三。【岗位JD】招聘Java后端，要求Spring Boot。"
        out = CareerFitRouter().run(text)
        self.assertTrue(len(out) > 0)

    def test_json_has_score_fields(self):
        """JSON输出包含新评分字段"""
        text = "【简历】技能：Java、Spring Boot、MySQL。项目：用户系统。【岗位JD】招聘Java后端，要求Spring Boot和MySQL。"
        import json

        out = CareerFitRouter().run(text, "json")
        d = json.loads(out)
        score = d.get("score", {})
        self.assertIn("must_have_score", score)
        self.assertIn("nice_to_have_bonus", score)
        self.assertIn("risk_penalty", score)
        self.assertIn("confidence", score)
        self.assertIn("information_completeness", score)

    def test_evidence_level_in_match(self):
        """匹配结果包含证据等级和置信度"""
        text = "【简历】技能：Java、Spring Boot。项目：用户系统。【岗位JD】招聘Java后端，要求Spring Boot和MySQL。"
        import json

        out = CareerFitRouter().run(text, "json")
        d = json.loads(out)
        matches = d.get("evidence_matches", [])
        self.assertTrue(len(matches) > 0)
        # 至少有一条匹配有evidence_blocks
        has_blocks = any(m.get("evidence_blocks") for m in matches)
        has_confidence = any(m.get("confidence", 0) > 0 for m in matches)
        self.assertTrue(has_blocks or has_confidence)


if __name__ == "__main__":
    unittest.main()
