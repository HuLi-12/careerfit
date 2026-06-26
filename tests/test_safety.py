import sys, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from services.safety_checker import SafetyChecker


class SafetyTest(unittest.TestCase):
    def test_scan(self):
        self.assertTrue(SafetyChecker().scan("性别：男，技能：Java")["contains_sensitive_terms"])


if __name__ == "__main__":
    unittest.main()
