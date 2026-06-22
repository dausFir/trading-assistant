"""Telegram Notification Service for sending alerts."""
import asyncio
from telegram import Bot
from telegram.constants import ParseMode

from app.config.__init__ import settings
from app.models.trading_models import Signal, AIAnalysisResult


class TelegramService:
    """Service for sending trading alerts to Telegram."""

    def __init__(self):
        """Initialize the Telegram service."""
        self.bot = Bot(token=settings.telegram_bot_token)
        self.chat_id = settings.telegram_chat_id

    async def send_alert(self, signal: Signal, analysis: AIAnalysisResult) -> bool:
        """Send a trading alert to Telegram.
        
        Args:
            signal: Signal object
            analysis: AI analysis result
            
        Returns:
            True if message sent successfully, False otherwise
        """
        if not settings.telegram_bot_token or not settings.telegram_chat_id:
            # For development/testing, just print what would be sent
            print(self._format_message(signal, analysis))
            return True

        try:
            message = self._format_message(signal, analysis)
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN
            )
            return True
        except Exception as e:
            print(f"Error sending Telegram message: {e}")
            return False

    def _format_message(self, signal: Signal, analysis: AIAnalysisResult) -> str:
        """Format the trading alert message.
        
        Args:
            signal: Signal object
            analysis: AI analysis result
            
        Returns:
            Formatted message string
        """
        emoji = "🚀" if signal.setup_type == "LONG" else "🔻" if signal.setup_type == "SHORT" else "⚡"
        setup_emoji = {
            "LONG": "LONG",
            "SHORT": "SHORT", 
            "BREAKOUT": "BREAKOUT"
        }
        
        message = f"""{emoji} *{signal.symbol} {setup_emoji[signal.setup_type]}*

Timeframe: {signal.timeframe}

Score: {analysis.score}/100

Entry:
{analysis.entry}

SL:
{analysis.stop_loss}

TP:
{analysis.take_profit}

RR:
{analysis.risk_reward}

Reason:
{analysis.summary}"""
        
        return message
