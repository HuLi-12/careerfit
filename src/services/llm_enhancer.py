"""可选的模型增强层 — 有 LLM API 时增强输出质量，无 API 时规则兜底

所有增强点都是可选的，不影响核心 Pipeline 执行。
"""

from services.llm_client import LLMClient


class LLMEnhancer:
    """模型增强层：解析增强 / 推理增强 / 报告润色

    使用方式：
        enhancer = LLMEnhancer()
        if enhancer.available:
            enhanced = enhancer.enhance_report(report)
    """

    def __init__(self):
        self.client = LLMClient()

    @property
    def available(self) -> bool:
        return self.client.available

    def enhance_resume_parse(self, resume_text: str) -> dict:
        """简历解析增强（可选）：用模型补充规则解析可能遗漏的信息"""
        if not self.available or not resume_text:
            return {}
        reply = self.client.chat(
            messages=[
                {
                    "role": "user",
                    "content": (
                        "从以下简历文本中提取结构化信息，返回JSON格式：\n"
                        "{\"skills\": [...], \"project_keywords\": [...], "
                        "\"years_of_experience\": <数字>}\n\n"
                        + resume_text[:2000]
                    ),
                }
            ],
            temperature=0.1,
            max_tokens=500,
        )
        try:
            import json as _json

            return _json.loads(reply)
        except Exception:
            return {}

    def enhance_evidence_reasoning(self, requirement: str, resume_text: str) -> str:
        """证据推理增强（可选）：用模型判断简历与要求的匹配程度"""
        if not self.available:
            return ""
        return self.client.chat(
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"岗位要求：{requirement}\n\n"
                        f"简历文本：{resume_text[:1500]}\n\n"
                        "请判断简历是否满足该要求，并给出理由（20字以内）。"
                    ),
                }
            ],
            temperature=0.2,
            max_tokens=200,
        )

    def enhance_report(self, report: str) -> str:
        """报告润色增强（可选）：优化表达质量"""
        if not self.available or not report:
            return report
        polished = self.client.polish_report(report[:3000])
        return polished if polished else report
