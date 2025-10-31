# 远程API配置指南

本项目现在支持多种AI服务提供商，包括本地Ollama和远程API服务。

## 支持的AI提供商

### 1. Ollama (默认)
- 本地部署的AI模型
- 无需API密钥
- 默认配置

### 2. OpenAI API
- 远程API服务
- 需要API密钥
- 支持GPT系列模型

## 配置方法

### 方法1: 修改配置文件

编辑 `config/settings.py` 文件中的配置：

```python
@dataclass
class AppConfig:
    # AI 提供商配置
    AI_PROVIDER: str = "openai"  # 改为 "openai" 使用OpenAI
    
    # Ollama 配置
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen3:4b"
    
    # OpenAI 配置
    OPENAI_API_KEY: str = "your-api-key-here"  # 填入你的OpenAI API密钥
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-3.5-turbo"  # 或其他支持的模型
```

### 方法2: 环境变量配置

你也可以通过环境变量配置：

```bash
# Windows PowerShell
$env:AI_PROVIDER="openai"
$env:OPENAI_API_KEY="your-api-key-here"
$env:OPENAI_MODEL="gpt-4"

# Windows CMD
set AI_PROVIDER=openai
set OPENAI_API_KEY=your-api-key-here
set OPENAI_MODEL=gpt-4

# Linux/macOS
export AI_PROVIDER=openai
export OPENAI_API_KEY=your-api-key-here
export OPENAI_MODEL=gpt-4
```

## 获取OpenAI API密钥

1. 访问 [OpenAI平台](https://platform.openai.com/)
2. 注册或登录账户
3. 进入 API Keys 页面
4. 点击 "Create new secret key"
5. 复制生成的API密钥

## 支持的OpenAI模型

- `gpt-3.5-turbo` (推荐，性价比高)
- `gpt-4`
- `gpt-4-turbo`
- `gpt-4o`

## 自定义API端点

如果你使用其他兼容OpenAI API的服务，可以修改 `OPENAI_BASE_URL`：

```python
# 例如使用Azure OpenAI
OPENAI_BASE_URL: str = "https://your-resource.openai.azure.com/openai/deployments/your-deployment"

# 或使用其他兼容服务
OPENAI_BASE_URL: str = "https://api.example.com/v1"
```

## 测试配置

运行测试脚本验证配置：

```bash
python test_remote_api.py
```

## 故障排除

### OpenAI API连接问题

1. **检查API密钥**: 确保API密钥正确且未过期
2. **检查网络连接**: 确保可以访问OpenAI API
3. **检查配额**: 确保账户有足够的API调用额度
4. **检查模型可用性**: 确保使用的模型在你的账户中可用

### Ollama连接问题

1. **检查Ollama服务**: 确保Ollama正在运行
2. **检查模型**: 确保指定的模型已下载
3. **检查端口**: 确保Ollama在默认端口11434运行

### 错误信息

- `无法连接到OpenAI API服务`: 网络连接问题或API密钥错误
- `OpenAI API调用失败: 401`: API密钥无效
- `OpenAI API调用失败: 429`: 请求频率过高
- `无法连接到Ollama服务`: Ollama未运行或端口被占用

## 性能建议

- **Ollama**: 适合本地使用，隐私性好，但需要本地GPU资源
- **OpenAI**: 适合需要高质量回答的场景，但需要网络连接和API费用

## 扩展其他提供商

要添加新的AI提供商，需要：

1. 在 `core/ai_client.py` 中创建新的客户端类，继承 `AIClient`
2. 在 `AIClientFactory` 中添加创建逻辑
3. 在 `config/settings.py` 中添加相应的配置项
4. 在 `main.py` 的 `create_ai_client` 方法中添加支持
