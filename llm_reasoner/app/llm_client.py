import os
import requests
import json


class LLMClient:
    def __init__(self, url: str | None = None, model: str | None = None):
        """
        url/model은 기본 Ollama 설정을 따르되, 필요 시 파라미터나 env로 오버라이드:
          - LLM_API_URL (예: http://localhost:11434/api/generate)
          - LLM_MODEL   (예: phi3:mini, llama3:8b 등)
        """
        self.url = url or os.getenv("LLM_API_URL", "http://localhost:11434/api/generate")
        self.model = model or os.getenv("LLM_MODEL", "phi3:mini")

    def generate(self, prompt: str) -> str:
        """
        Ollama 모델을 호출하여 텍스트를 생성하는 함수.
        analyzer.py는 반드시 이 이름(generate)을 사용한다.
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        try:
            res = requests.post(self.url, json=payload)
            data = res.json()
            return data.get("response", "")
        except Exception as e:
            return f"LLM error: {e}"
