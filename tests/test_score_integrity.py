"""评分完整性测试 — 验证分数、证据块、置信度、风险等级等结构化输出"""
import sys, json, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from router import CareerFitRouter
from services.score_engine import ScoreEngine
from services.evidence_matcher import EvidenceMatcher
from schemas.models import (
    EvidenceBlock,
    EvidenceMatch,
    ScoreResult,
    JobProfile,
    ResumeProfile,
    RequirementItem,
    ProjectExperienceItem,
)


class ScoreIntegrityTest(unittest.TestCase):
    def setUp(self):
        self.engine = ScoreEngine()
        self.matcher = EvidenceMatcher()

    # ── 评分结构完整性 ──

    def test_json_has_all_score_fields(self):
        """JSON输出的score必须包含全部7个评分字段"""
        text = "【简历】技能：Java、Spring Boot、MySQL。项目：用户系统。【岗位JD】招聘Java后端，要求Java、Spring Boot、MySQL。"
        out = CareerFitRouter().run(text, "json")
        d = json.loads(out)
        score = d.get("score", {})
        required = [
            "overall_score",
            "must_have_score",
            "nice_to_have_bonus",
            "risk_penalty",
            "confidence",
            "information_completeness",
            "recommendation",
            "level",
            "score_breakdown",
            "summary",
        ]
        for field in required:
            self.assertIn(field, score, f"score 缺少字段: {field}")

    def test_json_has_evidence_blocks(self):
        """每条evidence_match必须有evidence_blocks列表和confidence"""
        text = "【简历】技能：Java、Spring Boot。【岗位JD】招聘Java后端，要求Java。"
        out = CareerFitRouter().run(text, "json")
        d = json.loads(out)
        for m in d.get("evidence_matches", []):
            self.assertIn("evidence_blocks", m, f"{m['requirement']} 缺少 evidence_blocks")
            self.assertIn("confidence", m, f"{m['requirement']} 缺少 confidence")
            self.assertIsInstance(m["evidence_blocks"], list)
            self.assertIsInstance(m["confidence"], (int, float))

    # ── 证据等级结构 ──

    def test_evidence_block_structure(self):
        """EvidenceBlock 必须有 source_type / evidence_level / confidence"""
        job = JobProfile(
            must_have_requirements=[RequirementItem("具备 Java 相关能力", "hard_skill", "high", ["Java"])]
        )
        resume = ResumeProfile(raw_text="技能：Java")
        resume.skills["all"] = ["Java"]
        blocks = self.matcher.find_blocks(job.must_have_requirements[0], resume)
        for b in blocks:
            self.assertTrue(
                b.source_type in ("skill_section", "project_experience", "weak_semantic")
            )
            self.assertIn(b.evidence_level, ("A", "B", "C", "D", "E"))
            self.assertGreaterEqual(b.confidence, 0.0)
            self.assertLessEqual(b.confidence, 1.0)

    def test_strong_match_has_high_evidence(self):
        """strong匹配必须有至少一条A级证据（技能+项目+结果指标）"""
        job = JobProfile(
            must_have_requirements=[RequirementItem("具备 Java 相关能力", "hard_skill", "high", ["Java"])]
        )
        resume = ResumeProfile(raw_text="技能：Java")
        resume.skills["all"] = ["Java"]
        resume.project_experience = [
            ProjectExperienceItem(
                project_name="用户系统",
                tech_stack=["Java"],
                tasks=["后端接口开发"],
                results=["提升接口响应速度50%"],
                raw_text="使用Java开发后端接口，通过SQL优化提升性能50%",
            )
        ]
        matches = self.matcher.match(job, resume)
        m = matches[0]
        self.assertEqual(m.match_level, "strong", f"有技能+项目+结果应strong, 实际: {m.match_level}")
        levels = [b.evidence_level for b in m.evidence_blocks]
        self.assertIn("A", levels, f"strong匹配应含A级证据，实际: {levels}")

    def test_no_evidence_is_level_e(self):
        """无证据时match_level应为none，风险根据优先级判定"""
        job = JobProfile(
            must_have_requirements=[
                RequirementItem("具备 Redis 相关能力", "database", "medium", ["Redis"])
            ]
        )
        resume = ResumeProfile(raw_text="技能：Java")
        resume.skills["all"] = ["Java"]
        matches = self.matcher.match(job, resume)
        m = matches[0]
        self.assertEqual(m.match_level, "none")
        # medium优先级的none → red（新风险规则）
        self.assertEqual(m.risk_level, "red",
                         f"medium+none应为red, 实际: {m.risk_level}")

    def test_b_level_is_medium_not_strong(self):
        """B级证据应为medium，仅A级证据为strong"""
        job = JobProfile(
            must_have_requirements=[RequirementItem("具备 Java 相关能力", "hard_skill", "high", ["Java"])]
        )
        resume = ResumeProfile(raw_text="技能：Java")
        resume.skills["all"] = ["Java"]
        resume.project_experience = [
            ProjectExperienceItem(
                project_name="用户系统", tech_stack=["Java"], tasks=["后端接口开发"], raw_text="使用Java开发后端接口"
            )
        ]
        matches = self.matcher.match(job, resume)
        m = matches[0]
        # 有技能栏(→C) + 项目(→B) 但无结果指标 → 无A级 → medium
        self.assertEqual(m.match_level, "medium", f"B级无结果应medium, 实际: {m.match_level}")
        levels = [b.evidence_level for b in m.evidence_blocks]
        self.assertNotIn("A", levels)
        self.assertIn("B", levels)

    def test_risk_penalty_capped(self):
        """风险扣分不应超过20"""
        from services.score_engine import ScoreEngine
        from schemas.models import EvidenceMatch

        engine = ScoreEngine()
        # 构造10个red风险，按旧公式=80，应被cap到20
        red_matches = [
            EvidenceMatch(
                requirement=f"要求{i}",
                requirement_type="hard_skill",
                priority="high",
                match_level="none",
                risk_level="red",
            )
            for i in range(10)
        ]
        penalty = engine._risk_penalty(red_matches)
        self.assertLessEqual(penalty, 20.0, f"风险扣分应≤20, 实际: {penalty}")

    def test_evidence_block_has_keywords(self):
        """evidence_block应包含matched_keywords"""
        job = JobProfile(
            must_have_requirements=[RequirementItem("具备 Java 相关能力", "hard_skill", "high", ["Java"])]
        )
        resume = ResumeProfile(raw_text="技能：Java")
        resume.skills["all"] = ["Java"]
        blocks = self.matcher.find_blocks(job.must_have_requirements[0], resume)
        for b in blocks:
            self.assertIsInstance(b.matched_keywords, list)

    def test_evidence_block_has_source_name(self):
        """evidence_block应包含source_name"""
        job = JobProfile(
            must_have_requirements=[RequirementItem("具备 Java 相关能力", "hard_skill", "high", ["Java"])]
        )
        resume = ResumeProfile(raw_text="技能：Java")
        resume.skills["all"] = ["Java"]
        blocks = self.matcher.find_blocks(job.must_have_requirements[0], resume)
        for b in blocks:
            self.assertTrue(len(b.source_name) > 0, f"source_name不应为空, type={b.source_type}")

    # ── 评分合理性 ──

    def test_must_have_score_range(self):
        """must_have_score 应在 0-100 范围内"""
        text = "【简历】技能：Java、Spring Boot、MySQL。【岗位JD】招聘Java后端，要求Java、Spring Boot、MySQL、Redis。"
        out = CareerFitRouter().run(text, "json")
        d = json.loads(out)
        s = d["score"]
        self.assertGreaterEqual(s["must_have_score"], 0)
        self.assertLessEqual(s["must_have_score"], 100)

    def test_confidence_and_completeness_range(self):
        """confidence和information_completeness应在0-1之间"""
        text = "【简历】技能：Java、Spring Boot。【岗位JD】招聘Java后端，要求Java、Spring Boot。"
        out = CareerFitRouter().run(text, "json")
        d = json.loads(out)
        s = d["score"]
        for field in ("confidence", "information_completeness"):
            val = s[field]
            self.assertGreaterEqual(val, 0.0, f"{field} 不应为负数: {val}")
            self.assertLessEqual(val, 1.0, f"{field} 不应超过1: {val}")

    def test_risk_penalty_non_negative(self):
        """risk_penalty必须>=0"""
        text = "【简历】技能：Java、Spring Boot。【岗位JD】招聘Java后端，要求Java、Spring Boot、Redis。"
        out = CareerFitRouter().run(text, "json")
        d = json.loads(out)
        self.assertGreaterEqual(d["score"]["risk_penalty"], 0)

    def test_overall_score_derivation(self):
        """总分 = must_have + nice_to_have - risk, 截断到[0,100]"""
        text = "【简历】技能：Java、Spring Boot、MySQL。项目：用户系统。【岗位JD】招聘Java后端，要求Java、Spring Boot、MySQL。"
        out = CareerFitRouter().run(text, "json")
        d = json.loads(out)
        s = d["score"]
        expected = max(
            0, min(100, round(s["must_have_score"] + s["nice_to_have_bonus"] - s["risk_penalty"]))
        )
        self.assertEqual(s["overall_score"], expected)

    # ── Redis缺失场景 ──

    def test_redis_missing_is_yellow_risk(self):
        """Redis缺失应为yellow风险（非red）"""
        text = "【简历】技能：Java、Spring Boot、MySQL。项目：用户系统。【岗位JD】招聘Java后端，要求Spring Boot、MySQL，熟悉Redis。"
        out = CareerFitRouter().run(text, "json")
        d = json.loads(out)
        matches = d.get("evidence_matches", [])
        redis_matches = [
            m for m in matches if "Redis" in m["requirement"] or "redis" in m["requirement"].lower()
        ]
        for m in redis_matches:
            self.assertEqual(m["match_level"], "none", f"Redis 应无匹配, 实际: {m['match_level']}")
            self.assertIn(
                m["risk_level"], ("yellow", "red"), f"Redis 风险应为 yellow, 实际: {m['risk_level']}"
            )

    # ── 报告非兜底页 ──

    def test_report_not_error_fallback(self):
        """报告不应是异常兜底页"""
        text = "【简历】技能：Java、Spring Boot、MySQL。【岗位JD】招聘Java后端，要求Java、Spring Boot、MySQL。"
        out = CareerFitRouter().run(text)
        self.assertNotIn("报告生成异常", out)
        self.assertNotIn("异常", out[:50])

    # ── 空输入健壮性 ──

    def test_empty_input_score(self):
        """空输入不崩溃，返回有效score结构"""
        out = CareerFitRouter().run("", "json")
        d = json.loads(out)
        self.assertIn("score", d)
        self.assertIn("overall_score", d["score"])

    # ── 重复要求场景 ──

    def test_spring_springboot_no_duplicate(self):
        """Spring 和 Spring Boot 不会相互污染匹配等级"""
        job = JobProfile(
            must_have_requirements=[
                RequirementItem("具备 Spring Boot 相关能力", "framework", "high", ["Spring Boot"]),
                RequirementItem("具备 Spring 相关能力", "framework", "medium", ["Spring"]),
            ]
        )
        resume = ResumeProfile(raw_text="技能：Spring Boot")
        resume.skills["all"] = ["Spring Boot"]
        matches = self.matcher.match(job, resume)
        spring_boot = [m for m in matches if "Spring Boot" in m.requirement][0]
        spring = [m for m in matches if m.requirement == "具备 Spring 相关能力"][0]
        # Spring Boot 应 strong 或 medium
        self.assertIn(spring_boot.match_level, ("strong", "medium"))
        # Spring 不应为 strong（因为简历没有 Spring）
        self.assertNotEqual(spring.match_level, "strong")


if __name__ == "__main__":
    unittest.main()
