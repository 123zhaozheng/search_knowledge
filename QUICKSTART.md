# 🚀 快速开始指南

## 📋 前置要求

1. Python 3.8+
2. Dify 账号和 API Key
3. LLM API 访问权限 (OpenAI、Azure OpenAI 或其他兼容服务)
4. Reranker 服务部署完成

## ⚡ 5分钟快速启动

### 1️⃣ 克隆或下载项目

```bash
cd dify_konwledge_api
```

### 2️⃣ 创建虚拟环境 (推荐)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ 安装依赖

```bash
pip install -r requirements.txt
```

### 4️⃣ 配置环境变量

```bash
# 复制示例配置
cp .env.example .env

# 编辑 .env 文件,填入你的配置
# Windows 可以使用: notepad .env
# Linux/Mac 可以使用: nano .env 或 vim .env
```

**必须配置的项目**:

```env
# Dify 配置
DIFY_API_BASE_URL=https://api.dify.ai/v1
DIFY_API_KEY=your-dify-api-key-here

# LLM 配置
LLM_API_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=your-openai-api-key-here
LLM_MODEL=gpt-4-turbo-preview

# Reranker 配置
RERANKER_API_URL=http://your-reranker-url/rerank
RERANKER_API_KEY=your-reranker-key
RERANKER_MODEL_NAME=bge-reranker-v2-m3
```

### 5️⃣ 启动服务

**方式 1: 直接运行**

```bash
python main.py
```

**方式 2: 使用启动脚本**

```bash
# Windows
start.bat

# Linux/Mac
chmod +x start.sh
./start.sh
```

**方式 3: 使用 uvicorn**

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 6️⃣ 验证服务

打开浏览器访问:

- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health
- **根路径**: http://localhost:8000/

## 🧪 测试 API

### 使用测试脚本

1. 编辑 `test_api.py`,填入你的知识库配置:

```python
"dataset_id": "your-dataset-id",  # 替换为你的知识库ID
"dataset_api_key": "your-api-key", # 替换为你的API Key
```

2. 运行测试:

```bash
python test_api.py
```

### 使用 curl

```bash
curl -X POST "http://localhost:8000/api/v1/retrieve" \
  -H "Content-Type: application/json" \
  -d '{
    "datasets": [
      {
        "dataset_id": "your-dataset-id",
        "description": "你的知识库描述"
      }
    ],
    "dataset_api_key": "your-dataset-api-key",
    "question": "你的问题",
    "top_k": 10,
    "rerank_top_k": 5
  }'
```

### 使用 API 文档界面

1. 访问 http://localhost:8000/docs
2. 找到 `POST /api/v1/retrieve` 接口
3. 点击 "Try it out"
4. 填写请求参数
5. 点击 "Execute"

## 📊 API 响应示例

### 成功响应

```json
{
  "success": true,
  "need_retrieval": true,
  "retrieval_queries": [
    {
      "dataset_id": "dataset-123",
      "query": "优化后的检索查询"
    }
  ],
  "segments": [
    {
      "dataset_id": "dataset-123",
      "content": "文档内容...",
      "score": 0.95,
      ...
    }
  ],
  "total_segments": 5,
  "message": "检索成功,返回5个相关文档片段 (耗时1.23秒)"
}
```

### 不需要检索

```json
{
  "success": true,
  "need_retrieval": false,
  "retrieval_queries": [],
  "segments": [],
  "total_segments": 0,
  "message": "根据LLM判断,此问题不需要检索知识库"
}
```

## 🔧 常见问题

### 1. 启动失败: ModuleNotFoundError

**解决方案**: 确保已安装所有依赖

```bash
pip install -r requirements.txt
```

### 2. LLM API 调用失败

**检查项**:
- API Key 是否正确
- API Base URL 是否正确
- 网络连接是否正常
- 模型名称是否正确

### 3. Dify 检索失败

**检查项**:
- Dataset ID 是否正确
- Dataset API Key 是否正确
- 知识库是否已创建并包含内容
- API Key 是否有权限访问该知识库

### 4. Reranker 调用失败

**检查项**:
- Reranker 服务是否已启动
- URL 是否正确
- API Key 是否正确
- 模型名称是否正确

### 5. 服务启动正常但无法访问

**检查项**:
- 端口 8000 是否被占用
- 防火墙设置
- 尝试更换端口 (修改 .env 中的 APP_PORT)

## 🎯 下一步

1. 阅读完整 [README.md](README.md) 了解详细功能
2. 查看 [examples.json](examples.json) 了解更多示例
3. 根据需求调整配置参数
4. 集成到你的应用中

## 📞 获取帮助

- 查看项目 README.md
- 检查 examples.json 中的示例
- 查看 API 文档: http://localhost:8000/docs

## 🎉 开始使用

现在你的 Dify 知识库检索增强 API 已经启动成功！

访问 http://localhost:8000/docs 开始探索 API 功能。
