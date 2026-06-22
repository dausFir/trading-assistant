"""Binance Market Data Collector."""
import asyncio
import json
from datetime import datetime
from typing import Callable, Optional
from collections import deque
import websockets

from app.models.trading_models import Candle


class BinanceCollector:
    """Collects realtime market data from Binance WebSocket."""

    def __init__(self, symbols: list[str] = None, intervals: list[str] = None, max_candles: int = 500):
        """Initialize the Binance collector.
        
        Args:
            symbols: List of trading symbols (default: ["BTCUSDT", "ETHUSDT"])
            intervals: List of timeframes (default: ["1m", "5m", "15m"])
            max_candles: Maximum number of candles to store in memory
        """
        self.symbols = symbols or ["BTCUSDT", "ETHUSDT"]
        self.intervals = intervals or ["1m", "5m", "15m"]
        self.max_candles = max_candles
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.running = False
        # Store candles as {symbol: {interval: deque}}
        self.candles: dict[str, dict[str, deque[Candle]]] = {}
        self._callback: Optional[Callable] = None

    async def connect(self) -> None:
        """Connect to Binance WebSocket."""
        streams = [f"{symbol.lower()}@kline_{interval}" for symbol in self.symbols for interval in self.intervals]
        ws_url = f"wss://stream.binance.com:9443/stream?streams={'/'.join(streams)}"
        
        self.ws = await websockets.connect(ws_url)
        self.running = True
        
        # Initialize candle storage
        for symbol in self.symbols:
            self.candles[symbol] = {}
            for interval in self.intervals:
                self.candles[symbol][interval] = deque(maxlen=self.max_candles)

    async def disconnect(self) -> None:
        """Disconnect from Binance WebSocket."""
        self.running = False
        if self.ws:
            await self.ws.close()

    def set_callback(self, callback: Callable[[str, str, Candle], None]) -> None:
        """Set callback function for new candle data.
        
        Args:
            callback: Function that takes (symbol, interval, candle)
        """
        self._callback = callback

    async def listen(self) -> None:
        """Listen for WebSocket messages."""
        if not self.ws:
            await self.connect()

        try:
            while self.running:
                message = await self.ws.recv()
                data = json.loads(message)
                
                if data.get("e") == "kline":
                    kline = data["k"]
                    symbol = kline["s"]
                    interval = kline["i"]
                    
                    candle = Candle(
                        open_time=datetime.fromtimestamp(kline["t"] / 1000),
                        open=float(kline["o"]),
                        high=float(kline["h"]),
                        low=float(kline["l"]),
                        close=float(kline["c"]),
                        volume=float(kline["v"]),
                        close_time=datetime.fromtimestamp(kline["T"] / 1000),
                    )
                    
                    self.candles[symbol][interval].append(candle)
                    
                    # Callback for new candle
                    if self._callback:
                        await self._callback(symbol, interval, candle)
                        
        except websockets.exceptions.ConnectionClosed:
            # Reconnect on disconnect
            await self.reconnect()

    async def reconnect(self) -> None:
        """Reconnect to Binance WebSocket."""
        await self.disconnect()
        await self.connect()
        await self.listen()

    def get_candles(self, symbol: str, interval: str) -> list[Candle]:
        """Get stored candles for a symbol and interval.
        
        Args:
            symbol: Trading symbol
            interval: Timeframe
            
        Returns:
            List of Candle objects
        """
        if symbol in self.candles and interval in self.candles[symbol]:
            return list(self.candles[symbol][interval])
        return []
