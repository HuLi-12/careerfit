"""覆盖方案 T1（完整简历+完整JD）"""
import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from router import CareerFitRouter

class ResumeJdMatchTest(unittest.TestCase):
    def test_full_match(self):
        """T1: 完整简历+完整JD — 输出完整匹配报告"""
        text = '【简历】技能：Java、Spring Boot、MySQL。项目：用户管理系统。【岗位JD】招聘Java后端，要求Spring Boot和MySQL。'
        out = CareerFitRouter().run(text)
        self.assertIn('匹配', out)
        self.assertIn('综合匹配度', out)
        self.assertIn('证据链匹配表', out)

    def test_json_output(self):
        """T1: JSON 输出格式正确"""
        text = '【简历】技能：Java、Spring Boot、MySQL。项目：用户系统。【岗位JD】招聘Java后端，要求Spring Boot和MySQL。'
        out = CareerFitRouter().run(text, 'json')
        self.assertIn('overall_score', out)
        self.assertIn('evidence_matches', out)

    def test_full_with_optional(self):
        """包含加分项的匹配"""
        text = '【简历】技能：Java、Spring Boot、MySQL。项目：用户系统。【岗位JD】招聘Java后端，要求Spring Boot和MySQL，熟悉Redis优先。'
        out = CareerFitRouter().run(text)
        self.assertIn('匹配', out)

if __name__ == '__main__':
    unittest.main()
