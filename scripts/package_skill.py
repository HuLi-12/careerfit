#!/usr/bin/env python3
"""打包脚本 — 输出 dist/careerfit-evidence-skill.zip"""

import os, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
EXCLUDES = {
    "__pycache__",
    ".pytest_cache",
    ".git",
    ".claude",
    "dist",
    "*.pyc",
    "*.pyo",
    ".DS_Store",
    ".idea",
}


def should_exclude(name: str) -> bool:
    parts = name.replace("\\", "/").split("/")
    for p in parts:
        if p in EXCLUDES or any(p.endswith(suf) for suf in (".pyc", ".pyo")):
            return True
    return False


def main():
    os.makedirs(DIST, exist_ok=True)
    zip_path = DIST / "careerfit-evidence-skill.zip"

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(ROOT):
            rel = Path(root).relative_to(ROOT)
            if any(p in EXCLUDES for p in rel.parts):
                continue
            # 跳过 .git 内部子目录
            dirs[:] = [d for d in dirs if d not in EXCLUDES and not d.startswith(".")]
            for f in files:
                if any(f.endswith(suf) for suf in (".pyc", ".pyo")):
                    continue
                fpath = Path(root) / f
                arcname = str(rel / f)
                zf.write(fpath, arcname)

    print(f"OK: {zip_path} ({os.path.getsize(zip_path) / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
