from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class DatasetInfo(BaseModel):
    """知识库信息"""
    dataset_id: str = Field(..., description="知识库ID")
    description: str = Field(..., description="知识库详细描述")


class QueryRequest(BaseModel):
    """检索请求模型"""
    datasets: List[DatasetInfo] = Field(..., description="知识库列表")
    dataset_api_key: str = Field(..., description="知识库API Key")
    question: str = Field(..., description="用户原始问题")
    document: Optional[str] = Field(None, description="相关文档内容(可选)")

    # 检索参数
    top_k: int = Field(10, description="每个知识库返回的结果数量", ge=1, le=20)
    rerank_top_k: int = Field(5, description="Rerank后返回的最终结果数量", ge=1, le=20)
    score_threshold: float = Field(0.4, description="分数阈值", ge=0.0, le=1.0)
    semantic_weight: float = Field(0.7, description="混合检索中语义检索的权重", ge=0.0, le=1.0)


class RetrievalQuery(BaseModel):
    """单个检索查询"""
    dataset_id: str = Field(..., description="知识库ID")
    query: str = Field(..., description="检索查询语句")


class LLMDecision(BaseModel):
    """LLM判断结果"""
    need_retrieval: bool = Field(..., description="是否需要检索")
    retrieval_queries: List[RetrievalQuery] = Field(
        default_factory=list,
        description="需要检索的查询列表"
    )
    reason: Optional[str] = Field(None, description="判断理由")


class DocumentSegment(BaseModel):
    """文档片段"""
    dataset_id: str = Field(..., description="来源知识库ID")
    dataset_name: Optional[str] = Field(None, description="知识库名称")
    document_id: str = Field(..., description="文档ID")
    document_name: Optional[str] = Field(None, description="文档名称")
    segment_id: str = Field(..., description="片段ID")
    content: str = Field(..., description="片段内容")
    score: float = Field(..., description="相关性分数")
    position: Optional[int] = Field(None, description="在文档中的位置")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="额外元数据")


class RetrievalResponse(BaseModel):
    """检索响应模型"""
    success: bool = Field(..., description="请求是否成功")
    need_retrieval: bool = Field(..., description="是否需要检索")
    retrieval_queries: List[RetrievalQuery] = Field(
        default_factory=list,
        description="执行的检索查询列表"
    )
    segments: List[DocumentSegment] = Field(
        default_factory=list,
        description="检索到的文档片段(已排序)"
    )
    total_segments: int = Field(0, description="总片段数")
    message: Optional[str] = Field(None, description="响应消息")
    error: Optional[str] = Field(None, description="错误信息")


class DifyRetrievalRequest(BaseModel):
    """Dify知识库检索请求"""
    query: str
    retrieval_model: Dict[str, Any] = {
        "search_method": "hybrid_search",
        "reranking_enable": False,
        "weights": 0.7,
        "top_k": 10,
        "score_threshold_enabled": True,
        "score_threshold": 0.4
    }


class DifyDocument(BaseModel):
    """Dify返回的文档模型"""
    id: str
    name: str
    content: str
    score: float
    dataset_id: str
    dataset_name: Optional[str] = None
    document_id: Optional[str] = None
    segment_id: Optional[str] = None
    position: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class RerankRequest(BaseModel):
    """Rerank请求模型"""
    model: str
    query: str
    documents: List[str]
    top_n: Optional[int] = None
    return_documents: bool = True


class RerankResult(BaseModel):
    """Rerank结果"""
    index: int
    relevance_score: float
    document: Optional[str] = None
