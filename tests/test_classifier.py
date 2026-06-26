import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from services.input_classifier import classify_input

class ClassifierTest(unittest.TestCase):
    def test_resume_and_jd(self):
        r = classify_input('【简历】Java项目【岗位JD】招聘Java后端')
        self.assertEqual(r['input_type'], 'resume_and_jd')
        self.assertTrue(r['has_resume'])
        self.assertTrue(r['has_jd'])

    def test_empty(self):
        self.assertEqual(classify_input('')['input_type'], 'unknown')

if __name__ == '__main__':
    unittest.main()
