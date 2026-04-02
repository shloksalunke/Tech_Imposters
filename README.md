# ⚡ CryptoMind — AI-Powered Crypto Intelligence Dashboard

> Real-time cryptocurrency analysis platform combining **LSTM price predictions**, **LLM-powered sentiment analysis**, and **on-chain whale tracking** into a unified trading intelligence dashboard.

---

## 🎯 Overview

CryptoMind is a full-stack crypto analytics platform that aggregates multiple data signals and generates AI-driven trading recommendations. The system processes live market data through four independent pipelines and presents actionable insights through a modern React dashboard.

### Key Features

| Feature | Description |
|---------|-------------|
| 📊 **LSTM Price Forecasting** | PyTorch-based 3-layer stacked LSTM predicting 1h, 4h, and 24h prices for BTC, ETH, BNB |
| 🧠 **AI Sentiment Analysis** | Ollama (Mistral 7B) analyzes live crypto news with confidence scoring |
| 🐋 **Whale Tracking** | Monitors large Ethereum transactions via Etherscan with exchange classification |
| ⚡ **Trading Signals** | LLM fusion engine combining sentiment, predictions, and whale data into BUY/SELL/HOLD signals |
| 📈 **Live Dashboard** | React + Recharts frontend with 15-second auto-refresh |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────┐
│                   React Frontend                     │
│  MetricCards · PriceChart · SignalFeed · WhaleNews    │
│                  (15s polling)                        │
└──────────────────┬───────────────────────────────────┘
                   │ HTTP REST
┌──────────────────▼───────────────────────────────────┐
│              FastAPI Backend (app.py)                 │
│  /api/sentiment · /api/whales · /api/prediction      │
│  /api/signals   · /api/chart                         │
└──────────────────┬───────────────────────────────────┘
                   │ asyncpg
┌──────────────────▼───────────────────────────────────┐
│              PostgreSQL Database                     │
│  news_sentiment · whale_transactions                 │
│  price_forecasts · signals                           │
└──────────────────▲───────────────────────────────────┘
                   │ psycopg2
┌──────────────────┴───────────────────────────────────┐
│            Background Pipelines                      │
│  sentiment_pipeline.py  │  whale_pipeline.py         │
│  lstm_predict.py        │  signal_generator.py       │
└──────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
Tech_Imposters/
├── backend/
│   ├── app.py                      # FastAPI entry point
│   ├── requirements.txt            # Python dependencies
│   ├── schema.sql                  # Database schema
│   ├── routes/
│   │   ├── sentiment.py            # /api/sentiment endpoints
│   │   ├── whales.py               # /api/whales endpoint
│   │   ├── prediction.py           # /api/prediction endpoint
│   │   ├── signals.py              # /api/signals endpoint
│   │   └── chart.py                # /api/chart endpoint
│   ├── services/
│   │   └── db_service.py           # asyncpg connection pool
│   └── crypto_terminal/
│       ├── config.py               # Central configuration
│       ├── db.py                   # psycopg2 DB helper
│       ├── sentiment_pipeline.py   # RSS → Ollama → DB
│       ├── whale_pipeline.py       # Etherscan → DB
│       ├── lstm_predict.py         # PyTorch LSTM forecaster
│       └── signal_generator.py     # LLM signal fusion
├── frontend/
│   ├── src/
│   │   ├── pages/Index.tsx         # Dashboard page
│   │   ├── hooks/useApi.ts         # API hooks (15s polling)
│   │   └── components/
│   │       ├── Header.tsx
│   │       ├── MetricCards.tsx
│   │       ├── PriceChart.tsx
│   │       ├── SignalFeed.tsx
│   │       └── WhaleNews.tsx
│   └── package.json
└── models/                         # Pre-trained LSTM weights
    ├── btc_lstm_final_full.pth
    ├── eth_lstm_final_full.pth
    └── bnb_lstm_final_full.pth
```

---

## ⚙️ Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **PostgreSQL 14+**
- **Ollama** with `mistral:7b-instruct-q4_K_M` model pulled
- **Etherscan API Key** (for whale tracking)

---

## 🚀 Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/shloksalunke/Tech_Imposters.git
cd Tech_Imposters
```

### 2. Database setup

```bash
psql -U postgres -f backend/schema.sql
```

### 3. Backend setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

Create `backend/crypto_terminal/.env`:

```env
ETHERSCAN_API_KEY=your_etherscan_key
```

### 4. Frontend setup

```bash
cd frontend
npm install
```

### 5. Pull Ollama model

```bash
ollama pull mistral:7b-instruct-q4_K_M
```

---

## ▶️ Running the Application

Open **5 terminals**:

```bash
# Terminal 1 — FastAPI server
cd backend
python -m uvicorn app:app --port 8000

# Terminal 2 — Sentiment pipeline
cd backend/crypto_terminal
python sentiment_pipeline.py

# Terminal 3 — Whale tracker
cd backend/crypto_terminal
python whale_pipeline.py

# Terminal 4 — LSTM predictions
cd backend/crypto_terminal
python lstm_predict.py

# Terminal 5 — Signal generator
cd backend/crypto_terminal
python signal_generator.py

# Terminal 6 — Frontend
cd frontend
npm run dev
```

Open **http://localhost:5173** to view the dashboard.

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/sentiment/latest` | GET | Latest 50 news with sentiment scores |
| `/api/sentiment/summary` | GET | Per-coin sentiment aggregation (3h window) |
| `/api/whales` | GET | Recent whale transactions |
| `/api/prediction/{symbol}` | GET | LSTM price forecast (1h, 4h, 24h) |
| `/api/signals` | GET | AI trading signals with reasoning |
| `/api/chart/{symbol}?days=30` | GET | Historical prices + prediction overlay |

---

## 🧠 Pipeline Details

### Sentiment Pipeline
- Fetches crypto news from RSS feeds (CoinDesk, CoinTelegraph, Decrypt, Bitcoin Magazine)  
- Analyzes each article using **Ollama Mistral 7B** with structured prompting  
- Outputs: `BULLISH | BEARISH | NEUTRAL | FUD` with confidence score (0–1)

### Whale Pipeline
- Monitors Ethereum blockchain via **Etherscan API**  
- Classifies large transactions (>10 ETH) as inflow/outflow  
- Identifies known exchange wallets (Binance, etc.)

### LSTM Forecaster
- 3-layer stacked LSTM (input=32 → 128 → 64 → 32 → FC)  
- Trained on Binance 15-min OHLCV candles  
- Predicts prices at 1-hour, 4-hour, and 24-hour horizons

### Signal Generator
- Fuses sentiment, whale activity, and price predictions  
- Generates `BUY | SELL | HOLD` signals via LLM reasoning  
- Outputs confidence percentage and detailed explanation

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React, TypeScript, Vite, Tailwind CSS, Recharts |
| Backend | FastAPI, asyncpg, Uvicorn |
| Database | PostgreSQL |
| ML/AI | PyTorch (LSTM), Ollama (Mistral 7B) |
| Data Sources | Binance, Etherscan, RSS Feeds |

---

## 👥 Team

**Tech Imposters** — NMIMS Indore

---

## 📄 License

This project is developed for educational and hackathon purposes.
