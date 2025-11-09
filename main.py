from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
from typing import Dict, Any

from models import QueryRequest, RetrievalResponse, RetrievalQuery
from llm_service import llm_service
from dify_client import dify_client
from rerank_service import rerank_service
from config import settings


# 应用启动和关闭时的生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    print("🚀 Dify知识库检索增强API启动中...")
    print(f"📝 配置信息:")
    print(f"   - Dify API: {settings.dify_api_base_url}")
    print(f"   - LLM Model: {settings.llm_model}")
    print(f"   - Reranker Model: {settings.reranker_model_name}")
    yield
    print("👋 Dify知识库检索增强API关闭")


# 创建FastAPI应用
app = FastAPI(
    title="Dify Knowledge Retrieval Enhanced API",
    description="基于Dify的智能知识库检索增强接口",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """根路径 - API信息"""
    return {
        "name": "Dify Knowledge Retrieval Enhanced API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "retrieve": "/api/v1/retrieve",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": time.time()
    }


@app.post("/api/v1/retrieve", response_model=RetrievalResponse)
async def retrieve_knowledge(request: QueryRequest):
    """
    知识库检索增强接口

    工作流程:
    1. LLM判断是否需要检索以及生成检索查询
    2. 如果不需要检索,直接返回
    3. 如果需要检索,并行调用Dify知识库检索
    4. 汇总所有检索结果
    5. 使用Reranker进行重排序
    6. 返回最终结果

    Args:
        request: 检索请求

    Returns:
        RetrievalResponse: 检索响应
    """
    start_time = time.time()

    try:
        # 第一步: LLM判断是否需要检索
        step1_start = time.time()
        print(f"[Step 1] LLM判断是否需要检索...")
        llm_decision = await llm_service.decide_retrieval(
            question=request.question,
            datasets=request.datasets,
            document=request.document
        )
        step1_time = time.time() - step1_start

        print(f"[Step 1] 判断结果: need_retrieval={llm_decision.need_retrieval} (耗时{step1_time:.2f}s)")

        # 如果不需要检索,直接返回
        if not llm_decision.need_retrieval:
            return RetrievalResponse(
                success=True,
                need_retrieval=False,
                retrieval_queries=[],
                segments=[],
                total_segments=0,
                message="根据LLM判断,此问题不需要检索知识库"
            )

        # 如果没有生成检索查询,返回错误
        if not llm_decision.retrieval_queries:
            return RetrievalResponse(
                success=False,
                need_retrieval=True,
                retrieval_queries=[],
                segments=[],
                total_segments=0,
                error="LLM判断需要检索,但未生成有效的检索查询"
            )

        print(f"[Step 1] 生成 {len(llm_decision.retrieval_queries)} 个检索查询")

        # 第二步: 并行检索所有知识库
        step2_start = time.time()
        print(f"[Step 2] 并行检索知识库...")
        all_segments = await dify_client.batch_retrieve(
            retrieval_queries=llm_decision.retrieval_queries,
            api_key=request.dataset_api_key,
            top_k=request.top_k,
            score_threshold=request.score_threshold,
            semantic_weight=request.semantic_weight
        )
        step2_time = time.time() - step2_start

        print(f"[Step 2] 检索完成,共 {len(all_segments)} 个片段 (耗时{step2_time:.2f}s)")

        # 如果没有检索到任何结果
        if not all_segments:
            return RetrievalResponse(
                success=True,
                need_retrieval=True,
                retrieval_queries=llm_decision.retrieval_queries,
                segments=[],
                total_segments=0,
                message="未检索到符合条件的文档片段"
            )

        # 第三步: 使用Reranker进行重排序
        step3_start = time.time()
        print(f"[Step 3] Rerank重排序 (top_k={request.rerank_top_k})...")

        # 构建查询文本(合并原始问题和文档)
        if request.document:
            rerank_query = f"{request.document}\n\n{request.question}"
        else:
            rerank_query = request.question

        # 执行rerank
        reranked_segments = await rerank_service.rerank_segments(
            query=rerank_query,
            segments=all_segments,
            top_k=request.rerank_top_k
        )
        step3_time = time.time() - step3_start

        print(f"[Step 3] Rerank完成,返回 {len(reranked_segments)} 个片段 (耗时{step3_time:.2f}s)")

        # 计算总耗时
        elapsed_time = time.time() - start_time
        print(f"[完成] 总耗时: {elapsed_time:.2f}s (LLM:{step1_time:.2f}s + 检索:{step2_time:.2f}s + Rerank:{step3_time:.2f}s)\n")

        # 返回最终结果
        return RetrievalResponse(
            success=True,
            need_retrieval=True,
            retrieval_queries=llm_decision.retrieval_queries,
            segments=reranked_segments,
            total_segments=len(reranked_segments),
            message=f"检索成功,返回{len(reranked_segments)}个相关文档片段 (耗时{elapsed_time:.2f}秒)"
        )

    except Exception as e:
        print(f"[错误] 检索异常: {str(e)}")

        return RetrievalResponse(
            success=False,
            need_retrieval=True,
            retrieval_queries=[],
            segments=[],
            total_segments=0,
            error=f"检索异常: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": f"服务器内部错误: {str(exc)}"
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug
    )
