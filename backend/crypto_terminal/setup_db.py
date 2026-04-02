# setup_db.py — Creates all 4 tables in the crypto_terminal database.
# Run ONCE: python setup_db.py
# Prerequisites: postgres superuser must have already run:
#   CREATE DATABASE crypto_terminal;
#   CREATE USER crypto_user WITH PASSWORD 'crypto_pass_123';
#   GRANT ALL PRIVILEGES ON DATABASE crypto_terminal TO crypto_user;

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from db import get_connection

SCHEMA_SQL = """
-- ─── Table 1: LSTM Price Forecasts ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS price_forecasts (
    id              SERIAL PRIMARY KEY,
    coin            VARCHAR(10)    NOT NULL,
    forecasted_at   TIMESTAMPTZ    NOT NULL DEFAULT NOW(),
    current_price   NUMERIC(20,8)  NOT NULL,
    predicted_1h    NUMERIC(20,8),
    predicted_4h    NUMERIC(20,8),
    predicted_24h   NUMERIC(20,8),
    change_pct_1h   NUMERIC(8,4),
    change_pct_4h   NUMERIC(8,4),
    change_pct_24h  NUMERIC(8,4),
    direction_1h    VARCHAR(10),
    direction_4h    VARCHAR(10),
    direction_24h   VARCHAR(10),
    model_used      VARCHAR(30)    DEFAULT 'lstm'
);
CREATE INDEX IF NOT EXISTS idx_fc_coin_time ON price_forecasts(coin, forecasted_at DESC);

-- ─── Table 2: News Sentiment ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS news_sentiment (
    id            SERIAL PRIMARY KEY,
    coin          VARCHAR(10)   NOT NULL,
    published_at  TIMESTAMPTZ   NOT NULL,
    title         TEXT          NOT NULL,
    score         NUMERIC(5,3)  NOT NULL,
    label         VARCHAR(10)   NOT NULL,
    model_used    VARCHAR(40)   DEFAULT 'mistral:7b-instruct-q4_K_M',
    source        VARCHAR(30)   DEFAULT 'cryptopanic',
    created_at    TIMESTAMPTZ   DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_ns_coin_time ON news_sentiment(coin, published_at DESC);

-- ─── Table 3: Whale Transactions ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS whale_transactions (
    id            SERIAL PRIMARY KEY,
    tx_hash       VARCHAR(100)  NOT NULL,
    coin          VARCHAR(10)   NOT NULL DEFAULT 'ETH',
    value_eth     NUMERIC(30,8) NOT NULL,
    from_address  VARCHAR(100)  NOT NULL,
    to_address    VARCHAR(100)  NOT NULL,
    direction     VARCHAR(15),
    whale_signal  VARCHAR(15),
    block_number  BIGINT,
    detected_at   TIMESTAMPTZ   DEFAULT NOW(),
    CONSTRAINT uq_whale_tx UNIQUE (tx_hash)
);
CREATE INDEX IF NOT EXISTS idx_wt_coin_time ON whale_transactions(coin, detected_at DESC);

-- ─── Table 4: Trading Signals (final output) ──────────────────────────────────
CREATE TABLE IF NOT EXISTS signals (
    id                  SERIAL PRIMARY KEY,
    coin                VARCHAR(10)   NOT NULL,
    signal              VARCHAR(5)    NOT NULL,
    confidence          NUMERIC(4,3),
    sentiment_score     NUMERIC(5,3),
    sentiment_label     VARCHAR(10),
    price_direction     VARCHAR(10),
    current_price       NUMERIC(20,8),
    predicted_price_4h  NUMERIC(20,8),
    change_pct_4h       NUMERIC(8,4),
    whale_signal        VARCHAR(15),
    reason_text         TEXT,
    created_at          TIMESTAMPTZ   DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_sig_coin_time ON signals(coin, created_at DESC);
"""


def setup():
    print("🔧 Connecting to crypto_terminal ...")
    try:
        conn = get_connection("crypto_terminal")
        conn.autocommit = True
        cur = conn.cursor()

        print("🔧 Creating tables ...")
        cur.execute(SCHEMA_SQL)

        # Verify tables exist
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = [row[0] for row in cur.fetchall()]

        cur.close()
        conn.close()

        print("✅ Tables created successfully:")
        for t in tables:
            print(f"   • {t}")

    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    setup()
