"""
测试脚本 - 用于测试 Dify 知识库检索增强 API
"""

import asyncio
import httpx
import json
from typing import Dict, Any


API_BASE_URL = "http://localhost:8000"


async def test_health_check():
    """测试健康检查接口"""
    print("\n" + "="*60)
    print("🔍 测试: 健康检查")
    print("="*60)

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


async def test_retrieve_with_retrieval():
    """测试需要检索的场景"""
    print("\n" + "="*60)
    print("🔍 测试: 需要检索的问题")
    print("="*60)

    request_data = {
        "datasets": [
            {
                "dataset_id": "your-dataset-id",
                "description": "产品技术文档知识库,包含API文档、架构设计、使用指南等内容"
            }
        ],
        "dataset_api_key": "your-dataset-api-key",
        "question": "如何使用API进行数据导入?",
        "document": "用户正在查看数据管理模块",
        "top_k": 10,
        "rerank_top_k": 5,
        "score_threshold": 0.4,
        "semantic_weight": 0.7
    }

    print(f"\n📤 请求数据:")
    print(json.dumps(request_data, indent=2, ensure_ascii=False))

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{API_BASE_URL}/api/v1/retrieve",
                json=request_data
            )

            print(f"\n📥 响应状态码: {response.status_code}")
            result = response.json()
            print(f"\n📥 响应数据:")
            print(json.dumps(result, indent=2, ensure_ascii=False))

            # 分析结果
            if result.get("success"):
                print(f"\n✅ 检索成功!")
                print(f"   - 是否需要检索: {result.get('need_retrieval')}")
                print(f"   - 检索查询数: {len(result.get('retrieval_queries', []))}")
                print(f"   - 返回片段数: {result.get('total_segments')}")

                if result.get('retrieval_queries'):
                    print(f"\n🔎 检索查询:")
                    for i, query in enumerate(result['retrieval_queries'], 1):
                        print(f"   {i}. [{query['dataset_id']}] {query['query']}")

                if result.get('segments'):
                    print(f"\n📄 文档片段:")
                    for i, seg in enumerate(result['segments'], 1):
                        print(f"\n   片段 {i}:")
                        print(f"   - 来源: {seg.get('dataset_name', 'N/A')} / {seg.get('document_name', 'N/A')}")
                        print(f"   - 分数: {seg['score']:.3f}")
                        print(f"   - 内容: {seg['content'][:100]}...")
            else:
                print(f"\n❌ 检索失败: {result.get('error')}")

    except Exception as e:
        print(f"\n❌ 请求失败: {str(e)}")


async def test_retrieve_no_retrieval():
    """测试不需要检索的场景"""
    print("\n" + "="*60)
    print("🔍 测试: 不需要检索的问题")
    print("="*60)

    request_data = {
        "datasets": [
            {
                "dataset_id": "your-dataset-id",
                "description": "产品技术文档知识库"
            }
        ],
        "dataset_api_key": "your-dataset-api-key",
        "question": "你好",
        "rerank_top_k": 5
    }

    print(f"\n📤 请求数据:")
    print(json.dumps(request_data, indent=2, ensure_ascii=False))

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{API_BASE_URL}/api/v1/retrieve",
                json=request_data
            )

            print(f"\n📥 响应状态码: {response.status_code}")
            result = response.json()
            print(f"\n📥 响应数据:")
            print(json.dumps(result, indent=2, ensure_ascii=False))

            if result.get("success"):
                print(f"\n✅ 请求成功!")
                print(f"   - 是否需要检索: {result.get('need_retrieval')}")
                print(f"   - 消息: {result.get('message')}")
            else:
                print(f"\n❌ 请求失败: {result.get('error')}")

    except Exception as e:
        print(f"\n❌ 请求失败: {str(e)}")


async def test_multi_dataset():
    """测试多知识库检索"""
    print("\n" + "="*60)
    print("🔍 测试: 多知识库检索")
    print("="*60)

    request_data = {
        "datasets": [
            {
                "dataset_id": "dataset-api-docs",
                "description": "API技术文档,包含所有接口的详细说明和示例"
            },
            {
                "dataset_id": "dataset-faq",
                "description": "常见问题FAQ,包含用户常见问题和解决方案"
            },
            {
                "dataset_id": "dataset-tutorials",
                "description": "教程文档,包含入门指南和最佳实践"
            }
        ],
        "dataset_api_key": "your-dataset-api-key",
        "question": "如何快速开始使用产品?",
        "top_k": 8,
        "rerank_top_k": 5
    }

    print(f"\n📤 请求数据:")
    print(json.dumps(request_data, indent=2, ensure_ascii=False))

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{API_BASE_URL}/api/v1/retrieve",
                json=request_data
            )

            print(f"\n📥 响应状态码: {response.status_code}")
            result = response.json()
            print(f"\n📥 响应数据:")
            print(json.dumps(result, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"\n❌ 请求失败: {str(e)}")


async def main():
    """主函数"""
    print("\n" + "🚀"*30)
    print("Dify 知识库检索增强 API - 测试脚本")
    print("🚀"*30)

    # 1. 健康检查
    await test_health_check()

    # 2. 测试需要检索的场景
    await test_retrieve_with_retrieval()

    # 3. 测试不需要检索的场景
    # await test_retrieve_no_retrieval()

    # 4. 测试多知识库
    # await test_multi_dataset()

    print("\n" + "="*60)
    print("✅ 所有测试完成!")
    print("="*60 + "\n")


if __name__ == "__main__":
    print("\n⚠️  注意: 请先修改测试脚本中的以下参数:")
    print("   - dataset_id: 你的知识库ID")
    print("   - dataset_api_key: 你的知识库API Key")
    print("   - question: 测试问题")
    print("\n   然后取消注释需要测试的场景\n")

    asyncio.run(main())
