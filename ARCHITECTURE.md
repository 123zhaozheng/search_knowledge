# 📐 项目架构文档

## 🎯 系统概述

Dify知识库检索增强API是一个基于FastAPI构建的智能检索服务,通过整合LLM判断、并行检索和Reranker重排序,为Dify知识库提供高质量的检索能力。

## 🏗️ 架构设计

### 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                          客户端请求                              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI 主应用 (main.py)                    │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  POST /api/v1/retrieve                                    │  │
│  │  - 请求验证                                               │  │
│  │  - 流程编排                                               │  │
│  │  - 错误处理                                               │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────┬──────────────────┬──────────────────┬──────────────────┘
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ LLM Service  │  │ Dify Client  │  │Rerank Service│
│              │  │              │  │              │
│ 判断是否检索  │  │ 并行检索多库  │  │ 结果重排序   │
│ 生成查询语句  │  │ 混合检索策略  │  │ 相关性打分   │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ LLM API      │  │ Dify API     │  │ Reranker API │
│ (OpenAI等)   │  │              │  │ (自部署)     │
└──────────────┘  └──────────────┘  └──────────────┘
```

### 数据流程

```
1. 接收请求
   ├─ 验证参数
   └─ 提取知识库信息和问题

2. LLM判断阶段
   ├─ 构建系统提示词(包含知识库描述)
   ├─ 调用LLM API
   ├─ 解析JSON响应
   └─ 判断是否需要检索
       ├─ 不需要 → 直接返回
       └─ 需要 → 生成检索查询列表

3. 并行检索阶段
   ├─ 为每个查询创建异步任务
   ├─ 并发调用Dify检索API
   │   ├─ 混合检索(hybrid_search)
   │   ├─ 语义权重: 0.7
   │   ├─ Top-K: 10
   │   └─ 分数阈值: 0.4
   ├─ 汇总所有结果
   └─ 合并文档片段

4. Rerank重排序阶段
   ├─ 准备文档内容列表
   ├─ 调用Reranker API
   ├─ 接收相关性分数
   ├─ 按分数重新排序
   └─ 返回Top-K结果

5. 返回响应
   ├─ 构建响应数据
   ├─ 记录日志
   └─ 返回给客户端
```

## 📁 文件结构说明

```
dify_knowledge_api/
│
├── 📄 核心应用文件
│   ├── main.py              # FastAPI主应用,路由定义,请求处理
│   ├── config.py            # 配置管理,环境变量加载
│   └── models.py            # Pydantic数据模型定义
│
├── 🔧 服务模块
│   ├── llm_service.py       # LLM判断服务
│   ├── dify_client.py       # Dify API客户端
│   └── rerank_service.py    # Reranker服务
│
├── ⚙️ 配置文件
│   ├── .env.example         # 环境变量示例
│   ├── requirements.txt     # Python依赖列表
│   └── .gitignore          # Git忽略配置
│
├── 📖 文档
│   ├── README.md           # 项目说明文档
│   ├── QUICKSTART.md       # 快速开始指南
│   └── ARCHITECTURE.md     # 架构文档(本文件)
│
├── 🧪 测试和示例
│   ├── test_api.py         # API测试脚本
│   └── examples.json       # 请求响应示例
│
└── 🚀 启动脚本
    ├── start.sh            # Linux/Mac启动脚本
    └── start.bat           # Windows启动脚本
