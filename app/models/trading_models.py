"""Data models for the Trading Assistant."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class Candle(BaseModel):
    """Represents a single candlestick data point."""
    open_time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    close_time: datetime


class MarketData(BaseModel):
    """Market data for a symbol."""
    symbol: str
    timeframe: str
    candles: list[Candle]


class Indicators(BaseModel):
    """Technical indicators for market analysis."""
    ema20: Optional[float] = None
    ema50: Optional[float] = None
    ema200: Optional[float] = None
    rsi: Optional[float] = None
    volume_sma20: Optional[float] = None
    atr: Optional[float] = None


class Signal(BaseModel):
    """Trading signal detected by the Signal Engine."""
    symbol: str
    timeframe: str
    setup_type: str  # LONG, SHORT, BREAKOUT
    price: float
    timestamp: datetime
    indicators: Indicators


class AIAnalysisResult(BaseModel):
    """Result from the AI Analysis Engine."""
    score: int
    entry: float
    stop_loss: float
    take_profit: float
    risk_reward: str
    summary: str
