from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""

    # Dify Configuration
    dify_api_base_url: str = "https://api.dify.ai/v1"
    dify_api_key: str

    # LLM Configuration
    llm_api_base_url: str = "https://api.openai.com/v1"
    llm_api_key: str
    llm_model: str = "gpt-4-turbo-preview"

    # Reranker Configuration
    reranker_api_url: str
    reranker_api_key: str
    reranker_model_name: str = "bge-reranker-v2-m3"

    # Application Configuration
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = True

    # Retrieval Configuration
    default_top_k: int = 10
    default_rerank_top_k: int = 5
    default_score_threshold: float = 0.4
    default_semantic_weight: float = 0.7

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
