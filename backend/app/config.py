from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = Field(default="ProcessGraph Sentinel", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    app_log_level: str = Field(default="INFO", alias="APP_LOG_LEVEL")
    app_cors_origins: str = Field(default="http://localhost:3001", alias="APP_CORS_ORIGINS")

    falkordb_host: str = Field(default="falkordb", alias="FALKORDB_HOST")
    falkordb_port: int = Field(default=6379, alias="FALKORDB_PORT")
    falkordb_password: str = Field(default="", alias="FALKORDB_PASSWORD")
    falkordb_graph_prefix: str = Field(default="processgraph", alias="FALKORDB_GRAPH_PREFIX")
    falkordb_graph_name: str | None = Field(default=None, alias="FALKORDB_GRAPH_NAME")

    llm_provider: str = Field(default="disabled", alias="LLM_PROVIDER")
    max_traversal_depth: int = Field(default=4, alias="MAX_TRAVERSAL_DEPTH", ge=1, le=8)
    agent_timeout_seconds: int = Field(default=30, alias="AGENT_TIMEOUT_SECONDS", ge=1)
    memory_promotion_threshold: float = Field(
        default=0.8, alias="MEMORY_PROMOTION_THRESHOLD", ge=0, le=1
    )

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.app_cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
