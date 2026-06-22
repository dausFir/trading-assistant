"""US Stock Collector using yfinance."""
import asyncio
from datetime import datetime
from typing import Callable, Optional
from collections import deque

import yfinance as yf

from app.models.trading_models import Candle


class USStockCollector:
    """Collects US stock market data using yfinance."""

    def __init__(
        self,
        symbols: list[str] = None,
        interval_minutes: int = 1,
        max_candles: int = 500,
    ):
        """Initialize the US stock collector.
        
        Args:
            symbols: List of US stock symbols (default: major US stocks)
            interval_minutes: Update interval in minutes
            max_candles: Maximum candles to store in memory
        """
        self.symbols = symbols or ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
        self.interval_minutes = interval_minutes
        self.max_candles = max_candles
        self.running = False
        self._task: Optional[asyncio.Task] = None
        # Store candles as {symbol: deque}
        self.candles: dict[str, deque[Candle]] = {}
        self._callback: Optional[Callable] = None
        
        # Initialize candle storage
        for symbol in self.symbols:
            self.candles[symbol] = deque(maxlen=self.max_candles)

    def set_callback(self, callback: Callable[[str, Candle], None]) -> None:
        """Set callback for new candle data.
        
        Args:
            callback: Function that takes (symbol, candle)
        """
        self._callback = callback

    async def fetch_candle(self, symbol: str) -> Optional[Candle]:
        """Fetch latest candle for a symbol using yfinance.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Candle object or None if fetch failed
        """
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="1d", interval="1m")
            
            if df.empty:
                return None
            
            # Get the latest candle
            last = df.iloc[-1]
            
            candle = Candle(
                open_time=last.name.to_pydatetime(),
                open=float(last["Open"]),
                high=float(last["High"]),
                low=float(last["Low"]),
                close=float(last["Close"]),
                volume=float(last["Volume"]),
                close_time=datetime.now(),
            )
            
            return candle
            
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return None

    async def _update_loop(self) -> None:
        """Background loop to fetch latest data."""
        while self.running:
            for symbol in self.symbols:
                candle = await self.fetch_candle(symbol)
                if candle:
                    self.candles[symbol].append(candle)
                    
                    if self._callback:
                        await self._callback(symbol, candle)
            
            # Wait for interval
            await asyncio.sleep(self.interval_minutes * 60)

    async def start(self) -> None:
        """Start the collector."""
        self.running = True
        self._task = asyncio.create_task(self._update_loop())

    async def stop(self) -> None:
        """Stop the collector."""
        self.running = False
        if self._task:
            self._task.cancel()

    def get_candles(self, symbol: str) -> list[Candle]:
        """Get stored candles for a symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            List of Candle objects
        """
        if symbol in self.candles:
            return list(self.candles[symbol])
        return []
