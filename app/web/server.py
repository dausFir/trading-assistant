"""Web server with FastAPI and WebSocket support for real-time dashboard."""
import asyncio
import json
from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from app.services.main_service import TradingAssistant
from app.config.__init__ import settings
from app.web.connection_manager import manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    global trading_assistant
    trading_assistant = TradingAssistant()
    
    # Modify the callback to send updates via WebSocket
    original_callback = trading_assistant._on_new_candle
    
    async def websocket_callback(symbol: str, interval: str, candle):
        await original_callback(symbol, interval, candle)
        # Determine market from symbol
        market = "unknown"
        if symbol.endswith("USDT"):
            market = "crypto"
        elif symbol.endswith(".JK"):
            market = "ihsg"
        elif len(symbol) <= 5 and symbol.isalpha():  # Typical US stock symbols
            market = "us"
        
        # Broadcast candle data to all connected clients
        await manager.broadcast(json.dumps({
            "type": "candle",
            "market": market,
            "symbol": symbol,
            "interval": interval,
            "data": {
                "open": candle.open,
                "high": candle.high,
                "low": candle.low,
                "close": candle.close,
                "volume": candle.volume,
                "timestamp": candle.close_time.isoformat()
            }
        }))
    
    trading_assistant._on_new_candle = websocket_callback
    
    # Start the trading assistant in background
    task = asyncio.create_task(trading_assistant.start())
    
    yield  # Application runs here
    
    # Shutdown logic
    if trading_assistant:
        await trading_assistant.stop()
        task.cancel()

app = FastAPI(title="AI Trading Assistant Dashboard", version="0.1.0", lifespan=lifespan)

# Mount static files
app.mount("/static", StaticFiles(directory="app/web/static"), name="static")

# Global trading assistant instance
trading_assistant: Optional[TradingAssistant] = None

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Serve the main dashboard page."""
    with open("app/web/static/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
