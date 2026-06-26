"""覆盖方案 T2（只有简历）和 T9（学生简历）"""
import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from router import CareerFitRouter
from services.input_classifier import classify_input

class ResumeOnlyTest(unittest.TestCase):
    def test_resume_only(self):
        """T2: 只有简历 — 输出职业方向和简历建议"""
        text = '【简历】技能：Java、Spring Boot、MySQL。项目：用户管理系统。'
        out = CareerFitRouter().run(text)
        self.assertIn('职业方向', out)

    def test_resume_short(self):
        """T9: 学生简历（无工作经验）— 不因没有工作经历而错误否定"""
        text = '【简历】学校：XX大学，专业：计算机科学与技术，学历：本科，技能：Java、Python。'
        out = CareerFitRouter().run(text)
        self.assertIn('职业方向', out)
        # 不应该因为无工作经历而报错
        self.assertNotIn('异常', out)

    def test_classifier_resume_only(self):
        r = classify_input('【简历】技能：Java')
        self.assertEqual(r['input_type'], 'resume_only')

if __name__ == '__main__':
    unittest.main()
