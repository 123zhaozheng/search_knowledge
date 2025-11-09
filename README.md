# Dify 知识库检索增强 API

基于 Dify 的智能知识库检索增强接口,通过 LLM 判断 + 并行检索 + Reranker 重排序,提供高质量的知识库检索服务。

## 🌟 核心特性

- **智能判断**: 使用 LLM 判断问题是否需要检索,避免无效检索
- **多库并行**: 支持同时检索多个知识库,提升检索效率
- **查询优化**: LLM 自动为不同知识库生成最优检索查询
- **高性能**: 异步并行处理,确保快速响应
- **Rerank 增强**: 统一使用 Reranker 模型对结果进行重排序
- **灵活配置**: 支持自定义检索参数(top_k、阈值、权重等)

## 📋 工作流程

```
用户请求
    ↓
1️⃣ LLM 判断是否需要检索
    ↓
   需要? → 否 → 直接返回
    ↓ 是
2️⃣ LLM 生成检索查询 (为每个知识库优化)
    ↓
3️⃣ 并行调用 Dify 知识库检索 API
    ↓
4️⃣ 汇总所有检索结果
    ↓
5️⃣ Reranker 重排序
    ↓
返回 Top-K 结果
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并配置:

```bash
cp .env.example .env
```

编辑 `.env` 文件:

```env
# Dify 配置
DIFY_API_BASE_URL=https://api.dify.ai/v1
DIFY_API_KEY=your-dify-api-key

# LLM 配置 (用于判断)
LLM_API_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=your-llm-api-key
LLM_MODEL=gpt-4-turbo-preview

# Reranker 配置
RERANKER_API_URL=http://your-reranker-service/rerank
RERANKER_API_KEY=your-reranker-api-key
RERANKER_MODEL_NAME=bge-reranker-v2-m3

# 应用配置
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=True

