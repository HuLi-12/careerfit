"""可选的 LLM API 客户端 — 有 API 配置时启用，无配置时静默降级"""

import json
import os


class LLMClient:
    """轻量 LLM API 客户端

    仅当 CAREERFIT_LLM_API_KEY / _BASE / _MODEL 全部设置时才启用。
    默认关闭，不依赖任何外部服务。

    使用方式：
        client = LLMClient()
        if client.available:
            reply = client.chat([{"role": "user", "content": "你好"}])
    """

    def __init__(self):
        self.api_key = os.environ.get("CAREERFIT_LLM_API_KEY", "")
        self.api_base = os.environ.get("CAREERFIT_LLM_API_BASE", "")
        self.model = os.environ.get("CAREERFIT_LLM_MODEL", "")
        self._available = bool(self.api_key and self.api_base and self.model)

    @property
    def available(self) -> bool:
        return self._available

    def chat(self, messages, system_prompt="", temperature=0.3, max_tokens=1024):
        if not self._available:
            return ""
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
        }
        body = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
        }
        if system_prompt:
            body["system"] = system_prompt
        try:
            import urllib.request
            req = urllib.request.Request(
                f"{self.api_base}/messages",
                data=json.dumps(body).encode(),
                headers=headers,
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode())
            return result.get("content", [{}])[0].get("text", "")
        except Exception:
            return ""

    def summarize(self, text: str, max_length: int = 200) -> str:
        if not self._available or not text:
            return ""
        return self.chat(
            messages=[{"role": "user", "content": f"请用{max_length}字以内概括以下内容：\n\n{text[:2000]}"}],
            temperature=0.2,
            max_tokens=max_length,
        )

    def polish_report(self, report: str) -> str:
        if not self._available or not report:
            return ""
        return self.chat(
            messages=[
                {"role": "user", "content": "润色以下人岗匹配报告，保持 Markdown 格式和原有信息完整：\n\n" + report[:3000]}
            ],
            temperature=0.3,
            max_tokens=2048,
        )
