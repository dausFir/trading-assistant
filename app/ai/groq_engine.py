"""Groq AI Analysis Engine - Free tier alternative to OpenAI."""
import json
from typing import Optional

from groq import AsyncGroq

from app.config.__init__ import settings
from app.models.trading_models import Signal, AIAnalysisResult


class GroqAnalysisEngine:
    """Analyzes trading setups using Groq API (free tier)."""

    def __init__(self):
        """Initialize the Groq analysis engine."""
        self.client = AsyncGroq(api_key=settings.groq_api_key or "")

    async def analyze_setup(self, signal: Signal) -> Optional[AIAnalysisResult]:
        """Analyze a trading signal using Groq API.
        
        Args:
            signal: Signal object containing setup data
            
        Returns:
            AIAnalysisResult if successful, None otherwise
        """
        if not settings.groq_api_key:
            # Return mock analysis if no API key
            return self._generate_mock_analysis(signal)
        
        try:
            # Prepare input for Groq
            input_data = {
                "symbol": signal.symbol,
                "timeframe": signal.timeframe,
                "price": signal.price,
                "ema20": signal.indicators.ema20,
                "ema50": signal.indicators.ema50,
                "ema200": signal.indicators.ema200,
                "rsi": signal.indicators.rsi,
                "atr": signal.indicators.atr,
            }
            
            # Call Groq API
            response = await self.client.chat.completions.create(
                model="llama-3.1-8b-instant",  # Free tier model
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional trader. Analyze the setup and return ONLY JSON with these fields: score (0-100), entry (number), stop_loss (number), take_profit (number), risk_reward (string like '1:2'), summary (brief explanation)."
                    },
                    {
                        "role": "user",
                        "content": f"Analyze this trading setup: {json.dumps(input_data)}"
                    }
                ],
                temperature=0.7,
                max_tokens=500,
            )
            
            # Parse response
            content = response.choices[0].message.content
            
            # Extract JSON from response
            try:
                result_dict = json.loads(content)
            except json.JSONDecodeError:
                # Try to extract JSON from text if not pure JSON
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    result_dict = json.loads(json_match.group())
                else:
                    print(f"Failed to parse Groq response: {content}")
                    return None
            
            return AIAnalysisResult(**result_dict)
            
        except Exception as e:
            print(f"Error in Groq analysis: {e}")
            return None

    def _generate_mock_analysis(self, signal: Signal) -> AIAnalysisResult:
        """Generate mock analysis for development/testing without API key."""
        import random
        
        base_price = signal.price
        
        if signal.setup_type == "LONG":
            entry = base_price * 0.999
            stop_loss = base_price * 0.985
            take_profit = base_price * 1.035
            summary = "Bullish continuation with strong volume."
        elif signal.setup_type == "SHORT":
            entry = base_price * 1.001
            stop_loss = base_price * 1.015
            take_profit = base_price * 0.965
            summary = "Bearish reversal with volume confirmation."
        else:
            entry = base_price * 1.0005
            stop_loss = base_price * 0.992
            take_profit = base_price * 1.025
            summary = "Breakout above resistance with increased volume."
        
        risk = abs(entry - stop_loss)
        reward = abs(take_profit - entry)
        rr_ratio = f"1:{reward/risk:.1f}" if risk > 0 else "1:0"
        
        return AIAnalysisResult(
            score=random.randint(65, 95),
            entry=round(entry, 2),
            stop_loss=round(stop_loss, 2),
            take_profit=round(take_profit, 2),
            risk_reward=rr_ratio,
            summary=summary
        )
