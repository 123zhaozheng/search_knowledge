# Dify 知识库检索 API - Postman 测试配置

## 📋 完整请求信息

### 1. 基本信息

**Method:** `POST`

**URL:**
```
https://api.dify.ai/v1/datasets/{dataset_id}/retrieve
```

将 `{dataset_id}` 替换为你的知识库ID，例如:
```
https://api.dify.ai/v1/datasets/0b50716f-c66d-4c78-b088-2198fc12ae85/retrieve
```

### 2. Headers

```json
{
  "Authorization": "Bearer dataset-xxxxxxxxxxxx",
  "Content-Type": "application/json"
}
```

**注意:**
- `Authorization` 的值是 `Bearer ` + 你的知识库 API Key
- API Key 通常以 `dataset-` 开头

### 3. Request Body (当前代码使用的配置)

```json
{
  "query": "python 逻辑错误",
  "retrieval_model": {
    "search_method": "hybrid_search",
    "reranking_enable": false,
    "weights": 0.7,
    "top_k": 10,
    "score_threshold_enabled": true,
    "score_threshold": 0.4
  }
}
```

### 4. Body 参数说明

| 参数 | 类型 | 必填 | 说明 | 当前值 |
|------|------|------|------|--------|
| query | string | ✅ | 检索查询语句 | "python 逻辑错误" |
| retrieval_model | object | ❌ | 检索配置 | - |
| └─ search_method | string | ✅ | 检索方法 | "hybrid_search" |
| └─ reranking_enable | boolean | ❌ | 是否启用Rerank | false |
| └─ weights | float | ❌ | 语义检索权重 | 0.7 |
| └─ top_k | integer | ❌ | 返回结果数量 | 10 |
| └─ score_threshold_enabled | boolean | ❌ | 是否启用分数阈值 | true |
| └─ score_threshold | float | ❌ | 分数阈值 | 0.4 |

---

## 🧪 Postman 测试步骤

### 步骤1: 创建新请求

1. 打开 Postman
2. 点击 "New" → "HTTP Request"
3. 选择 `POST` 方法

### 步骤2: 设置 URL

```
https://api.dify.ai/v1/datasets/0b50716f-c66d-4c78-b088-2198fc12ae85/retrieve
```

**替换你的知识库ID！**

### 步骤3: 设置 Headers

点击 "Headers" 标签页，添加：

| Key | Value |
|-----|-------|
| Authorization | Bearer dataset-你的API-Key |
| Content-Type | application/json |

### 步骤4: 设置 Body

1. 点击 "Body" 标签页
2. 选择 "raw"
3. 选择格式为 "JSON"
4. 粘贴以下内容:

**方案A: 使用当前配置 (可能因为阈值太高返回0条)**

```json
{
  "query": "python 逻辑错误",
  "retrieval_model": {
    "search_method": "hybrid_search",
    "reranking_enable": false,
    "weights": 0.7,
    "top_k": 10,
    "score_threshold_enabled": true,
    "score_threshold": 0.4
  }
}
```

**方案B: 降低阈值测试 (推荐先试这个)**

```json
{
  "query": "python",
  "retrieval_model": {
    "search_method": "hybrid_search",
    "reranking_enable": false,
    "weights": 0.7,
    "top_k": 10,
    "score_threshold_enabled": true,
    "score_threshold": 0.1
  }
}
```

**方案C: 最简单配置 (只传query，其他用默认)**

```json
{
  "query": "python"
}
```

**方案D: 语义检索 (semantic_search)**

```json
{
  "query": "python 逻辑错误",
  "retrieval_model": {
    "search_method": "semantic_search",
    "top_k": 10,
    "score_threshold_enabled": false
  }
}
```

### 步骤5: 发送请求

点击 "Send" 按钮

---

## 📊 预期响应

### 成功响应 (200 OK)

```json
{
  "data": {
    "records": [
      {
        "id": "segment-xxx",
        "content": "文档内容...",
        "score": 0.85,
        "document_id": "doc-xxx",
        "document_name": "文件名.pdf",
        "dataset_id": "0b50716f-c66d-4c78-b088-2198fc12ae85",
        "dataset_name": "知识库名称",
        "position": 1,
        "metadata": {}
      }
    ]
  },
  "doc_id": "xxx"
}
```

### 返回0条记录

```json
{
  "data": {
    "records": []
  },
  "doc_id": "xxx"
}
```

