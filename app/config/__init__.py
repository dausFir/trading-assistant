"""Configuration module for Trading Assistant."""
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # API Keys
    openai_api_key: str = ""
    groq_api_key: str = ""
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    
    # Endpoints
    binance_ws_url: str = "wss://stream.binance.com:9443/ws"
    
    # Market & AI Config
    enabled_markets: str = "crypto,ihsg,us"
    ai_provider: str = "openai"  # openai or groq

    @property
    def markets_list(self) -> List[str]:
        """Get enabled markets as a list."""
        return [market.strip() for market in self.enabled_markets.split(',') if market.strip()]


settings = Settings()
