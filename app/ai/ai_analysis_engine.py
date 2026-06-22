"""AI Analysis Engine for analyzing trading setups."""
import json
import openai
from typing import Optional

from app.config.__init__ import settings
from app.models.trading_models import Signal, AIAnalysisResult
from app.ai.groq_engine import GroqAnalysisEngine


class AIAnalysisEngine:
    """Analyzes trading setups using configured AI provider."""

    def __init__(self):
        """Initialize the AI analysis engine."""
        self.openai_client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        self.groq_engine = GroqAnalysisEngine()

    async def analyze_setup(self, signal: Signal) -> Optional[AIAnalysisResult]:
        """Analyze a trading signal using configured AI provider.
        
        Args:
            signal: Signal object containing setup data
            
        Returns:
            AIAnalysisResult if successful, None otherwise
        """
        if settings.ai_provider == "groq":
            return await self.groq_engine.analyze_setup(signal)
            
        # Default to OpenAI
        if not settings.openai_api_key:
            return self._generate_mock_analysis(signal)
        
        try:
            # Prepare input for OpenAI
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
            
            # Call OpenAI API
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o", # Updated model
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional trader. Analyze the setup and return JSON only with fields: score (0-100), entry (number), stop_loss (number), take_profit (number), risk_reward (string like '1:2'), summary (brief explanation)."
                    },
                    {
                        "role": "user",
                        "content": json.dumps(input_data)
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            # Parse response
            result_dict = json.loads(response.choices[0].message.content)
            return AIAnalysisResult(**result_dict)
            
        except Exception as e:
            # Log error and return None
            print(f"Error in OpenAI analysis: {e}")
            return None

    def _generate_mock_analysis(self, signal: Signal) -> AIAnalysisResult:
        """Generate mock analysis for development/testing."""
        import random
        
        # Generate realistic mock values based on signal type
        base_price = signal.price
        # Simple logic...
        entry = base_price * 0.999
        stop_loss = base_price * 0.985
        take_profit = base_price * 1.035
        summary = "Bullish setup."
        
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
