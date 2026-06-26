"""技能同义映射和分类测试 — 验证 ES→Elasticsearch、k8s→Kubernetes 等别名匹配"""
import sys, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from services.skill_normalizer import SkillNormalizer
from services.evidence_matcher import EvidenceMatcher
from schemas.models import JobProfile, ResumeProfile, RequirementItem


class SkillTaxonomyTest(unittest.TestCase):
    def setUp(self):
        self.norm = SkillNormalizer()
        self.matcher = EvidenceMatcher()

    def test_es_to_elasticsearch(self):
        """ES → Elasticsearch 同义映射"""
        self.assertEqual(self.norm.normalize("ES"), "Elasticsearch")

    def test_k8s_to_kubernetes(self):
        """k8s → Kubernetes 同义映射"""
        self.assertEqual(self.norm.normalize("k8s"), "Kubernetes")

    def test_springcloud_mapped(self):
        """SpringCloud → Spring Cloud"""
        self.assertEqual(self.norm.normalize("SpringCloud"), "Spring Cloud")

    def test_synonym_skill_matching(self):
        """简历写ES，JD要求Elasticsearch — 应匹配成功"""
        job = JobProfile(
            must_have_requirements=[
                RequirementItem("具备 Elasticsearch 相关能力", "database", "high", ["Elasticsearch"])
            ]
        )
        resume = ResumeProfile(raw_text="技能：ES")
        resume.skills["all"] = ["Elasticsearch"]
        matches = self.matcher.match(job, resume)
        # skill栏匹配但无项目支撑 → C级 → medium
        self.assertEqual(
            matches[0].match_level,
            "medium",
            f"ES→Elasticsearch 应匹配 medium, 实际: {matches[0].match_level}",
        )

    def test_k8s_in_project_matches(self):
        """简历项目写k8s，JD要求Kubernetes — 应匹配"""
        job = JobProfile(
            must_have_requirements=[
                RequirementItem("具备 Kubernetes 相关能力", "tool", "high", ["Kubernetes"])
            ]
        )
        from schemas.models import ProjectExperienceItem

        resume = ResumeProfile(raw_text="项目中使用k8s部署微服务, 负责容器编排")
        resume.project_experience = [
            ProjectExperienceItem(
                project_name="微服务部署平台",
                tech_stack=["k8s", "Docker"],
                tasks=["使用k8s部署微服务"],
                raw_text="项目中使用k8s部署微服务, 负责容器编排",
            )
        ]
        resume.skills["all"] = []
        matches = self.matcher.match(job, resume)
        # weak or better, not none
        self.assertNotEqual(matches[0].match_level, "none", "k8s→Kubernetes 不应为 none")


if __name__ == "__main__":
    unittest.main()
