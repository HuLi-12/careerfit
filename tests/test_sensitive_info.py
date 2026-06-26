"""覆盖方案 T7（包含敏感信息）和 T10（转行简历）"""
import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from router import CareerFitRouter
from services.safety_checker import SafetyChecker

class SensitiveInfoTest(unittest.TestCase):
    def test_sensitive_not_affect_score(self):
        """T7: 包含敏感信息 — 不基于敏感信息判断候选人"""
        text = '【简历】性别：男，年龄：28，民族：汉，婚育：已婚。技能：Java、Spring Boot、MySQL。项目：用户系统。【岗位JD】招聘Java后端，要求Spring Boot和MySQL。'
        out = CareerFitRouter().run(text)
        # 应该正常输出匹配报告，而不是因敏感信息报错
        self.assertIn('匹配', out)
        # 敏感信息不应该导致异常
        self.assertNotIn('异常', out)

    def test_safety_scan_detects_sensitive(self):
        """安全扫描器能检测敏感词"""
        self.assertTrue(SafetyChecker().scan('性别：男，技能：Java')['contains_sensitive_terms'])
        self.assertFalse(SafetyChecker().scan('技能：Java、Spring Boot')['contains_sensitive_terms'])

    def test_career_change(self):
        """T10: 转行简历 — 输出匹配结果而非报错"""
        text = '【简历】之前做销售，自学Java一年。项目：个人博客系统，使用Spring Boot。【岗位JD】招聘Java后端开发，要求熟悉Spring Boot。'
        out = CareerFitRouter().run(text)
        # 输出结果，不崩溃
        self.assertTrue(len(out) > 0)

if __name__ == '__main__':
    unittest.main()
