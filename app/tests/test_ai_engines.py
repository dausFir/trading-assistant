import pytest
from unittest.mock import MagicMock, AsyncMock
from app.ai.groq_engine import GroqAnalysisEngine
from app.models.trading_models import Signal, Indicators

@pytest.mark.asyncio
async def test_groq_engine_analyze_setup_mock():
    # Test with no API key (should trigger mock)
    engine = GroqAnalysisEngine()
    
    signal = Signal(
        symbol="BTCUSDT",
        timeframe="1m",
        price=50000,
        indicators=Indicators(ema20=50000, ema50=49000, ema200=48000, rsi=60, atr=100),
        setup_type="LONG"
    )
    
    result = await engine.analyze_setup(signal)
    assert result is not None
    assert 65 <= result.score <= 95
