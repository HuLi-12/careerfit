"""覆盖方案 T4（简历很短）和 T8（无关输入）"""
import sys, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from router import CareerFitRouter
from services.input_classifier import classify_input


class EmptyInputTest(unittest.TestCase):
    def test_empty_input(self):
        """T4: 空输入 — 不崩溃，返回引导信息"""
        out = CareerFitRouter().run("")
        self.assertIn("输入信息不足", out)

    def test_short_input(self):
        """T4: 输入过短 — 给出补充模板"""
        out = CareerFitRouter().run("你好")
        self.assertIn("输入信息不足", out)

    def test_nonsense_input(self):
        """T8: 无关输入 — 给出合理引导"""
        out = CareerFitRouter().run("今天天气真好")
        self.assertIn("输入信息不足", out)

    def test_classifier_empty(self):
        self.assertEqual(classify_input("")["input_type"], "unknown")


if __name__ == "__main__":
    unittest.main()
