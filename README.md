# 🤖 AI Trading Assistant

A powerful, multi-market AI-driven trading assistant capable of monitoring Crypto, US Stocks, and Indonesian Stocks (IHSG) with real-time AI analysis powered by LLMs (OpenAI/Groq).

## 🚀 Features

- **Multi-Market Support**: Seamlessly monitors Binance (Crypto), IHSG (Indonesia), and US Stock markets.
- **AI-Powered Analysis**: Delivers intelligent trade setups using OpenAI or Groq API.
- **Real-time Dashboard**: A lightweight FastAPI web dashboard for visualizing live price data and AI signals.
- **Automated Alerts**: Direct notifications via Telegram for actionable trading signals.
- **Extensible Architecture**: Modular collectors for easy integration of new data sources.

## 📋 Technology Stack

- **Backend**: Python 3.13, FastAPI
- **Data**: yfinance (Stocks), Binance WebSocket (Crypto)
- **AI Engines**: OpenAI API, Groq API
- **Frontend**: Vanilla JS (WebSocket-based)

---

## 🛠 Prerequisites

- Python 3.13+
- A valid `OPENAI_API_KEY` or `GROQ_API_KEY`
- (Optional) Telegram `BOT_TOKEN` and `CHAT_ID`

## ⚙️ Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd trading-assistant
   ```

2. **Install dependencies:**
   ```bash
   pip install -e .
   ```

3. **Configure Environment:**
   Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   # Add your API keys and configuration
   ```

## 🚀 How to Run

### Start the Dashboard
To start the real-time trading dashboard:
```bash
python -m app.web.server
```
Visit `http://localhost:8000` in your web browser.

## 🏗 Project Architecture

- `app/collectors/`: Data ingestors for various markets.
- `app/ai/`: Engines for AI market analysis.
- `app/web/`: FastAPI dashboard and WebSocket management.
- `app/services/`: Main application orchestrator.

## 🛡 Disclaimer
This software is for educational purposes only. Use it at your own risk. Trading involves significant financial risk.