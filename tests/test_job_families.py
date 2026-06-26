"""岗位族测试 — 产品经理、数据分析、测试、运维等不同岗位场景"""
import sys, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from router import CareerFitRouter
from services.input_classifier import classify_input


class JobFamiliesTest(unittest.TestCase):
    def test_product_manager_input(self):
        """产品经理岗位 — 能正常输出"""
        text = "【简历】技能：需求分析、原型设计、Axure、Figma。【岗位JD】招聘产品经理，负责需求分析和产品规划。"
        out = CareerFitRouter().run(text)
        self.assertIn("匹配", out)

    def test_data_analyst_input(self):
        """数据分析岗位 — 能正常输出"""
        text = "【简历】技能：SQL、Python、Pandas、Excel。【岗位JD】招聘数据分析师，要求SQL和数据分析能力。"
        out = CareerFitRouter().run(text)
        self.assertIn("匹配", out)

    def test_test_engineer_input(self):
        """测试岗位 — 能正常输出"""
        text = "【简历】技能：Python、Selenium、JMeter、Linux。【岗位JD】招聘测试开发，要求自动化测试经验。"
        out = CareerFitRouter().run(text)
        self.assertIn("匹配", out)

    def test_ops_engineer_input(self):
        """运维岗位 — 能正常输出"""
        text = "【简历】技能：Linux、Docker、Kubernetes、Jenkins。【岗位JD】招聘运维工程师，要求Docker和K8s经验。"
        out = CareerFitRouter().run(text)
        self.assertIn("匹配", out)

    def test_recruiter_eval_mode(self):
        """招聘方评估模式"""
        text = "【简历】技能：Java、Spring Boot。【岗位JD】招聘Java后端。我是招聘方，请评估这个候选人。"
        out = CareerFitRouter().run(text)
        self.assertIn("候选人", out) or self.assertIn("初筛", out)

    def test_social_recruitment_resume(self):
        """社招简历 — 有工作经验"""
        text = "【简历】工作经历：曾在XX科技公司任Java开发工程师2年，负责电商系统开发。【岗位JD】招聘Java后端。"
        out = CareerFitRouter().run(text)
        self.assertTrue(len(out) > 0)


if __name__ == "__main__":
    unittest.main()
