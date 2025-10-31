import requests
import json


class OllamaClient:
    def __init__(self, base_url="http://localhost:11434", model="qwen3:4b"):
        self.base_url = base_url.rstrip('/')
        self.model = model

    def generate_response(self, prompt, system_prompt=None):
        """调用Ollama生成回复。

        Returns a string. Handles a few possible JSON shapes returned by different Ollama versions:
        - {"response": "..."}
        - {"outputs": [{"content": "..."}, ...]}
        - streaming/other variants (attempt to join text fields)
        """
        try:
            url = f"{self.base_url}/api/generate"

            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }

            if system_prompt:
                payload["system"] = system_prompt

            response = requests.post(url, json=payload, timeout=120)

            if response.status_code != 200:
                # Try to include response body for debugging
                body = response.text
                return f"API调用失败: {response.status_code} - {body}"

            result = response.json()

            # Common shapes
            if isinstance(result, dict):
                if 'response' in result and isinstance(result['response'], str):
                    return result['response']

                # Newer versions sometimes use outputs list
                outputs = result.get('outputs') or result.get('result')
                if isinstance(outputs, list):
                    parts = []
                    for out in outputs:
                        if isinstance(out, dict):
                            # look for common keys
                            for key in ('content', 'text', 'message'):
                                if key in out and isinstance(out[key], str):
                                    parts.append(out[key])
                                    break
                        elif isinstance(out, str):
                            parts.append(out)
                    if parts:
                        return '\n'.join(parts)

            # Fallback: return raw text
            return response.text

        except requests.exceptions.ConnectionError:
            return "无法连接到Ollama服务，请确保Ollama正在运行"
        except Exception as e:
            return f"AI调用错误: {str(e)}"