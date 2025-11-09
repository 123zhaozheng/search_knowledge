"""
Dify 知识库接口测试脚本
用于独立测试 Dify API 的连通性和功能
"""

import asyncio
import httpx
import json
import time
from typing import Dict, Any


# ========== 配置区 ==========
# 请在这里填写你的配置
DIFY_API_BASE_URL = "https://api.dify.ai/v1"  # 或你的私有部署地址
DIFY_DATASET_ID = "your-dataset-id"  # 你的知识库ID
DIFY_API_KEY = "your-api-key"  # 你的API Key

# 测试查询
TEST_QUERY = "测试查询"

# 检索参数
RETRIEVAL_PARAMS = {
    "search_method": "hybrid_search",
    "reranking_enable": False,
    "weights": 0.7,
    "top_k": 10,
    "score_threshold_enabled": True,
    "score_threshold": 0.4
}
# ===========================


async def test_dify_retrieve_detailed():
    """详细测试 Dify 知识库检索接口"""

    print("\n" + "="*70)
    print("🔍 Dify 知识库接口详细测试")
    print("="*70)

    # 构建请求
    url = f"{DIFY_API_BASE_URL}/datasets/{DIFY_DATASET_ID}/retrieve"

    payload = {
        "query": TEST_QUERY,
        "retrieval_model": RETRIEVAL_PARAMS
    }

    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json"
    }

    print(f"\n📋 测试配置:")
    print(f"   API Base URL: {DIFY_API_BASE_URL}")
    print(f"   Dataset ID: {DIFY_DATASET_ID}")
    print(f"   API Key: {DIFY_API_KEY[:10]}...{DIFY_API_KEY[-4:]}" if len(DIFY_API_KEY) > 14 else f"   API Key: {DIFY_API_KEY}")
    print(f"   Test Query: {TEST_QUERY}")

    print(f"\n🌐 请求信息:")
    print(f"   URL: {url}")
    print(f"   Method: POST")
    print(f"   Headers: {json.dumps(headers, indent=6)}")
    print(f"   Payload: {json.dumps(payload, indent=6, ensure_ascii=False)}")

    print(f"\n⏳ 发送请求...")
    start_time = time.time()

    try:
        # 创建HTTP客户端，设置详细的超时配置
        timeout = httpx.Timeout(
            connect=10.0,  # 连接超时
            read=30.0,     # 读取超时
            write=10.0,    # 写入超时
            pool=10.0      # 连接池超时
        )

        async with httpx.AsyncClient(timeout=timeout) as client:
            print(f"   正在连接到 {url}...")

            response = await client.post(
                url,
                json=payload,
                headers=headers
            )

            elapsed_time = time.time() - start_time

            print(f"\n✅ 收到响应 (耗时: {elapsed_time:.2f}秒)")
            print(f"   状态码: {response.status_code}")
            print(f"   响应头: {json.dumps(dict(response.headers), indent=6)}")

            # 打印响应体
            try:
                response_json = response.json()
                print(f"\n📦 响应数据:")
                print(json.dumps(response_json, indent=3, ensure_ascii=False))

                # 分析响应
                if response.status_code == 200:
                    print(f"\n✅ 请求成功!")

                    # 检查数据结构
                    if "data" in response_json:
                        data = response_json["data"]
                        records = data.get("records", [])

                        print(f"\n📊 检索结果统计:")
                        print(f"   返回记录数: {len(records)}")

                        if records:
                            print(f"\n📄 文档片段详情:")
                            for i, record in enumerate(records, 1):
                                print(f"\n   片段 {i}:")
                                print(f"      ID: {record.get('id', 'N/A')}")
                                print(f"      文档ID: {record.get('document_id', 'N/A')}")
                                print(f"      文档名: {record.get('document_name', 'N/A')}")
                                print(f"      分数: {record.get('score', 'N/A')}")
                                print(f"      内容: {record.get('content', 'N/A')[:100]}...")
                        else:
                            print(f"\n⚠️  未检索到任何文档片段")
                            print(f"   可能原因:")
                            print(f"   1. 知识库为空或未包含相关内容")
                            print(f"   2. 查询词'{TEST_QUERY}'没有匹配的内容")
                            print(f"   3. score_threshold 设置过高")
                    else:
                        print(f"\n⚠️  响应格式异常: 缺少 'data' 字段")

                else:
                    print(f"\n❌ 请求失败!")
                    print(f"   状态码: {response.status_code}")
                    print(f"   错误信息: {response_json.get('message', 'N/A')}")

            except json.JSONDecodeError as e:
                print(f"\n❌ 响应解析失败: {e}")
                print(f"   原始响应: {response.text[:500]}")

    except httpx.ConnectTimeout as e:
        elapsed_time = time.time() - start_time
        print(f"\n❌ 连接超时 (耗时: {elapsed_time:.2f}秒)")
        print(f"   错误: {e}")
        print(f"\n💡 可能的原因:")
        print(f"   1. DIFY_API_BASE_URL 配置错误")
        print(f"   2. 网络连接问题")
        print(f"   3. Dify服务未启动或不可访问")

    except httpx.ReadTimeout as e:
        elapsed_time = time.time() - start_time
        print(f"\n❌ 读取超时 (耗时: {elapsed_time:.2f}秒)")
        print(f"   错误: {e}")
        print(f"\n💡 可能的原因:")
        print(f"   1. Dify服务响应过慢")
        print(f"   2. 知识库数据量过大")
        print(f"   3. 服务器负载过高")

    except httpx.HTTPStatusError as e:
        elapsed_time = time.time() - start_time
        print(f"\n❌ HTTP错误 (耗时: {elapsed_time:.2f}秒)")
        print(f"   状态码: {e.response.status_code}")
        print(f"   错误: {e}")
        print(f"   响应内容: {e.response.text}")

        print(f"\n💡 可能的原因:")
        if e.response.status_code == 401:
            print(f"   - API Key 错误或过期")
        elif e.response.status_code == 404:
            print(f"   - Dataset ID 不存在")
            print(f"   - API URL 路径错误")
        elif e.response.status_code == 403:
            print(f"   - API Key 无权限访问此知识库")

    except httpx.HTTPError as e:
        elapsed_time = time.time() - start_time
        print(f"\n❌ HTTP请求失败 (耗时: {elapsed_time:.2f}秒)")
        print(f"   错误类型: {type(e).__name__}")
        print(f"   错误信息: {e}")

    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"\n❌ 未知错误 (耗时: {elapsed_time:.2f}秒)")
        print(f"   错误类型: {type(e).__name__}")
        print(f"   错误信息: {e}")
        import traceback
        print(f"\n堆栈跟踪:")
        traceback.print_exc()

    print(f"\n" + "="*70)


