"""Signal Engine for detecting trading setups."""
from datetime import datetime, timedelta
from typing import Optional

from app.models.trading_models import Candle, Indicators, Signal


class SignalEngine:
    """Detects trading signals based on technical indicators."""

    def __init__(self, cooldown_minutes: int = 60):
        """Initialize the signal engine.
        
        Args:
            cooldown_minutes: Minimum time between signals for same symbol/setup
        """
        self.cooldown_minutes = cooldown_minutes
        # Track last signal time: {(symbol, setup_type): datetime}
        self._last_signal_time: dict[tuple[str, str], datetime] = {}

    def detect_long_setup(self, indicators: Indicators, price: float) -> bool:
        """Detect Long Setup conditions.
        
        Long Setup:
        - EMA20 > EMA50
        - EMA50 > EMA200
        - RSI between 50 and 70
        - Volume > VolumeSMA20
        """
        if not all([indicators.ema20, indicators.ema50, indicators.ema200, 
                   indicators.rsi, indicators.volume_sma20]):
            return False
        
        return (
            indicators.ema20 > indicators.ema50 >
            indicators.ema200 and
            50 < indicators.rsi < 70 and
            indicators.volume_sma20 is not None and
            indicators.volume_sma20 > 0
        )

    def detect_short_setup(self, indicators: Indicators, price: float) -> bool:
        """Detect Short Setup conditions.
        
        Short Setup:
        - EMA20 < EMA50
        - EMA50 < EMA200
        - RSI between 30 and 50
        - Volume > VolumeSMA20
        """
        if not all([indicators.ema20, indicators.ema50, indicators.ema200,
                   indicators.rsi, indicators.volume_sma20]):
            return False
        
        return (
            indicators.ema20 < indicators.ema50 <
            indicators.ema200 and
            30 < indicators.rsi < 50 and
            indicators.volume_sma20 is not None and
            indicators.volume_sma20 > 0
        )

    def detect_breakout_setup(self, candles: list[Candle]) -> bool:
        """Detect Breakout Setup conditions.
        
        Breakout Setup:
        - Current close > previous 20-candle high
        - Volume > 1.5x average volume (of last 20 candles)
        """
        if len(candles) < 21:
            return False
        
        current_candle = candles[-1]
        previous_candles = candles[-21:-1]
        
        # Previous 20-candle high
        prev_high = max(c.high for c in previous_candles)
        
        # Average volume
        avg_volume = sum(c.volume for c in previous_candles) / 20
        
        return (
            current_candle.close > prev_high and
            current_candle.volume > 1.5 * avg_volume
        )

    def check_cooldown(self, symbol: str, setup_type: str) -> bool:
        """Check if a signal is within the cooldown period.
        
        Args:
            symbol: Trading symbol
            setup_type: Type of setup (LONG, SHORT, BREAKOUT)
            
        Returns:
            True if within cooldown (should skip), False if OK to signal
        """
        key = (symbol, setup_type)
        if key not in self._last_signal_time:
            return False
        
        elapsed = datetime.now() - self._last_signal_time[key]
        return elapsed < timedelta(minutes=self.cooldown_minutes)

    def update_cooldown(self, symbol: str, setup_type: str) -> None:
        """Update the last signal time for cooldown tracking.
        
        Args:
            symbol: Trading symbol
            setup_type: Type of setup
        """
        key = (symbol, setup_type)
        self._last_signal_time[key] = datetime.now()

    def evaluate(self, symbol: str, timeframe: str, 
                 indicators: Indicators, 
                 candles: list[Candle]) -> Optional[Signal]:
        """Evaluate all setups and return a signal if detected.
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe
            indicators: Calculated indicators
            candles: Recent candle data
            
        Returns:
            Signal if detected and not in cooldown, None otherwise
        """
        price = candles[-1].close if candles else 0
        timestamp = datetime.now()

        # Check Long Setup
        if self.detect_long_setup(indicators, price):
            if not self.check_cooldown(symbol, "LONG"):
                self.update_cooldown(symbol, "LONG")
                return Signal(
                    symbol=symbol,
                    timeframe=timeframe,
                    setup_type="LONG",
                    price=price,
                    timestamp=timestamp,
                    indicators=indicators,
                )

        # Check Short Setup
        if self.detect_short_setup(indicators, price):
            if not self.check_cooldown(symbol, "SHORT"):
                self.update_cooldown(symbol, "SHORT")
                return Signal(
                    symbol=symbol,
                    timeframe=timeframe,
                    setup_type="SHORT",
                    price=price,
                    timestamp=timestamp,
                    indicators=indicators,
                )

        # Check Breakout Setup
        if self.detect_breakout_setup(candles):
            if not self.check_cooldown(symbol, "BREAKOUT"):
                self.update_cooldown(symbol, "BREAKOUT")
                return Signal(
                    symbol=symbol,
                    timeframe=timeframe,
                    setup_type="BREAKOUT",
                    price=price,
                    timestamp=timestamp,
                    indicators=indicators,
                )

        return None
