"""Main service orchestrator for the Trading Assistant."""
import asyncio
import json
import logging
from datetime import datetime
from typing import Optional

from app.config.__init__ import settings
from app.collectors.binance_collector import BinanceCollector
from app.collectors.ihsg_collector import IHSGCollector
from app.collectors.us_stock_collector import USStockCollector
from app.indicators.indicator_engine import IndicatorEngine
from app.signals.signal_engine import SignalEngine
from app.ai.ai_analysis_engine import AIAnalysisEngine
from app.telegram.telegram_service import TelegramService
from app.models.trading_models import Signal, AIAnalysisResult
from app.web.connection_manager import manager


class TradingAssistant:
    """Main orchestrator for the AI Trading Assistant."""

    def __init__(self):
        """Initialize the trading assistant."""
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.indicator_engine = IndicatorEngine()
        self.signal_engine = SignalEngine()
        self.ai_engine = AIAnalysisEngine()
        self.telegram_service = TelegramService()
        
        # Initialize collectors based on enabled markets
        self.collectors = {}
        self._setup_collectors()

        self.logger.info("Trading Assistant initialized")

    def _setup_collectors(self):
        """Setup data collectors based on enabled markets."""
        # Crypto collector
        if "crypto" in settings.markets_list:
            self.collectors["binance"] = BinanceCollector(
                symbols=["BTCUSDT", "ETHUSDT"],
                intervals=["1m", "5m", "15m"]
            )
            self.logger.info("Binance collector enabled for crypto")

        # IHSG collector
        if "ihsg" in settings.markets_list:
            self.collectors["ihsg"] = IHSGCollector()
            self.logger.info("IHSG collector enabled")

        # US Stocks collector
        if "us" in settings.markets_list:
            self.collectors["us_stocks"] = USStockCollector()
            self.logger.info("US Stocks collector enabled")

    def _get_collector_for_symbol(self, symbol: str):
        """Get the appropriate collector for a symbol."""
        # Check if symbol belongs to any collector
        for name, collector in self.collectors.items():
            if hasattr(collector, 'symbols'):
                if symbol in collector.symbols:
                    return collector
            # Special handling for Binance collector which has symbols as list
            if name == "binance" and hasattr(collector, 'symbols'):
                if symbol in collector.symbols:
                    return collector
        return None

    async def _on_new_candle(self, symbol: str, interval: str, candle) -> None:
        """Handle new candle data.
        
        Args:
            symbol: Trading symbol
            interval: Timeframe
            candle: New Candle object
        """
        self.logger.debug(f"New {interval} candle for {symbol}: {candle.close}")
        
        # Get the collector for this symbol
        collector = self._get_collector_for_symbol(symbol)
        if not collector:
            self.logger.warning(f"No collector found for symbol {symbol}")
            return
        
        # Get recent candles for indicator calculation
        if hasattr(collector, 'get_candles'):
            candles = collector.get_candles(symbol, interval)
        else:
            # Fallback for collectors with different interface
            candles = list(collector.candles.get(symbol, []))
            
        if len(candles) < 20:  # Need sufficient data for indicators
            return
        
        # Calculate indicators
        indicators = self.indicator_engine.calculate_indicators(candles)
        self.logger.debug(f"Indicators for {symbol}: EMA20={indicators.ema20}, RSI={indicators.rsi}")
        
        # Detect signals
        signal = self.signal_engine.evaluate(symbol, interval, indicators, candles)
        if signal:
            self.logger.info(f"Signal detected: {signal.setup_type} for {symbol} at {signal.price}")
            
            # Analyze with AI
            analysis = await self.ai_engine.analyze_setup(signal)
            if analysis:
                self.logger.info(f"AI Analysis: Score={analysis.score}, RR={analysis.risk_reward}")
                
                # Send Telegram alert
                success = await self.telegram_service.send_alert(signal, analysis)
                if success:
                    self.logger.info(f"Alert sent for {signal.setup_type} {symbol}")
                    
                    # Broadcast signal via WebSocket
                    await manager.broadcast(json.dumps({
                        "type": "signal",
                        "symbol": symbol,
                        "signal": {
                            "setup_type": signal.setup_type,
                            "price": signal.price,
                            "score": analysis.score,
                            "timestamp": datetime.now().isoformat()
                        }
                    }))
                else:
                    self.logger.error(f"Failed to send alert for {signal.setup_type} {symbol}")
            else:
                self.logger.warning(f"AI analysis failed for {signal.setup_type} {symbol}")

    async def start(self) -> None:
        """Start the trading assistant."""
        self.logger.info("Starting Trading Assistant...")
        
        # Set callbacks for all collectors
        for name, collector in self.collectors.items():
            collector.set_callback(self._on_new_candle)
            self.logger.info(f"Set callback for {name} collector")
        
        # Start all collectors concurrently
        tasks = []
        for name, collector in self.collectors.items():
            if hasattr(collector, 'start'):
                task = asyncio.create_task(collector.start())
                tasks.append(task)
                self.logger.info(f"Started {name} collector")
        
        # Wait for all collectors (they run indefinitely)
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def stop(self) -> None:
        """Stop the trading assistant."""
        self.logger.info("Stopping Trading Assistant...")
        
        # Stop all collectors
        for name, collector in self.collectors.items():
            if hasattr(collector, 'stop'):
                await collector.stop()
                self.logger.info(f"Stopped {name} collector")


async def main() -> None:
    """Main entry point."""
    assistant = TradingAssistant()
    try:
        await assistant.start()
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await assistant.stop()


if __name__ == "__main__":
    asyncio.run(main())
