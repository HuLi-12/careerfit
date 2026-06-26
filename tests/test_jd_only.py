"""覆盖方案 T3（只有JD）和 T5（JD格式混乱）"""
import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from router import CareerFitRouter
from services.input_classifier import classify_input

class JdOnlyTest(unittest.TestCase):
    def test_jd_only(self):
        """T3: 只有JD — 输出JD优化和候选人画像"""
        text = '【岗位JD】招聘Java后端，要求Spring Boot和MySQL，熟悉Redis优先。'
        out = CareerFitRouter().run(text)
        self.assertIn('候选人画像', out)

    def test_jd_messy_format(self):
        """T5: JD格式混乱 — 能拆解核心要求"""
        text = '招聘Java后端开发工程师 要求：Java Spring Boot MySQL 加分：Redis 地点：北京'
        out = CareerFitRouter().run(text)
        self.assertIn('JD优化', out) or self.assertIn('候选人画像', out)

    def test_classifier_jd_only(self):
        r = classify_input('【JD】招聘Java开发')
        self.assertEqual(r['input_type'], 'jd_only')

if __name__ == '__main__':
    unittest.main()
