"""Application settings, read from environment variables or a .env file."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All tunable values in one place. Override via TINYRAG_<NAME> env vars."""

    model_config = SettingsConfigDict(env_prefix="TINYRAG_", env_file=".env")

    ollama_url: str = "http://localhost:11434"
    embedding_model: str = "bge-m3"
    llm_model: str = "qwen2.5:14b"
    llm_context_tokens: int = 8192
    qdrant_path: Path = Path("data/qdrant")
    collection_name: str = "documents"
    top_k: int = 5
