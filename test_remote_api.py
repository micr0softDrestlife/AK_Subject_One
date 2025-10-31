#!/usr/bin/env python3
"""
测试远程API支持的脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.ai_client import AIClientFactory
from config.settings import AppConfig

def test_ollama_client():
    """测试Ollama客户端"""
    print("=== 测试Ollama客户端 ===")
    try:
        client = AIClientFactory.create_client(
            provider='ollama',
            base_url='http://localhost:11434',
            model='qwen3:4b'
        )
        response = client.generate_response("你好，请简单介绍一下你自己")
        print(f"Ollama响应: {response}")
        print("✅ Ollama客户端测试通过")
    except Exception as e:
        print(f"❌ Ollama客户端测试失败: {e}")

def test_openai_client():
    """测试OpenAI客户端"""
    print("\n=== 测试OpenAI客户端 ===")
    config = AppConfig()
    if not config.OPENAI_API_KEY:
        print("⚠️ OpenAI API密钥未设置，跳过测试")
        return
    
    try:
        client = AIClientFactory.create_client(
            provider='openai',
            api_key=config.OPENAI_API_KEY,
            base_url=config.OPENAI_BASE_URL,
            model=config.OPENAI_MODEL
        )
        response = client.generate_response("你好，请简单介绍一下你自己")
        print(f"OpenAI响应: {response}")
        print("✅ OpenAI客户端测试通过")
    except Exception as e:
        print(f"❌ OpenAI客户端测试失败: {e}")

def test_config_loading():
    """测试配置加载"""
    print("\n=== 测试配置加载 ===")
    try:
        config = AppConfig()
        print(f"AI提供商: {config.AI_PROVIDER}")
        print(f"Ollama URL: {config.OLLAMA_BASE_URL}")
        print(f"Ollama模型: {config.OLLAMA_MODEL}")
        print(f"OpenAI模型: {config.OPENAI_MODEL}")
        print("✅ 配置加载测试通过")
    except Exception as e:
        print(f"❌ 配置加载测试失败: {e}")

if __name__ == "__main__":
    print("开始测试远程API支持...")
    test_config_loading()
    test_ollama_client()
    test_openai_client()
    print("\n测试完成！")
