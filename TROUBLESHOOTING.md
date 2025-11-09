# 🔧 Dify接口卡死问题诊断指南

## 问题现象

程序在执行到 Dify 知识库检索时卡住，返回 0 个文档片段。

## 🎯 快速诊断步骤

### 1️⃣ 使用独立测试脚本

我已经创建了一个详细的 Dify API 测试脚本，可以帮助你快速定位问题。

**运行测试脚本:**

```bash
python test_dify_api.py
```

**配置测试脚本:**

编辑 `test_dify_api.py` 文件顶部的配置:

```python
# ========== 配置区 ==========
DIFY_API_BASE_URL = "https://api.dify.ai/v1"  # 你的 Dify API 地址
DIFY_DATASET_ID = "0b50716f-c66d-4c78-b088-2198fc12ae85"  # 你的知识库ID
DIFY_API_KEY = "dataset-xxxxxxxxxxxx"  # 你的 API Key
TEST_QUERY = "python 逻辑错误"  # 测试查询
```

### 2️⃣ 查看详细日志

我已经改进了 [dify_client.py](dify_client.py:1)，现在会输出详细的调试信息:

```
[Dify] 开始检索知识库: 0b50716f-c66d-4c78-b088-2198fc12ae85
[Dify] URL: https://api.dify.ai/v1/datasets/0b50716f-c66d-4c78-b088-2198fc12ae85/retrieve
[Dify] 查询: python 逻辑错误
[Dify] 参数: top_k=10, threshold=0.4, weight=0.7
[Dify] 正在连接 Dify API...
[Dify] 发送 POST 请求...
[Dify] 收到响应 (耗时 1.23秒), 状态码: 200
[Dify] 响应数据结构: ['data', 'doc_id']
[Dify] 检索到 5 个文档片段
[Dify] 成功转换 5 个片段
```

如果卡住，你会看到具体在哪个步骤卡住了。

## 🔍 常见问题和解决方案

### 问题1: 连接超时

**症状:**
```
[Dify] 正在连接 Dify API...
[Dify] ❌ 连接超时: ...
```

**可能原因:**
1. API 地址配置错误
2. 网络连接问题
3. 防火墙阻止连接
4. Dify 服务未启动

**解决方法:**
```bash
# 测试网络连通性
ping api.dify.ai

# 如果是私有部署，检查服务是否启动
curl https://your-dify-url/v1
```

### 问题2: 读取超时

**症状:**
```
[Dify] 发送 POST 请求...
(等待很久...)
[Dify] ❌ 读取超时: ...
```

**可能原因:**
1. Dify 服务响应缓慢
2. 知识库数据量过大
3. 服务器资源不足

**解决方法:**
- 增加超时时间 (在 [dify_client.py](dify_client.py:67) 中修改 `read` 参数)
- 减少 `top_k` 参数
- 检查 Dify 服务器性能

### 问题3: HTTP 401 错误

**症状:**
```
[Dify] ❌ HTTP错误
[Dify]    状态码: 401
[Dify]    可能原因: API Key 错误或过期
```

**解决方法:**
1. 在 Dify 控制台重新生成 API Key
2. 确认 `.env` 文件中的 `DIFY_API_KEY` 正确
3. 注意不要混淆 Dataset API Key 和其他类型的 Key

### 问题4: HTTP 404 错误

**症状:**
```
[Dify] ❌ HTTP错误
[Dify]    状态码: 404
[Dify]    可能原因: Dataset ID 不存在或URL路径错误
```

**解决方法:**
1. 检查 Dataset ID 是否正确
2. 在 Dify 控制台确认知识库存在
3. 确认 API Base URL 格式: `https://api.dify.ai/v1` (注意 `/v1`)

### 问题5: 返回 0 个文档片段

**症状:**
```
[Dify] 收到响应 (耗时 1.23秒), 状态码: 200
[Dify] 检索到 0 个文档片段
```

**可能原因:**
1. 知识库为空
2. 查询词没有匹配的内容
3. `score_threshold` 设置过高
4. 文档还在向量化处理中

**解决方法:**

1. **检查知识库状态:**
   - 登录 Dify 控制台
   - 确认知识库中有文档
   - 确认文档已完成向量化（状态显示为"已完成"）

2. **调整检索参数:**

编辑你的请求，降低阈值:

```python
{
    "score_threshold": 0.1,  # 降低到 0.1
    "top_k": 20,             # 增加返回数量
}
```

3. **测试简单查询:**

使用更通用的查询词测试:

```python
TEST_QUERY = "python"  # 简单的查询
```

## 📝 配置检查清单

运行前请确认:

- [ ] Dify 服务正常运行
- [ ] 知识库已创建并包含文档
- [ ] 文档已完成向量化
- [ ] API Key 正确且有效
- [ ] Dataset ID 正确
- [ ] 网络连接正常
- [ ] 防火墙允许访问 Dify API

## 🔧 调试步骤

### 第1步: 运行独立测试

```bash
# 编辑配置
nano test_dify_api.py

# 运行测试
python test_dify_api.py
```

### 第2步: 查看详细日志

测试脚本会输出:
- 请求 URL
- 请求参数
- 响应状态
- 错误详情
- 可能的原因

### 第3步: 根据错误信息修复

根据测试脚本的输出，参考上面的"常见问题和解决方案"进行修复。

### 第4步: 验证修复

修复后重新运行主程序:

```bash
python main.py
```

## 💡 临时解决方案

如果问题依然存在，可以先绕过 LLM 判断，直接检索:

修改 [main.py](main.py:1)，添加测试代码:

```python
# 临时测试: 直接调用 Dify 检索，不经过 LLM 判断
from dify_client import dify_client
from models import RetrievalQuery

async def test_direct_retrieve():
    queries = [
        RetrievalQuery(
            dataset_id="你的知识库ID",
            query="测试查询"
        )
    ]

    result = await dify_client.batch_retrieve(
        retrieval_queries=queries,
        api_key="你的API Key",
        top_k=10,
        score_threshold=0.1,  # 降低阈值
        semantic_weight=0.7
    )

    print(f"检索结果: {len(result)} 个片段")
    for seg in result:
        print(f"- {seg.content[:100]}...")

# 在 main() 函数中调用
# await test_direct_retrieve()
```

## 📞 获取更多帮助

如果以上方法都无法解决问题:

1. 运行 `test_dify_api.py` 并保存完整输出
2. 检查 Dify 官方文档: https://docs.dify.ai/
3. 查看 Dify 服务日志
4. 联系 Dify 技术支持

## 🎯 成功标志

测试成功的输出应该类似:

```
✅ 连接成功!
✅ 请求成功!
📊 检索结果统计:
   返回记录数: 5

📄 文档片段详情:
   片段 1:
      文档名: xxx.pdf
      分数: 0.85
      内容: ...
```

修复后，主程序的输出应该是:

```
[Step 2] 并行检索知识库...
[Dify] 开始检索知识库: ...
[Dify] 收到响应 (耗时 1.23秒), 状态码: 200
[Dify] 检索到 5 个文档片段
[Step 2] 检索到 5 个文档片段
[Step 3] 使用Reranker重排序...
```

---

**注意**: 如果使用的是私有部署的 Dify，请确保版本兼容性和 API 接口一致性。
