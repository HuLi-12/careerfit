"""Prompt 模板加载器 — 从 prompts/ 目录加载 .md 模板"""

from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"


def load_prompt(name: str, **kwargs) -> str:
    """加载 prompt 模板并填充变量

    用法：
        prompt = load_prompt("resume_parse_enhance", resume_text=text)
    """
    path = PROMPTS_DIR / f"{name}.md"
    if not path.exists():
        return ""
    template = path.read_text(encoding="utf-8")
    if kwargs:
        try:
            return template.format(**kwargs)
        except KeyError:
            return template
    return template


def list_prompts() -> list:
    """列出所有可用 prompt 模板"""
    if not PROMPTS_DIR.exists():
        return []
    return sorted(p.stem for p in PROMPTS_DIR.iterdir() if p.suffix == ".md")
