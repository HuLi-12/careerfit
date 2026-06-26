import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


class DeliveryFormatTest(unittest.TestCase):
    def test_gitattributes_enforces_lf_for_delivery_files(self):
        gitattributes = Path(__file__).resolve().parents[1] / ".gitattributes"
        self.assertTrue(gitattributes.exists(), ".gitattributes is required for stable raw/fresh-clone formatting")

        text = gitattributes.read_text(encoding="utf-8")
        self.assertIn("*.py text eol=lf", text)
        self.assertIn("*.md text eol=lf", text)
        self.assertIn("*.yml text eol=lf", text)
        self.assertIn("Makefile text eol=lf", text)


if __name__ == "__main__":
    unittest.main()
