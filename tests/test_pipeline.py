import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from router import CareerFitRouter


class PipelineTest(unittest.TestCase):
    def test_markdown(self):
        text = (
            "【简历】技能：Java、Spring Boot、MySQL。项目：用户系统。"
            "【岗位JD】招聘Java后端，要求Spring Boot和MySQL。"
        )
        out = CareerFitRouter().run(text)
        self.assertIn("CareerFit 人岗匹配诊断报告", out)
        self.assertIn("总分", out)

    def test_json(self):
        text = (
            "【简历】技能：Java、Spring Boot、MySQL。项目：用户系统。"
            "【岗位JD】招聘Java后端，要求Spring Boot和MySQL。"
        )
        out = CareerFitRouter().run(text, "json")
        self.assertIn("overall_score", out)

    def test_skill_frontmatter_uses_one_field_per_line(self):
        skill_text = Path(__file__).resolve().parents[1].joinpath("SKILL.md").read_text(encoding="utf-8")
        frontmatter = re.match(r"^---\n(.*?)\n---", skill_text, re.DOTALL)
        self.assertIsNotNone(frontmatter)
        fm = frontmatter.group(1)
        self.assertRegex(fm, r"(?m)^description:\s*.+$")
        self.assertRegex(fm, r"(?m)^version:\s*.+$")
        self.assertNotRegex(fm, r"(?m)^description:.*version:")

    def test_example_report_does_not_duplicate_requirements(self):
        example_input = Path(__file__).resolve().parents[1].joinpath("examples", "input_match_analysis.txt").read_text(
            encoding="utf-8"
        )
        out = CareerFitRouter().run(example_input)
        requirements_section = out.split("## 3. 岗位核心要求拆解", 1)[1].split("## 4. 核心证据链表", 1)[0]
        self.assertEqual(requirements_section.count("| 具备 Redis 相关能力 |"), 1)


if __name__ == "__main__":
    unittest.main()
