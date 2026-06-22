"""Unit tests for the Trading Assistant."""
import pytest
from datetime import datetime

from app.indicators.indicator_engine import IndicatorEngine
from app.signals.signal_engine import SignalEngine
from app.ai.ai_analysis_engine import AIAnalysisEngine
from app.models.trading_models import Candle, Indicators


class TestIndicatorEngine:
    """Tests for the Indicator Engine."""

    def test_calculate_indicators_with_sufficient_data(self):
        """Test indicator calculation with sufficient data."""
        engine = IndicatorEngine()
        
        # Create 200 candles with upward trend
        candles = []
        for i in range(200):
            candles.append(Candle(
                open_time=datetime.now(),
                open=100 + i * 0.1,
                high=100 + i * 0.1 + 0.5,
                low=100 + i * 0.1 - 0.5,
                close=100 + i * 0.1,
                volume=1000,
                close_time=datetime.now(),
            ))
        
        indicators = engine.calculate_indicators(candles)
        
        assert indicators.ema20 is not None
        assert indicators.ema50 is not None
        assert indicators.ema200 is not None
        assert indicators.rsi is not None
        assert indicators.volume_sma20 is not None
        assert indicators.atr is not None

    def test_calculate_indicators_with_insufficient_data(self):
        """Test indicator calculation with insufficient data."""
        engine = IndicatorEngine()
        
        # Create only 5 candles
        candles = [
            Candle(
                open_time=datetime.now(),
                open=100,
                high=101,
                low=99,
                close=100,
                volume=1000,
                close_time=datetime.now(),
            )
            for _ in range(5)
        ]
        
        indicators = engine.calculate_indicators(candles)
        
        # Only EMA is calculated with < 20 data
        assert indicators.ema20 is None


class TestSignalEngine:
    """Tests for the Signal Engine."""

    def test_detect_long_setup(self):
        """Test Long Setup detection."""
        engine = SignalEngine()
        
        indicators = Indicators(
            ema20=105000,
            ema50=104000,
            ema200=103000,
            rsi=60,
            volume_sma20=1000,
            atr=500,
        )
        
        assert engine.detect_long_setup(indicators, 105000) is True

    def test_detect_short_setup(self):
        """Test Short Setup detection."""
        engine = SignalEngine()
        
        indicators = Indicators(
            ema20=103000,
            ema50=104000,
            ema200=105000,
            rsi=40,
            volume_sma20=1000,
            atr=500,
        )
        
        assert engine.detect_short_setup(indicators, 103000) is True

    def test_cooldown_logic(self):
        """Test cooldown logic."""
        engine = SignalEngine(cooldown_minutes=60)
        
        # Should be OK initially
        assert engine.check_cooldown("BTCUSDT", "LONG") is False
        
        # Update cooldown
        engine.update_cooldown("BTCUSDT", "LONG")
        
        # Should be in cooldown now
        assert engine.check_cooldown("BTCUSDT", "LONG") is True
        
        # Different setup should be OK
        assert engine.check_cooldown("BTCUSDT", "SHORT") is False

    def test_evaluate_returns_signal(self):
        """Test evaluate returns signal when conditions met."""
        engine = SignalEngine()
        
        # Create proper indicators for Long Setup
        indicators = Indicators(
            ema20=105000,
            ema50=104000,
            ema200=103000,
            rsi=60,
            volume_sma20=1000,
            atr=500,
        )
        
        # Create 21 candles for breakout check + enough for other indicators
        candles = [
            Candle(
                open_time=datetime.now(),
                open=100 + i * 0.1,
                high=100 + i * 0.1 + 0.5,
                low=100 + i * 0.1 - 0.5,
                close=100 + i * 0.1,
                volume=1000,
                close_time=datetime.now(),
            )
            for i in range(25)
        ]
        
        signal = engine.evaluate("BTCUSDT", "15m", indicators, candles)
        
        assert signal is not None
        assert signal.symbol == "BTCUSDT"
        assert signal.setup_type == "LONG"


class TestAIAnalysisEngine:
    """Tests for the AI Analysis Engine."""

    @pytest.mark.asyncio
    async def test_analyze_setup_returns_result(self):
        """Test analyze setup returns analysis result."""
        engine = AIAnalysisEngine()
        
        signal = Candle(
            open_time=datetime.now(),
            open=100,
            high=101,
            low=99,
            close=100,
            volume=1000,
            close_time=datetime.now(),
        )
        
        # Create a dummy Signal object for test
        from app.models.trading_models import Signal
        signal_obj = Signal(
            symbol="BTCUSDT",
            timeframe="15m",
            setup_type="LONG",
            price=105000,
            timestamp=datetime.now(),
            indicators=Indicators(
                ema20=105000,
                ema50=104000,
                ema200=103000,
                rsi=60,
                volume_sma20=1000,
                atr=500,
            ),
        )
        
        result = await engine.analyze_setup(signal_obj)
        
        assert result is not None
        assert result.score > 0
        assert result.entry > 0
        assert result.stop_loss > 0
        assert result.take_profit > 0
