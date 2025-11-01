#  Author: micr0softDrestlife
"""AI client adapters.

This module provides a small adapter/factory so the application can use different
local or remote LLM providers (e.g. Ollama, Qianwen) via a common interface.

Implemented:
 - OllamaClient (existing behavior preserved)
 - QianwenClient (basic HTTP adapter; API shape may require adjustment to your
   Qianwen deployment — see docstring and AppConfig fields in config/settings.py)

Use get_ai_client(config) to obtain a client instance appropriate to
`config.AI_PROVIDER`.
"""

from typing import Optional
import requests


class BaseAIClient:
    """Minimal interface for AI clients."""

    def generate_response(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        raise NotImplementedError()


class OllamaClient(BaseAIClient):
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "qwen2.5-coder:7b"):
        self.base_url = base_url.rstrip('/') if base_url else base_url
        self.model = model

    def generate_response(self, prompt, system_prompt=None):
        """调用Ollama生成回复。保持原来宽容的解析逻辑以处理不同 Ollama 版本的返回形状。"""
        try:
            url = f"{self.base_url}/api/generate"

            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            }

            if system_prompt:
                payload["system"] = system_prompt

            response = requests.post(url, json=payload, timeout=120)

            if response.status_code != 200:
                body = response.text
                return f"API调用失败: {response.status_code} - {body}"

            result = response.json()

            if isinstance(result, dict):
                if 'response' in result and isinstance(result['response'], str):
                    return result['response']

                outputs = result.get('outputs') or result.get('result')
                if isinstance(outputs, list):
                    parts = []
                    for out in outputs:
                        if isinstance(out, dict):
                            for key in ('content', 'text', 'message'):
                                if key in out and isinstance(out[key], str):
                                    parts.append(out[key])
                                    break
                        elif isinstance(out, str):
                            parts.append(out)
                    if parts:
                        return '\n'.join(parts)

            return response.text

        except requests.exceptions.ConnectionError:
            return "无法连接到Ollama服务，请确保Ollama正在运行"
        except Exception as e:
            return f"AI调用错误: {str(e)}"


class OpenAIClient(BaseAIClient):
    """Adapter for OpenAI-compatible Chat completions API (and similar vendors).

    Expects a base_url pointing to the provider's REST API root (e.g. https://api.openai.com/v1)
    and an API key. Uses the /chat/completions endpoint and returns the first choice
    message content when available.
    """

    def __init__(self, api_key: Optional[str], base_url: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key
        self.base_url = (base_url.rstrip('/') if base_url else None)
        self.model = model

    def generate_response(self, prompt, system_prompt=None):
        if not self.api_key:
            return "OpenAI API key 未配置"
        base = self.base_url or 'https://api.openai.com/v1'
        b = base.rstrip('/')
        # If base already contains '/v1' use base+'/chat/completions', otherwise use base+'/v1/chat/completions'
        if b.endswith('/v1') or '/v1/' in b or b.endswith('/v1'):
            url = f"{b}/chat/completions"
        else:
            url = f"{b}/v1/chat/completions"

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        messages.append({'role': 'user', 'content': prompt})

        payload = {
            'model': self.model or 'gpt-3.5-turbo',
            'messages': messages,
            'temperature': 0.7,
            'max_tokens': 1000,
        }

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=120)
            if resp.status_code != 200:
                return f"OpenAI API 调用失败: {resp.status_code} - {resp.text}"

            data = resp.json()
            if isinstance(data, dict):
                choices = data.get('choices') or []
                if choices and isinstance(choices, list):
                    first = choices[0]
                    if isinstance(first, dict):
                        message = first.get('message') or first.get('text')
                        if isinstance(message, dict) and 'content' in message:
                            return message['content'].strip()
                        if isinstance(message, str):
                            return message.strip()

            return resp.text

        except requests.exceptions.ConnectionError:
            return "无法连接到 OpenAI 服务"
        except Exception as e:
            return f"OpenAI 调用错误: {str(e)}"


def get_ai_client(config) -> BaseAIClient:
    """Factory: return an AI client instance based on `config.AI_PROVIDER`.

    Expects config to have attributes used in `config/settings.AppConfig`.
    """
    provider = getattr(config, 'AI_PROVIDER', 'ollama')
    provider = (provider or 'ollama').lower()

    if provider == 'ollama':
        base = getattr(config, 'OLLAMA_BASE_URL', 'http://localhost:11434')
        model = getattr(config, 'OLLAMA_MODEL', None)
        return OllamaClient(base_url=base, model=model)

    if provider in ('qianwen', 'qw'):
        url = getattr(config, 'QIANWEN_API_URL', None)
        key = getattr(config, 'QIANWEN_API_KEY', None)
        model = getattr(config, 'QIANWEN_MODEL', None)
        return OpenAIClient(api_key=key, base_url=url, model=model)

    if provider in ('openai', 'oa'):
        key = getattr(config, 'OPENAI_API_KEY', None)
        base = getattr(config, 'OPENAI_BASE_URL', None)
        model = getattr(config, 'OPENAI_MODEL', None)
        return OpenAIClient(api_key=key, base_url=base, model=model)

    if provider in ('deepseek', 'ds'):
        # Deepseek is OpenAI-compatible; prefer using the OpenAIClient wrapper so
        # we call the /v1/chat/completions endpoint with the provided base URL.
        key = getattr(config, 'DEEPSEEK_API_KEY', None)
        base = getattr(config, 'DEEPSEEK_API_URL', None)
        model = getattr(config, 'DEEPSEEK_MODEL', None)
        return OpenAIClient(api_key=key, base_url=base, model=model)

    # Unknown provider: fallback to OllamaClient for compatibility
    base = getattr(config, 'OLLAMA_BASE_URL', 'http://localhost:11434')
    model = getattr(config, 'OLLAMA_MODEL', None)
    return OllamaClient(base_url=base, model=model)