import json
from typing import List
import httpx
from models import DatasetInfo, LLMDecision, RetrievalQuery
from config import settings


class LLMService:
    """LLM服务，用于判断是否需要检索以及生成检索查询"""

    def __init__(self):
        self.api_base_url = settings.llm_api_base_url
        self.api_key = settings.llm_api_key
        self.model = settings.llm_model

    def _create_system_prompt(self, datasets: List[DatasetInfo]) -> str:
        """创建系统提示词"""
        dataset_desc = "\n".join([
            f"- 知识库ID: {ds.dataset_id}\n  描述: {ds.description}"
            for ds in datasets
        ])

        return f"""你是一个智能检索助手。你的任务是分析用户问题,判断是否需要从知识库中检索信息来回答。

可用的知识库:
{dataset_desc}

请按照以下规则进行判断:
1. 如果问题需要特定的事实、数据、文档内容或专业知识才能回答,则需要检索
2. 如果问题是通用常识、闲聊、问候等,则不需要检索
3. 如果需要检索,请为每个相关的知识库生成最优的检索查询语句
4. 检索查询应该简洁、准确,能够匹配到相关文档

你必须以JSON格式返回结果,格式如下:
{{
    "need_retrieval": true/false,
    "retrieval_queries": [
        {{
            "dataset_id": "知识库ID",
            "query": "优化后的检索查询"
        }}
    ]
}}

注意:
- 如果need_retrieval为false,retrieval_queries应为空数组
- 可以为同一个知识库生成多个不同角度的查询
- 查询语句应该提取问题的核心关键词和语义"""

    def _create_user_prompt(self, question: str, document: str = None) -> str:
        """创建用户提示词"""
        if document:
            return f"""相关文档内容:
{document}

用户问题:
{question}

请分析是否需要从知识库检索更多信息。"""
        else:
            return f"""用户问题:
{question}

请分析是否需要从知识库检索信息。"""

    async def decide_retrieval(
        self,
        question: str,
        datasets: List[DatasetInfo],
        document: str = None
    ) -> LLMDecision:
        """
        判断是否需要检索以及生成检索查询

        Args:
            question: 用户问题
            datasets: 可用的知识库列表
            document: 相关文档(可选)

        Returns:
            LLMDecision: 判断结果
        """
        system_prompt = self._create_system_prompt(datasets)
        user_prompt = self._create_user_prompt(question, document)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": 0.3,
                        "response_format": {"type": "json_object"}
                    }
                )
                response.raise_for_status()

                result = response.json()
                content = result["choices"][0]["message"]["content"]

                # 解析JSON响应
                decision_data = json.loads(content)

                return LLMDecision(
                    need_retrieval=decision_data.get("need_retrieval", False),
                    retrieval_queries=[
                        RetrievalQuery(**query)
                        for query in decision_data.get("retrieval_queries", [])
                    ],
                    reason=None
                )

        except httpx.HTTPError as e:
            print(f"[LLM] API请求失败: {e}")
            # 发生错误时默认需要检索，使用原始问题
            return LLMDecision(
                need_retrieval=True,
                retrieval_queries=[
                    RetrievalQuery(dataset_id=ds.dataset_id, query=question)
                    for ds in datasets
                ],
                reason=None
            )
        except (json.JSONDecodeError, KeyError) as e:
            print(f"[LLM] 解析响应失败: {e}")
            # 解析失败时默认需要检索
            return LLMDecision(
                need_retrieval=True,
                retrieval_queries=[
                    RetrievalQuery(dataset_id=ds.dataset_id, query=question)
                    for ds in datasets
                ],
                reason=None
            )


# 创建全局实例
llm_service = LLMService()
