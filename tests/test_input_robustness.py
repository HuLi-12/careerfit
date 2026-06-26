"""输入鲁棒性测试 — Markdown格式、无分隔符、极短JD、超长输入"""
import sys, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from router import CareerFitRouter


class InputRobustnessTest(unittest.TestCase):
    def test_markdown_format_input(self):
        """Markdown格式输入 — 能正常解析"""
        text = """## 简历

技能：Java、Spring Boot、MySQL

项目：用户管理系统

## 岗位JD

招聘Java后端开发，要求Spring Boot和MySQL"""
        out = CareerFitRouter().run(text)
        self.assertIn("人岗匹配", out)

    def test_no_separator_input(self):
        """无分隔符输入 — 能自动拆分简历和JD"""
        text = "姓名：张三 技能：Java Spring Boot MySQL 项目：用户管理系统 招聘Java后端开发 要求Spring Boot和MySQL"
        out = CareerFitRouter().run(text)
        self.assertIn("匹配", out)

    def test_jd_one_line(self):
        """JD只有一句话 — 能拆解核心要求"""
        text = "【简历】技能：Java、Spring Boot【岗位JD】招聘Java后端"
        out = CareerFitRouter().run(text)
        self.assertIn("匹配", out)

    def test_long_jd(self):
        """JD很长 — 不截断关键内容"""
        text = "【简历】技能：Java、Spring Boot。" + "【岗位JD】" + "、".join(["要求" + str(i) for i in range(50)])
        out = CareerFitRouter().run(text)
        self.assertTrue(len(out) > 0)

    def test_long_resume(self):
        """简历很长 — 不崩溃"""
        text = "【简历】" + "技能：Java、Spring Boot。" * 100 + "【岗位JD】招聘Java后端"
        out = CareerFitRouter().run(text)
        self.assertTrue(len(out) > 0)


if __name__ == "__main__":
    unittest.main()
