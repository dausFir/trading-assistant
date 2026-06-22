"""Indicator Engine for calculating technical indicators."""
import pandas as pd
from ta.trend import EMAIndicator, SMAIndicator
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange

from app.models.trading_models import Candle, Indicators


class IndicatorEngine:
    """Calculates technical indicators from candle data."""

    def __init__(self):
        """Initialize the indicator engine."""
        pass

    def calculate_indicators(self, candles: list[Candle]) -> Indicators:
        """Calculate technical indicators from candlestick data.
        
        Args:
            candles: List of Candle objects
            
        Returns:
            Indicators object with calculated values
        """
        if len(candles) < 1:
            return Indicators()
        
        # Convert to DataFrame for calculations
        df = pd.DataFrame([{
            'open': c.open,
            'high': c.high,
            'low': c.low,
            'close': c.close,
            'volume': c.volume,
        } for c in candles])
        
        indicators = Indicators()
        
        # Ensure we have enough data
        if len(candles) >= 20:
            # EMA 20
            ema20 = EMAIndicator(df['close'], window=20)
            indicators.ema20 = ema20.ema_indicator().iloc[-1]
        
        if len(candles) >= 50:
            # EMA 50
            ema50 = EMAIndicator(df['close'], window=50)
            indicators.ema50 = ema50.ema_indicator().iloc[-1]
        
        if len(candles) >= 200:
            # EMA 200
            ema200 = EMAIndicator(df['close'], window=200)
            indicators.ema200 = ema200.ema_indicator().iloc[-1]
        
        if len(candles) >= 14:
            # RSI 14
            rsi = RSIIndicator(df['close'], window=14)
            indicators.rsi = rsi.rsi().iloc[-1]
        
        if len(candles) >= 20:
            # Volume SMA 20
            volume_sma = SMAIndicator(df['volume'], window=20)
            indicators.volume_sma20 = volume_sma.sma_indicator().iloc[-1]
        
        if len(candles) >= 14:
                # ATR 14
                atr = AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=14)
                indicators.atr = atr.average_true_range().iloc[-1]
        
        return indicators
