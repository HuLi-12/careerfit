class ResumeOptimizer:
    def optimize(self, resume, matches):
        risks = [m for m in matches if m.risk_level in ["red", "yellow"]]
        out = []
        for m in risks[:5]:
            t = m.requirement.replace("具备 ", "").replace(" 相关能力", "").replace(" 相关经验优先", "")
            out.append(
                {
                    "target": m.requirement,
                    "original": f'当前简历中缺少"{t}"的明确描述。'
                    if m.match_level == "none"
                    else f'简历中出现与"{t}"相关但不充分的内容。',
                    "problem": m.reason,
                    "optimized_text": f'围绕"{t}"补充项目经历：说明业务背景、个人职责、技术方案、遇到的问题和最终结果。',
                    "reason": m.suggestion,
                }
            )
        if not out:
            out.append(
                {
                    "target": "项目经历表达",
                    "original": "当前已有匹配基础，但职责和结果仍可强化。",
                    "problem": '当前已有匹配基础，但职责和结果仍可强化。建议采用"项目背景 + 个人职责 + 技术方案 + 结果指标"的结构改写项目。',
                    "optimized_text": '建议采用"项目背景 + 个人职责 + 技术方案 + 结果指标"的结构改写项目。',
                    "reason": "结构化表达可以提升可读性和可信度，让面试官快速理解你的角色和贡献。",
                }
            )
        return out
