import requests
class OllamaClient:
    def __init__(self, base_url: str):
        self.base_url=base_url
        self.session = requests.Session()

    def generate(self,model, prompt: str) -> str:  # prompt is of type str(String) and return type(->str) is also str (String )
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }

        response = self.session.post(
            url,
            json=payload,
            timeout=30
        )

        response.raise_for_status()

        result = response.json()

        return result["response"]