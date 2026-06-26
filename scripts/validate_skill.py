#!/usr/bin/env python3
"""校验 SKILL.md 元数据格式是否符合 SkillHub 提交规范。"""
import re
import sys
from pathlib import Path


def validate():
    root = Path(__file__).resolve().parents[1]
    skill_path = root / "SKILL.md"

    if not skill_path.exists():
        print("FAIL: SKILL.md not found")
        return False

    text = skill_path.read_text(encoding="utf-8")

    # 1. 是否存在 frontmatter
    if not text.startswith("---"):
        print("FAIL: SKILL.md missing frontmatter (must start with '---')")
        return False

    # 提取 frontmatter
    m = re.match(r"^---\s*\n(.+?)\n---", text, re.DOTALL)
    if not m:
        print("FAIL: SKILL.md frontmatter not properly closed (---)")
        return False

    fm = m.group(1)

    # 2. name 是否存在
    if not re.search(r"^name:\s*\S", fm, re.MULTILINE):
        print("FAIL: SKILL.md frontmatter missing 'name' field")
        return False

    # 3. description 是否存在
    if not re.search(r"^description:\s*\S", fm, re.MULTILINE):
        print("FAIL: SKILL.md frontmatter missing 'description' field")
        return False

    # 4. version 是否存在
    if not re.search(r"^version:\s*\S", fm, re.MULTILINE):
        print("FAIL: SKILL.md frontmatter missing 'version' field")
        return False

    # 5. tags 是否为数组
    lines = fm.splitlines()
    in_tags = False
    tags = []
    for line in lines:
        if line.startswith("tags:"):
            in_tags = True
            continue
        if in_tags:
            m = re.match(r"\s+-\s+(\S+)", line)
            if m:
                tags.append(m.group(1))
            else:
                break
    if not tags:
        print("FAIL: SKILL.md 'tags' must be a YAML list (each on its own line with '- ')")
        return False

    if len(tags) < 2:
        print("FAIL: SKILL.md tags must contain at least 2 entries")
        return False

    print(f"PASS: SKILL.md frontmatter valid (name={_get(fm, 'name')}, tags={tags})")
    return True


def _get(fm, key):
    m = re.search(rf"^{key}:\s*(.+)", fm, re.MULTILINE)
    return m.group(1).strip() if m else ""


if __name__ == "__main__":
    ok = validate()
    sys.exit(0 if ok else 1)
