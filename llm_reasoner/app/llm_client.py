import requests
import json


class LLMClient:
    def __init__(self):
        self.url = "http://localhost:11434/api/generate"
        self.model = "phi3:mini"

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