**可能原因:**
1. 知识库为空
2. 查询词不匹配
3. score_threshold 太高 (0.4)
4. 文档未完成向量化

---

## 🔍 排查建议

### 测试1: 检查知识库是否有数据

使用最简单的查询:

```json
{
  "query": "的"
}
```

如果还是返回空，说明知识库可能真的没有数据。

### 测试2: 降低阈值

```json
{
  "query": "python",
  "retrieval_model": {
    "search_method": "hybrid_search",
    "reranking_enable": false,
    "weights": 0.7,
    "top_k": 20,
    "score_threshold_enabled": true,
    "score_threshold": 0.01
  }
}
```

### 测试3: 尝试关闭阈值

```json
{
  "query": "python",
  "retrieval_model": {
    "search_method": "semantic_search",
    "top_k": 20,
    "score_threshold_enabled": false
  }
}
```

### 测试4: 使用全文检索

```json
{
  "query": "python",
  "retrieval_model": {
    "search_method": "full_text_search",
    "top_k": 10
  }
}
```

---

## ❌ 常见错误响应

### 401 Unauthorized

```json
{
  "code": "unauthorized",
  "message": "Invalid API key"
}
```

**原因:** API Key 错误或过期

### 404 Not Found

```json
{
  "code": "not_found",
  "message": "Dataset not found"
}
```

**原因:** Dataset ID 不存在

### 403 Forbidden

```json
{
  "code": "forbidden",
  "message": "Access denied"
}
```

**原因:** API Key 无权限访问此知识库

---

## 📝 Postman Collection (可导入)

将以下内容保存为 `dify_test.json`，然后在 Postman 中导入:

```json
{
  "info": {
    "name": "Dify Knowledge Base API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Retrieve - Current Config",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer dataset-你的API-Key"
          },
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"query\": \"python 逻辑错误\",\n  \"retrieval_model\": {\n    \"search_method\": \"hybrid_search\",\n    \"reranking_enable\": false,\n    \"weights\": 0.7,\n    \"top_k\": 10,\n    \"score_threshold_enabled\": true,\n    \"score_threshold\": 0.4\n  }\n}"
        },
        "url": {
          "raw": "https://api.dify.ai/v1/datasets/0b50716f-c66d-4c78-b088-2198fc12ae85/retrieve",
          "protocol": "https",
          "host": ["api", "dify", "ai"],
          "path": ["v1", "datasets", "0b50716f-c66d-4c78-b088-2198fc12ae85", "retrieve"]
        }
      }
    },
    {
      "name": "Retrieve - Low Threshold",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer dataset-你的API-Key"
          },
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"query\": \"python\",\n  \"retrieval_model\": {\n    \"search_method\": \"hybrid_search\",\n    \"reranking_enable\": false,\n    \"weights\": 0.7,\n    \"top_k\": 10,\n    \"score_threshold_enabled\": true,\n    \"score_threshold\": 0.1\n  }\n}"
        },
        "url": {
          "raw": "https://api.dify.ai/v1/datasets/0b50716f-c66d-4c78-b088-2198fc12ae85/retrieve",
          "protocol": "https",
          "host": ["api", "dify", "ai"],
          "path": ["v1", "datasets", "0b50716f-c66d-4c78-b088-2198fc12ae85", "retrieve"]
        }
      }
    },
    {
      "name": "Retrieve - Simple",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer dataset-你的API-Key"
          },
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"query\": \"python\"\n}"
        },
        "url": {
          "raw": "https://api.dify.ai/v1/datasets/0b50716f-c66d-4c78-b088-2198fc12ae85/retrieve",
          "protocol": "https",
          "host": ["api", "dify", "ai"],
          "path": ["v1", "datasets", "0b50716f-c66d-4c78-b088-2198fc12ae85", "retrieve"]
        }
      }
    }
  ]
}
```

---

## 💡 关键检查点

在 Postman 测试时，请特别注意:

1. ✅ **API Key 格式**: 必须是 `Bearer ` + API Key (注意Bearer后面有个空格)
2. ✅ **Dataset ID**: 确保是正确的知识库ID
3. ✅ **知识库状态**: 在 Dify 控制台确认知识库有文档且已向量化
4. ✅ **查询词**: 先用简单的通用词测试，如 "python"、"的"
5. ✅ **阈值设置**: 0.4 偏高，建议先降到 0.1 或关闭

---

**测试后请告诉我结果，我可以帮你分析具体问题！** 🔍
