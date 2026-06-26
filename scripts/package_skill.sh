#!/bin/bash
# 一键打包 Skill ZIP
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ZIP_NAME="careerfit-evidence-skill.zip"

cd "$PROJECT_DIR"

echo "📦 Packaging CareerFit Evidence Skill ..."

# 校验
python scripts/validate_skill.py

# 运行测试
python -m unittest discover -s tests -q
echo "✅ All tests passed"

# 打包
if command -v zip &> /dev/null; then
    zip -r "$ZIP_NAME" \
        SKILL.md README.md requirements.txt pyproject.toml Makefile \
        src/ examples/ tests/ docs/ scripts/ \
        -x "*/__pycache__/*" "*.pyc" ".pytest_cache/*"
    echo "✅ Packaged: $ZIP_NAME"
else
    echo "⚠️  zip not available, skipping package step"
fi
