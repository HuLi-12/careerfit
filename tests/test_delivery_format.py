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

    def test_critical_files_keep_multiline_structure(self):
        root = Path(__file__).resolve().parents[1]
        minimum_lines = {
            "SKILL.md": 20,
            ".github/workflows/test.yml": 15,
            "Makefile": 10,
            "src/services/evidence_matcher.py": 150,
            "src/schemas/models.py": 80,
            "src/services/score_engine.py": 100,
            "examples/output_match_report.md": 80,
        }

        for relative_path, min_lines in minimum_lines.items():
            with self.subTest(path=relative_path):
                line_count = len((root / relative_path).read_text(encoding="utf-8").splitlines())
                self.assertGreaterEqual(line_count, min_lines)

    def test_verbose_test_result_is_checked_in(self):
        test_result = (Path(__file__).resolve().parents[1] / "docs/test_result.txt").read_text(
            encoding="utf-8"
        )
        self.assertGreaterEqual(len(test_result.splitlines()), 20)
        self.assertIn("test_", test_result)
        self.assertIn("Ran ", test_result)
        self.assertIn("OK", test_result)


if __name__ == "__main__":
    unittest.main()
