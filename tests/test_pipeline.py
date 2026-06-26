import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from router import CareerFitRouter
class PipelineTest(unittest.TestCase):
    def test_markdown(self):
        text='【简历】技能：Java、Spring Boot、MySQL。项目：用户系统。【岗位JD】招聘Java后端，要求Spring Boot和MySQL。'
        out=CareerFitRouter().run(text)
        self.assertIn('简历-JD匹配诊断报告', out)
        self.assertIn('综合匹配度', out)
    def test_json(self):
        text='【简历】技能：Java、Spring Boot、MySQL。项目：用户系统。【岗位JD】招聘Java后端，要求Spring Boot和MySQL。'
        out=CareerFitRouter().run(text,'json')
        self.assertIn('overall_score', out)
if __name__=='__main__': unittest.main()
