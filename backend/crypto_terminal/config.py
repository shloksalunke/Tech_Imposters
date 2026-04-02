# config.py — Central configuration for the Crypto Intelligence Terminal

# ─── Existing Binance DB (READ-ONLY) ─────────────────────────────────────────
BINANCE_DB = {
    "host":     "localhost",
    "port":     5432,
    "user":     "binance_user",
    "password": "secure_password_123",
    "dbname":   "binance_data"
}

# ─── New Crypto Terminal DB (READ + WRITE) ────────────────────────────────────
CRYPTO_DB = {
    "host":     "localhost",
    "port":     5432,
    "user":     "crypto_user",
    "password": "crypto_pass_123",
    "dbname":   "crypto_terminal"
}

# ─── Coins & Table Mapping ────────────────────────────────────────────────────
COINS = ["BTC", "ETH", "BNB"]

COIN_TABLE_MAP = {
    "BTC": "btcusdt",
    "ETH": "ethusdt",
    "BNB": "bnbusdt"
}

# ─── LSTM Models ──────────────────────────────────────────────────────────────
MODEL_DIR = "../models"

MODEL_MAP = {
    "BTC": "btc_lstm_final_full",
    "ETH": "eth_lstm_final_full",
    "BNB": "bnb_lstm_final_full"
}

SEQUENCE_LENGTH = 96  # 24h of 15-min candles

FEATURE_COLS = [
    "close_price",
    "volume",
    "price_range",
    "price_change",
    "sma_10",
    "sma_30",
    "vol_ma",
    "number_of_trades"
]

# ─── Ollama ───────────────────────────────────────────────────────────────────
OLLAMA_URL   = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral:7b-instruct-q4_K_M"

# ─── Signal Thresholds ────────────────────────────────────────────────────────
SIGNAL_BUY_THRESHOLD  =  3
SIGNAL_SELL_THRESHOLD = -3

# ─── Sentiment Thresholds ─────────────────────────────────────────────────────
SENTIMENT_BULLISH_THRESHOLD = 0.65
SENTIMENT_BEARISH_THRESHOLD = 0.35

# ─── Whale Known Exchange Addresses ──────────────────────────────────────────
KNOWN_EXCHANGES = {
    "0x28c6c06298d514db089934071355e5743bf21d60": "binance",
    "0x21a31ee1afc51d94c2efccaa2092ad1028285549": "binance",
    "0xbe0eb53f46cd790cd13851d5eff43d12404d33e8": "binance",
    "0xdfd5293d8e347dfe59e90efd55b2956a1343963d": "binance",
}

# ─── Poll Intervals (seconds) ─────────────────────────────────────────────────
SENTIMENT_POLL_INTERVAL = 300    # 5 minutes
WHALE_POLL_INTERVAL     = 60     # 1 minute
SIGNAL_POLL_INTERVAL    = 300    # 5 minutes
