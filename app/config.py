from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    openai_base_url: str = Field(default="http://localhost:1234/v1", alias="OPENAI_BASE_URL")
    openai_api_key: str = Field(default="lm-studio", alias="OPENAI_API_KEY")
    host: str = Field(default="127.0.0.1", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    cors_origins: str = Field(default="*", alias="CORS_ORIGINS")
    default_regular_model: str = Field(default="qwen/qwen3-4b-2507", alias="DEFAULT_REGULAR_MODEL")
    default_vision_model: str = Field(default="qwen3-vl-4b-instruct", alias="DEFAULT_VISION_MODEL")
    # Timeout for LLM requests (connect timeout, read timeout for streaming)
    llm_timeout: float = Field(default=300.0, alias="LLM_TIMEOUT")

    @property
    def cors_origin_list(self) -> List[str]:
        if self.cors_origins == "*":
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache
def get_settings() -> Settings:
    return Settings()
