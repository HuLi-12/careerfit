import argparse, sys
from pathlib import Path
from router import CareerFitRouter


def main():
    p = argparse.ArgumentParser(description="CareerFit Evidence：简历-JD证据链匹配助手")
    p.add_argument("--input", "-i", default="", help="输入文本文件路径")
    p.add_argument("--output", "-o", default="", help="输出报告路径")
    p.add_argument("--format", "-f", choices=["markdown", "json"], default="markdown")
    a = p.parse_args()
    text = (
        Path(a.input).read_text(encoding="utf-8")
        if a.input
        else (sys.stdin.read() if not sys.stdin.isatty() else "")
    )
    out = CareerFitRouter().run(text, a.format)
    if a.output:
        Path(a.output).write_text(out, encoding="utf-8")
        print(f"已生成报告：{a.output}")
    else:
        print(out)


if __name__ == "__main__":
    main()
