"""覆盖方案 T6（中英文混合）"""
import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from router import CareerFitRouter

class MixedLanguageTest(unittest.TestCase):
    def test_mixed_cn_en(self):
        """T6: 中英文混合 — 能正常解析和匹配"""
        text = '【简历】Skills: Java, Spring Boot, MySQL. 项目：User Management System。【岗位JD】Hiring Java Backend, familiar with Spring Boot and MySQL.'
        out = CareerFitRouter().run(text)
        self.assertIn('匹配', out)

    def test_english_jd(self):
        """全英文JD"""
        text = '【简历】技能：Java、Spring Boot、MySQL。【岗位JD】Hiring Java Backend Developer. Requirements: Java, Spring Boot, MySQL.'
        out = CareerFitRouter().run(text)
        self.assertIn('匹配', out)

if __name__ == '__main__':
    unittest.main()
