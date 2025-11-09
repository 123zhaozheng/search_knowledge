from typing import List, Dict, Any
import asyncio
import httpx
from models import DocumentSegment, RetrievalQuery
from config import settings


class DifyClient:
    """Dify知识库检索客户端"""

    def __init__(self):
        self.api_base_url = settings.dify_api_base_url.rstrip('/')

    async def retrieve_from_dataset(
        self,
        dataset_id: str,
        query: str,
        api_key: str,
        top_k: int = 10,
        score_threshold: float = 0.4,
        semantic_weight: float = 0.7
    ) -> List[DocumentSegment]:
        """
        从单个知识库检索

        Args:
            dataset_id: 知识库ID
            query: 检索查询
            api_key: API密钥
            top_k: 返回结果数量
            score_threshold: 分数阈值
            semantic_weight: 语义检索权重

        Returns:
            List[DocumentSegment]: 检索到的文档片段列表
        """
        url = f"{self.api_base_url}/datasets/{dataset_id}/retrieve"

        payload = {
            "query": query,
            "retrieval_model": {
                "search_method": "hybrid_search",
                "reranking_enable": False,
                "weights": semantic_weight,
                "top_k": top_k,
                "score_threshold_enabled": True,
                "score_threshold": score_threshold
            }
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        try:
            import time
            start_time = time.time()

            # 配置超时设置
            timeout = httpx.Timeout(
                connect=10.0,
                read=30.0,
                write=10.0,
                pool=10.0
            )

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()

                result = response.json()
                records = result.get("records", [])

                elapsed = time.time() - start_time
                print(f"[Dify] 检索完成: {len(records)}个片段 (耗时{elapsed:.2f}s)")

                # 转换为统一的DocumentSegment格式
                segments = []
                for record in records:
                    try:
                        segment_data = record.get("segment", {})
                        document_data = segment_data.get("document", {})

                        segment = DocumentSegment(
                            dataset_id=dataset_id,
                            dataset_name=None,
                            document_id=segment_data.get("document_id", ""),
                            document_name=document_data.get("name", ""),
                            segment_id=segment_data.get("id", ""),
                            content=segment_data.get("content", ""),
                            score=record.get("score", 0.0),
                            position=segment_data.get("position"),
                            metadata=document_data.get("doc_metadata", {})
                        )
                        segments.append(segment)
                    except Exception as e:
                        print(f"[Dify] 警告: 片段转换失败: {e}")
                        continue

                return segments

        except httpx.ConnectTimeout as e:
            print(f"[Dify] ❌ 连接超时 [dataset_id={dataset_id}]: {e}")
            print(f"[Dify] 请检查: 1) API地址是否正确 2) 网络连接是否正常")
            return []
        except httpx.ReadTimeout as e:
            print(f"[Dify] ❌ 读取超时 [dataset_id={dataset_id}]: {e}")
            print(f"[Dify] 请检查: 1) Dify服务是否正常 2) 知识库数据量是否过大")
            return []
        except httpx.HTTPStatusError as e:
            print(f"[Dify] ❌ HTTP错误 [dataset_id={dataset_id}]:")
            print(f"[Dify]    状态码: {e.response.status_code}")
            print(f"[Dify]    响应: {e.response.text[:500]}")
            if e.response.status_code == 401:
                print(f"[Dify]    可能原因: API Key 错误或过期")
            elif e.response.status_code == 404:
                print(f"[Dify]    可能原因: Dataset ID 不存在或URL路径错误")
            elif e.response.status_code == 403:
                print(f"[Dify]    可能原因: API Key 无权限访问此知识库")
            return []
        except httpx.HTTPError as e:
            print(f"[Dify] ❌ HTTP请求失败 [dataset_id={dataset_id}]:")
            print(f"[Dify]    错误类型: {type(e).__name__}")
            print(f"[Dify]    错误信息: {e}")
            return []
        except Exception as e:
            print(f"[Dify] ❌ 处理响应时出错 [dataset_id={dataset_id}]:")
            print(f"[Dify]    错误类型: {type(e).__name__}")
            print(f"[Dify]    错误信息: {e}")
            import traceback
            traceback.print_exc()
            return []

    async def batch_retrieve(
        self,
        retrieval_queries: List[RetrievalQuery],
        api_key: str,
        top_k: int = 10,
        score_threshold: float = 0.4,
        semantic_weight: float = 0.7
    ) -> List[DocumentSegment]:
        """
        并行批量检索多个知识库

        Args:
            retrieval_queries: 检索查询列表
            api_key: API密钥
            top_k: 每个知识库返回的结果数量
            score_threshold: 分数阈值
            semantic_weight: 语义检索权重

        Returns:
            List[DocumentSegment]: 合并后的所有文档片段(已去重)
        """
        # 创建并发任务
        tasks = [
            self.retrieve_from_dataset(
                dataset_id=query.dataset_id,
                query=query.query,
                api_key=api_key,
                top_k=top_k,
                score_threshold=score_threshold,
                semantic_weight=semantic_weight
            )
            for query in retrieval_queries
        ]

        # 并行执行所有检索任务
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 合并所有结果，并根据 segment_id 和 content 去重
        seen_segment_ids = set()
        seen_contents = set()  # 新增：内容去重
        all_segments = []

        for result in results:
            if isinstance(result, list):
                for segment in result:
                    # 同时根据 segment_id 和 content 去重
                    if segment.segment_id not in seen_segment_ids and segment.content not in seen_contents:
                        seen_segment_ids.add(segment.segment_id)
                        seen_contents.add(segment.content)
                        all_segments.append(segment)
            elif isinstance(result, Exception):
                print(f"[Dify] 检索任务失败: {result}")

        total_before = sum(len(r) if isinstance(r, list) else 0 for r in results)
        print(f"[Dify] 去重后剩余 {len(all_segments)} 个片段 (去重前: {total_before}, 去重: {total_before - len(all_segments)})")

        return all_segments


# 创建全局实例
dify_client = DifyClient()