# 检索默认配置
DEFAULT_TOP_K=10
DEFAULT_RERANK_TOP_K=5
DEFAULT_SCORE_THRESHOLD=0.4
DEFAULT_SEMANTIC_WEIGHT=0.7
```

### 3. 启动服务

```bash
python main.py
```

或使用 uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 📖 API 使用

### 接口地址

```
POST /api/v1/retrieve
```

### 请求示例

```json
{
  "datasets": [
    {
      "dataset_id": "dataset-123",
      "description": "产品技术文档知识库,包含API文档、架构设计等"
    },
    {
      "dataset_id": "dataset-456",
      "description": "常见问题FAQ知识库,包含用户常见问题和解答"
    }
  ],
  "dataset_api_key": "your-dataset-api-key",
  "question": "如何使用API进行数据导入?",
  "document": "用户正在查看数据管理模块的文档",
  "top_k": 10,
  "rerank_top_k": 5,
  "score_threshold": 0.4,
  "semantic_weight": 0.7
}
```

### 请求参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| datasets | Array | ✅ | - | 知识库列表,包含 ID 和描述 |
| dataset_api_key | String | ✅ | - | Dify 知识库 API Key |
| question | String | ✅ | - | 用户问题 |
| document | String | ❌ | null | 相关文档内容(可选) |
| top_k | Integer | ❌ | 10 | 每个知识库返回的结果数 |
| rerank_top_k | Integer | ❌ | 5 | Rerank 后返回的最终结果数 |
| score_threshold | Float | ❌ | 0.4 | 相关性分数阈值(0.0-1.0) |
| semantic_weight | Float | ❌ | 0.7 | 混合检索中语义检索的权重 |

### 响应示例

```json
{
  "success": true,
  "need_retrieval": true,
  "retrieval_queries": [
    {
      "dataset_id": "dataset-123",
      "query": "API 数据导入方法"
    },
    {
      "dataset_id": "dataset-456",
      "query": "数据导入常见问题"
    }
  ],
  "segments": [
    {
      "dataset_id": "dataset-123",
      "dataset_name": "产品技术文档",
      "document_id": "doc-001",
      "document_name": "API 使用指南",
      "segment_id": "seg-123",
      "content": "数据导入API的使用方法...",
      "score": 0.95,
      "position": 5,
      "metadata": {}
    }
  ],
  "total_segments": 5,
  "message": "检索成功,返回5个相关文档片段 (耗时1.23秒)"
}
```

### 响应字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| success | Boolean | 请求是否成功 |
| need_retrieval | Boolean | 是否需要检索 |
| retrieval_queries | Array | 执行的检索查询列表 |
| segments | Array | 检索到的文档片段(已排序) |
| total_segments | Integer | 返回的片段总数 |
| message | String | 响应消息 |
| error | String | 错误信息(仅失败时) |

## 🔧 配置说明

### Dify 检索配置

本接口使用以下 Dify 检索参数:

- **检索方法**: `hybrid_search` (混合检索)
- **语义检索权重**: 默认 0.7 (可配置)
- **Reranking**: 在 Dify 层面关闭,使用统一的外部 Reranker
- **Top-K**: 默认 10 (可配置)
- **分数阈值**: 默认 0.4 (可配置)

### Reranker 接口规范

Reranker 服务需要提供以下接口:

**请求格式**:
```json
{
  "model": "bge-reranker-v2-m3",
  "query": "用户问题",
  "documents": ["文档1", "文档2", "..."],
  "top_n": 5,
  "return_documents": true
}
```

**响应格式**:
```json
{
  "results": [
    {
      "index": 0,
      "relevance_score": 0.95,
      "document": "文档内容"
    }
  ]
}
```

## 📂 项目结构

```
dify_knowledge_api/
├── main.py              # FastAPI 主应用
├── config.py            # 配置管理
├── models.py            # Pydantic 数据模型
├── llm_service.py       # LLM 判断服务
├── dify_client.py       # Dify API 客户端
├── rerank_service.py    # Reranker 服务
├── requirements.txt     # 依赖列表
├── .env.example         # 环境变量示例
└── README.md           # 项目文档
```

## 🧪 测试示例

### 使用 curl

```bash
curl -X POST "http://localhost:8000/api/v1/retrieve" \
  -H "Content-Type: application/json" \
  -d '{
    "datasets": [
      {
        "dataset_id": "your-dataset-id",
        "description": "产品文档知识库"
      }
    ],
    "dataset_api_key": "your-api-key",
    "question": "如何重置密码?",
    "top_k": 10,
    "rerank_top_k": 5
  }'
```

### 使用 Python requests

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/retrieve",
    json={
        "datasets": [
            {
                "dataset_id": "your-dataset-id",
                "description": "产品文档知识库"
            }
        ],
        "dataset_api_key": "your-api-key",
        "question": "如何重置密码?",
        "top_k": 10,
        "rerank_top_k": 5
    }
)

print(response.json())
```

## 🎯 性能优化

1. **并行检索**: 多个知识库同时检索,减少总耗时
2. **异步处理**: 全流程使用 async/await,提升并发能力
3. **连接池**: httpx 自动管理连接池
4. **错误容错**: 单个知识库失败不影响其他知识库

## ⚠️ 注意事项

1. 确保 Dify API Key 有访问指定知识库的权限
2. LLM API 需要支持 JSON 格式输出
3. Reranker 服务需要预先部署
4. 建议设置合理的 timeout 时间
5. 生产环境建议关闭 DEBUG 模式

## 📝 常见问题

**Q: LLM 判断失败怎么办?**
A: 系统会自动降级,使用原始问题对所有知识库进行检索。

**Q: Rerank 失败怎么办?**
A: 系统会返回原始检索结果的 Top-K。

**Q: 如何调整检索质量?**
A: 可以调整 `score_threshold`、`semantic_weight` 和 `rerank_top_k` 参数。

**Q: 支持流式返回吗?**
A: 当前版本不支持,因为需要等待 Rerank 完成。

## 📄 License

MIT License

## 👥 贡献

欢迎提交 Issue 和 Pull Request!