```

## 🔍 核心模块详解

### 1. main.py - FastAPI主应用

**职责**:
- 定义API路由和端点
- 请求验证和参数处理
- 协调各个服务模块
- 全局异常处理
- 应用生命周期管理

**核心端点**:
- `GET /`: 根路径,返回API信息
- `GET /health`: 健康检查
- `POST /api/v1/retrieve`: 主检索接口

**关键特性**:
- 异步处理,支持高并发
- CORS中间件配置
- 详细的日志输出
- 统一的错误处理

### 2. llm_service.py - LLM判断服务

**职责**:
- 判断问题是否需要检索
- 为每个知识库生成优化的检索查询
- 处理LLM API调用和响应解析

**核心方法**:
- `decide_retrieval()`: 主判断方法
- `_create_system_prompt()`: 构建系统提示词
- `_create_user_prompt()`: 构建用户提示词

**容错机制**:
- API调用失败时降级为默认检索策略
- JSON解析失败时使用原始问题检索

### 3. dify_client.py - Dify检索客户端

**职责**:
- 调用Dify知识库检索API
- 并行处理多个知识库检索
- 结果格式标准化

**核心方法**:
- `retrieve_from_dataset()`: 单库检索
- `batch_retrieve()`: 批量并行检索

**检索配置**:
- 混合检索(hybrid_search)
- 语义权重可配置
- 支持分数阈值过滤

### 4. rerank_service.py - 重排序服务

**职责**:
- 对检索结果进行重排序
- 提升结果相关性
- 支持多查询融合排序

**核心方法**:
- `rerank_segments()`: 基础重排序
- `rerank_with_multiple_queries()`: 多查询重排序

**容错机制**:
- API失败时返回原始排序结果
- 自动处理结果数量少于top_k的情况

### 5. models.py - 数据模型

**定义的模型**:
- `QueryRequest`: 检索请求
- `RetrievalResponse`: 检索响应
- `LLMDecision`: LLM判断结果
- `DocumentSegment`: 文档片段
- `DatasetInfo`: 知识库信息
- 其他辅助模型

**特性**:
- 完整的类型注解
- 字段验证和约束
- 清晰的文档说明

### 6. config.py - 配置管理

**职责**:
- 加载环境变量
- 提供全局配置访问
- 配置验证

**配置分类**:
- Dify配置
- LLM配置
- Reranker配置
- 应用配置
- 检索默认参数

## 🔄 API请求处理流程

### 完整的请求处理步骤

```python
async def retrieve_knowledge(request: QueryRequest):
    # 1. 参数验证(自动,通过Pydantic)

    # 2. LLM判断
    llm_decision = await llm_service.decide_retrieval(
        question=request.question,
        datasets=request.datasets,
        document=request.document
    )

    # 3. 检查是否需要检索
    if not llm_decision.need_retrieval:
        return early_response

    # 4. 并行检索
    all_segments = await dify_client.batch_retrieve(
        retrieval_queries=llm_decision.retrieval_queries,
        api_key=request.dataset_api_key,
        top_k=request.top_k,
        score_threshold=request.score_threshold,
        semantic_weight=request.semantic_weight
    )

    # 5. Rerank重排序
    reranked_segments = await rerank_service.rerank_segments(
        query=rerank_query,
        segments=all_segments,
        top_k=request.rerank_top_k
    )

    # 6. 返回结果
    return RetrievalResponse(...)
```

## ⚡ 性能优化策略

### 1. 异步并发

- 使用 `asyncio` 进行异步IO操作
- 多个知识库检索并行执行
- 非阻塞HTTP请求

### 2. 请求优化

- 复用HTTP连接池(httpx)
- 合理的超时设置(30秒)
- 流式处理大数据

### 3. 错误处理

- 单个知识库失败不影响其他
- 自动降级策略
- 详细的错误日志

### 4. 资源管理

- 自动连接池管理
- 生命周期钩子
- 优雅关闭

## 🔐 安全考虑

### 1. API密钥管理

- 环境变量存储
- 不在代码中硬编码
- .env文件不提交到Git

### 2. 请求验证

- Pydantic模型验证
- 参数范围限制
- 类型检查

### 3. 错误信息

- 避免泄露敏感信息
- 统一错误格式
- 适当的HTTP状态码

## 📊 监控和日志

### 日志输出

每个步骤都有详细的日志:

```
[Step 1] LLM判断是否需要检索...
[Step 1] 判断结果: need_retrieval=True
[Step 2] 并行检索知识库...
[Step 2] 检索到 15 个文档片段
[Step 3] 使用Reranker重排序...
[Step 3] Rerank完成,返回 5 个片段
[完成] 总耗时: 1.23秒
```

### 性能指标

- 总处理时间
- 各阶段耗时
- 检索结果数量
- 成功/失败状态

## 🔧 扩展点

### 1. 支持更多LLM

修改 `llm_service.py`,适配不同的API格式

### 2. 自定义检索策略

修改 `dify_client.py`,调整检索参数

### 3. 多种Rerank方式

扩展 `rerank_service.py`,支持不同的重排序算法

### 4. 缓存机制

添加Redis缓存,减少重复查询

### 5. 限流和配额

添加中间件,控制请求频率

## 📝 设计原则

1. **单一职责**: 每个模块专注一个功能
2. **依赖注入**: 通过配置管理依赖
3. **异步优先**: 充分利用异步IO
4. **容错设计**: 优雅的降级策略
5. **可观测性**: 详细的日志和指标

## 🎯 未来规划

- [ ] 添加缓存层(Redis)
- [ ] 支持流式返回
- [ ] 添加监控指标(Prometheus)
- [ ] 支持更多Rerank模型
- [ ] 优化提示词工程
- [ ] 添加A/B测试能力
- [ ] 支持结果解释功能

---

**文档版本**: 1.0.0
**最后更新**: 2024
