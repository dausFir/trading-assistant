import pytest
from unittest.mock import MagicMock, AsyncMock
from app.collectors.us_stock_collector import USStockCollector
from app.collectors.ihsg_collector import IHSGCollector

@pytest.mark.asyncio
async def test_us_stock_collector_fetch():
    collector = USStockCollector(symbols=["AAPL"])
    # Mock yfinance ticker
    collector.fetch_candle = AsyncMock(return_value=MagicMock())
    
    candle = await collector.fetch_candle("AAPL")
    assert candle is not None
    collector.fetch_candle.assert_awaited_once_with("AAPL")

@pytest.mark.asyncio
async def test_ihsg_collector_fetch():
    collector = IHSGCollector(symbols=["BBCA.JK"])
    # Mock yfinance ticker
    collector.fetch_candle = AsyncMock(return_value=MagicMock())
    
    candle = await collector.fetch_candle("BBCA.JK")
    assert candle is not None
    collector.fetch_candle.assert_awaited_once_with("BBCA.JK")
