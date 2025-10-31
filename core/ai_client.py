import requests
import json
from abc import ABC, abstractmethod


class AIClient(ABC):
    """AI客户端抽象基类"""
    
    @abstractmethod
    def generate_response(self, prompt, system_prompt=None):
        pass


class OllamaClient(AIClient):
    """Ollama客户端实现"""
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
                return f"Ollama API调用失败: {response.status_code} - {body}"

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


class OpenAIClient(AIClient):
    """OpenAI API客户端"""
    def __init__(self, api_key, base_url="https://api.openai.com/v1", model="gpt-3.5-turbo"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model = model

    def generate_response(self, prompt, system_prompt=None):
        """调用OpenAI API生成回复"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions", 
                headers=headers, 
                json=payload, 
                timeout=120
            )

            if response.status_code != 200:
                body = response.text
                return f"OpenAI API调用失败: {response.status_code} - {body}"

            result = response.json()
            
            # Extract response from OpenAI format
            if isinstance(result, dict):
                choices = result.get('choices', [])
                if choices and len(choices) > 0:
                    message = choices[0].get('message', {})
                    if isinstance(message, dict) and 'content' in message:
                        return message['content'].strip()
            
            return "OpenAI API响应格式错误"

        except requests.exceptions.ConnectionError:
            return "无法连接到OpenAI API服务，请检查网络连接"
        except Exception as e:
            return f"OpenAI API调用错误: {str(e)}"


class AIClientFactory:
    """AI客户端工厂类"""
    
    @staticmethod
    def create_client(provider, **kwargs):
        """根据提供商创建AI客户端"""
        if provider == "ollama":
            return OllamaClient(
                base_url=kwargs.get('base_url', 'http://localhost:11434'),
                model=kwargs.get('model', 'qwen3:4b')
            )
        elif provider == "openai":
            api_key = kwargs.get('api_key')
            if not api_key:
                raise ValueError("OpenAI API密钥不能为空")
            return OpenAIClient(
                api_key=api_key,
                base_url=kwargs.get('base_url', 'https://api.openai.com/v1'),
                model=kwargs.get('model', 'gpt-3.5-turbo')
            )
        else:
            raise ValueError(f"不支持的AI提供商: {provider}")
