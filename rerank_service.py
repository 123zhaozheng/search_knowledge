from typing import List, Dict, Any
import httpx
from models import DocumentSegment, RerankRequest, RerankResult
from config import settings


class RerankService:
    """Rerank服务,用于对检索结果进行重排序"""

    def __init__(self):
        self.api_url = settings.reranker_api_url
        self.api_key = settings.reranker_api_key
        self.model_name = settings.reranker_model_name

    async def rerank_segments(
        self,
        query: str,
        segments: List[DocumentSegment],
        top_k: int = 5
    ) -> List[DocumentSegment]:
        """
        对文档片段进行重排序

        Args:
            query: 原始查询
            segments: 待排序的文档片段列表
            top_k: 返回的top-k结果数量

        Returns:
            List[DocumentSegment]: 重排序后的文档片段
        """
        if not segments:
            return []

        # 如果片段数量小于等于top_k,直接返回
        if len(segments) <= top_k:
            return segments

        # 准备文档内容列表
        documents = [seg.content for seg in segments]

        # 构建rerank请求
        rerank_request = RerankRequest(
            model=self.model_name,
            query=query,
            documents=documents,
            top_n=top_k,
            return_documents=True
        )

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=rerank_request.model_dump()
                )
                response.raise_for_status()

                result = response.json()
                rerank_results = result.get("results", [])

                # 根据rerank结果重新排序segments
                reranked_segments = []
                for rerank_result in rerank_results:
                    index = rerank_result.get("index")
                    relevance_score = rerank_result.get("relevance_score", 0.0)

                    if 0 <= index < len(segments):
                        segment = segments[index]
                        # 更新分数为rerank分数
                        segment.score = relevance_score
                        reranked_segments.append(segment)

                return reranked_segments

        except httpx.HTTPError as e:
            print(f"Rerank API请求失败: {e}")
            # 如果rerank失败,返回原始排序的top_k结果
            return segments[:top_k]
        except Exception as e:
            print(f"Rerank处理失败: {e}")
            return segments[:top_k]

    async def rerank_with_multiple_queries(
        self,
        queries: List[str],
        segments: List[DocumentSegment],
        top_k: int = 5
    ) -> List[DocumentSegment]:
        """
        使用多个查询进行rerank(取平均分)

        Args:
            queries: 多个查询语句
            segments: 待排序的文档片段列表
            top_k: 返回的top-k结果数量

        Returns:
            List[DocumentSegment]: 重排序后的文档片段
        """
        if not segments or not queries:
            return segments[:top_k]

        # 为每个query单独rerank,收集分数
        segment_scores: Dict[str, List[float]] = {}

        for query in queries:
            reranked = await self.rerank_segments(query, segments, len(segments))
            for seg in reranked:
                seg_key = f"{seg.dataset_id}_{seg.segment_id}"
                if seg_key not in segment_scores:
                    segment_scores[seg_key] = []
                segment_scores[seg_key].append(seg.score)

        # 计算平均分数
        for segment in segments:
            seg_key = f"{segment.dataset_id}_{segment.segment_id}"
            if seg_key in segment_scores:
                scores = segment_scores[seg_key]
                segment.score = sum(scores) / len(scores)

        # 按平均分数排序并返回top-k
        segments.sort(key=lambda x: x.score, reverse=True)
        return segments[:top_k]


# 创建全局实例
rerank_service = RerankService()
