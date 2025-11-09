"""
请求对比工具 - 对比 Postman 和代码的请求差异
"""

import json


def compare_requests():
    """
    使用方法：
    1. 从代码日志中复制完整的请求信息
    2. 从 Postman 中导出请求信息
    3. 在下面填入对比
    """

    # ========== 从 Postman 导出的成功请求 ==========
    postman_request = {
        "url": "https://api.dify.ai/v1/datasets/0b50716f-c66d-4c78-b088-2198fc12ae85/retrieve",
        "headers": {
            "Authorization": "Bearer dataset-你的API-Key",  # 填入真实值
            "Content-Type": "application/json"
        },
        "body": {
            # 填入你 Postman 中成功的 Body
            "query": "python",
            "retrieval_model": {
                "search_method": "hybrid_search",
                "reranking_enable": False,
                "weights": 0.7,
                "top_k": 10,
                "score_threshold_enabled": True,
                "score_threshold": 0.1
            }
        }
    }

    # ========== 从代码日志中复制的请求 ==========
    code_request = {
        "url": "",  # 从日志中复制 [Dify] URL: 后面的值
        "headers": {
            "Authorization": "",  # 从日志中复制
            "Content-Type": "application/json"
        },
        "body": {
            # 从日志中复制 Request Body 的完整JSON
        }
    }

    print("\n" + "="*80)
    print("🔍 Postman vs 代码请求对比")
    print("="*80)

    # 对比 URL
    print("\n1️⃣ URL 对比:")
    print(f"   Postman: {postman_request['url']}")
    print(f"   代码:    {code_request['url']}")
    if postman_request['url'] != code_request['url']:
        print("   ❌ URL 不一致!")
    else:
        print("   ✅ URL 一致")

    # 对比 Headers
    print("\n2️⃣ Headers 对比:")
    print(f"   Postman Authorization: {postman_request['headers'].get('Authorization', 'N/A')}")
    print(f"   代码 Authorization:    {code_request['headers'].get('Authorization', 'N/A')}")

    postman_auth = postman_request['headers'].get('Authorization', '')
    code_auth = code_request['headers'].get('Authorization', '')

    if postman_auth and code_auth:
        # 检查 Bearer 前缀
        if not code_auth.startswith('Bearer '):
            print("   ❌ 代码缺少 'Bearer ' 前缀!")
        elif postman_auth != code_auth:
            print("   ⚠️  API Key 不同")
            # 对比长度
            if len(postman_auth) != len(code_auth):
                print(f"   ⚠️  长度不同: Postman={len(postman_auth)}, 代码={len(code_auth)}")
        else:
            print("   ✅ Authorization 一致")

    # 对比 Body
    print("\n3️⃣ Request Body 对比:")

    print("\n   Postman Body:")
    print(json.dumps(postman_request['body'], indent=4, ensure_ascii=False))

    print("\n   代码 Body:")
    print(json.dumps(code_request['body'], indent=4, ensure_ascii=False))

    # 详细对比每个字段
    print("\n4️⃣ Body 字段详细对比:")

    postman_body = postman_request['body']
    code_body = code_request['body']

    # query
    postman_query = postman_body.get('query')
    code_query = code_body.get('query')
    print(f"\n   query:")
    print(f"      Postman: '{postman_query}'")
    print(f"      代码:    '{code_query}'")
    if postman_query != code_query:
        print(f"      ❌ 查询词不同!")
    else:
        print(f"      ✅ 一致")

    # retrieval_model
    if 'retrieval_model' in postman_body or 'retrieval_model' in code_body:
        print(f"\n   retrieval_model:")

        pm_model = postman_body.get('retrieval_model', {})
        code_model = code_body.get('retrieval_model', {})

        fields = ['search_method', 'reranking_enable', 'weights', 'top_k',
                  'score_threshold_enabled', 'score_threshold']

        for field in fields:
            pm_value = pm_model.get(field)
            code_value = code_model.get(field)

            print(f"\n      {field}:")
            print(f"         Postman: {pm_value} (type: {type(pm_value).__name__})")
            print(f"         代码:    {code_value} (type: {type(code_value).__name__})")

            if pm_value != code_value:
                print(f"         ❌ 不同!")

                # 特别检查类型
                if type(pm_value) != type(code_value):
                    print(f"         ⚠️  类型不同! Postman={type(pm_value).__name__}, 代码={type(code_value).__name__}")

                # 特别提示 score_threshold
                if field == 'score_threshold':
                    if pm_value is not None and code_value is not None:
                        if code_value > pm_value:
                            print(f"         💡 代码的阈值({code_value})比Postman({pm_value})高，可能导致返回0条!")
            else:
                print(f"         ✅ 一致")

    print("\n" + "="*80)
    print("✅ 对比完成")
    print("="*80)

    print("\n💡 关键检查点:")
    print("   1. URL 是否完全一致（包括知识库ID）")
    print("   2. Authorization 是否包含 'Bearer ' 前缀")
    print("   3. API Key 是否一致")
    print("   4. query 查询词是否一致")
    print("   5. score_threshold 代码是否比 Postman 高（导致返回0条）")
    print("   6. 字段类型是否正确（特别是 boolean 和 number）")
    print()


if __name__ == "__main__":
    print("""
🔧 使用说明:

1. 运行你的代码，从日志中找到这些信息:
   - [Dify] URL: ...
   - [Dify] Headers: {...}
   - [Dify] Request Body: {...}

2. 从 Postman 中获取成功请求的信息

3. 在本脚本顶部填入 postman_request 和 code_request 的值

4. 运行此脚本:
   python compare_requests.py

5. 查看对比结果，找出差异
    """)

    compare_requests()
