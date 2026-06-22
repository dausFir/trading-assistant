"""Configuration module for Trading Assistant."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys
    openai_api_key: str = ""
    groq_api_key: str = ""
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    
    # Endpoints
    binance_ws_url: str = "wss://stream.binance.com:9443/ws"
    
    # Market & AI Config
    enabled_markets: list[str] = ["crypto", "ihsg", "us"]
    ai_provider: str = "openai"  # openai or groq

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