async def test_dify_connection():
    """测试 Dify API 基础连通性"""

    print("\n" + "="*70)
    print("🔌 测试 Dify API 连通性")
    print("="*70)

    # 尝试访问基础URL
    base_url = DIFY_API_BASE_URL.rstrip('/v1').rstrip('/')

    print(f"\n测试 URL: {base_url}")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(base_url)
            print(f"✅ 连接成功!")
            print(f"   状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 连接失败: {e}")

    print(f"\n" + "="*70)


async def test_with_simple_query():
    """使用简单查询测试"""

    print("\n" + "="*70)
    print("🔍 使用简单查询测试 (semantic_search)")
    print("="*70)

    url = f"{DIFY_API_BASE_URL}/datasets/{DIFY_DATASET_ID}/retrieve"

    # 使用最简单的检索配置
    payload = {
        "query": "测试"
    }

    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json"
    }

    print(f"\n请求配置: {json.dumps(payload, ensure_ascii=False)}")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)

            print(f"\n状态码: {response.status_code}")
            print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

    print(f"\n" + "="*70)


def print_checklist():
    """打印检查清单"""
    print("\n" + "="*70)
    print("📋 Dify API 配置检查清单")
    print("="*70)

    print(f"\n请确认以下配置是否正确:")
    print(f"")
    print(f"✓ DIFY_API_BASE_URL = {DIFY_API_BASE_URL}")
    print(f"  - 确保URL格式正确 (例如: https://api.dify.ai/v1)")
    print(f"  - 如果是私有部署,确保地址可访问")
    print(f"")
    print(f"✓ DIFY_DATASET_ID = {DIFY_DATASET_ID}")
    print(f"  - 在 Dify 控制台查看知识库ID")
    print(f"  - 确保ID格式正确 (通常是UUID格式)")
    print(f"")
    print(f"✓ DIFY_API_KEY = {DIFY_API_KEY[:10]}...{DIFY_API_KEY[-4:]}" if len(DIFY_API_KEY) > 14 else f"✓ DIFY_API_KEY = {DIFY_API_KEY}")
    print(f"  - 在 Dify 控制台获取 API Key")
    print(f"  - 确保 API Key 有权限访问该知识库")
    print(f"")
    print(f"✓ 知识库状态")
    print(f"  - 确保知识库已创建")
    print(f"  - 确保知识库中已上传文档")
    print(f"  - 确保文档已完成向量化")
    print(f"")
    print("="*70)


async def main():
    """主函数"""

    print("\n" + "🚀"*35)
    print("Dify 知识库接口测试工具")
    print("🚀"*35)

    # 检查配置
    if DIFY_DATASET_ID == "your-dataset-id" or DIFY_API_KEY == "your-api-key":
        print("\n⚠️  警告: 请先在脚本顶部配置以下参数:")
        print("   - DIFY_API_BASE_URL")
        print("   - DIFY_DATASET_ID")
        print("   - DIFY_API_KEY")
        print("   - TEST_QUERY")
        return

    # 打印检查清单
    print_checklist()

    # 测试1: 连通性
    await test_dify_connection()

    # 测试2: 简单查询
    await test_with_simple_query()

    # 测试3: 详细测试
    await test_dify_retrieve_detailed()

    print("\n" + "="*70)
    print("✅ 所有测试完成!")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
