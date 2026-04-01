-- ================================================================
-- CRYPTO TERMINAL — FULL SCHEMA
-- Covers: Binance (script.py) + CryptoPanic (panic.py) + Etherscan (test.py)
-- ================================================================

-- ────────────────────────────────────────────────────────────────
-- 1. BINANCE MARKET DATA  (script.py writes here)
--    One table per coin — matches script.py table_name pattern
-- ────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS market_data_btcusdt (
    id                SERIAL PRIMARY KEY,
    open_time         BIGINT      NOT NULL,   -- ms epoch from Binance d[0]
    open_price        NUMERIC(20,8) NOT NULL,
    high_price        NUMERIC(20,8) NOT NULL,
    low_price         NUMERIC(20,8) NOT NULL,
    close_price       NUMERIC(20,8) NOT NULL,
    volume            NUMERIC(30,8) NOT NULL,
    close_time        BIGINT      NOT NULL,   -- ms epoch from Binance d[6]
    number_of_trades  INT         NOT NULL,
    created_at        TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_btc_open_time UNIQUE (open_time)
);

CREATE TABLE IF NOT EXISTS market_data_ethusdt (
    id                SERIAL PRIMARY KEY,
    open_time         BIGINT      NOT NULL,
    open_price        NUMERIC(20,8) NOT NULL,
    high_price        NUMERIC(20,8) NOT NULL,
    low_price         NUMERIC(20,8) NOT NULL,
    close_price       NUMERIC(20,8) NOT NULL,
    volume            NUMERIC(30,8) NOT NULL,
    close_time        BIGINT      NOT NULL,
    number_of_trades  INT         NOT NULL,
    created_at        TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_eth_open_time UNIQUE (open_time)
);

CREATE TABLE IF NOT EXISTS market_data_bnbusdt (
    id                SERIAL PRIMARY KEY,
    open_time         BIGINT      NOT NULL,
    open_price        NUMERIC(20,8) NOT NULL,
    high_price        NUMERIC(20,8) NOT NULL,
    low_price         NUMERIC(20,8) NOT NULL,
    close_price       NUMERIC(20,8) NOT NULL,
    volume            NUMERIC(30,8) NOT NULL,
    close_time        BIGINT      NOT NULL,
    number_of_trades  INT         NOT NULL,
    created_at        TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_bnb_open_time UNIQUE (open_time)
);

-- Indexes for Prophet — it queries by time range
CREATE INDEX IF NOT EXISTS idx_btc_open_time ON market_data_btcusdt(open_time DESC);
CREATE INDEX IF NOT EXISTS idx_eth_open_time ON market_data_ethusdt(open_time DESC);
CREATE INDEX IF NOT EXISTS idx_bnb_open_time ON market_data_bnbusdt(open_time DESC);


-- ────────────────────────────────────────────────────────────────
-- 2. CRYPTOPANIC NEWS SENTIMENT  (panic.py writes here)
--    Matches: Date, Time, News(title), Score, Sentiment(label)
--    + we add coin and model_used columns
-- ────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS news_sentiment (
    id            SERIAL PRIMARY KEY,
    coin          VARCHAR(10)   NOT NULL,   -- 'BTC', 'ETH', 'BNB', etc.
    published_at  TIMESTAMPTZ   NOT NULL,   -- Date + Time merged from panic.py
    title         TEXT          NOT NULL,   -- "News" column from panic.py
    score         NUMERIC(5,3)  NOT NULL,   -- 0.000 – 1.000
    label         VARCHAR(10)   NOT NULL,   -- BULLISH / BEARISH / NEUTRAL / FUD
    model_used    VARCHAR(30)   DEFAULT 'mistral:7b-instruct-q4_K_M',
    source        VARCHAR(30)   DEFAULT 'cryptopanic',
    created_at    TIMESTAMPTZ   DEFAULT NOW()
);

-- Signal generator queries: WHERE coin='BTC' AND published_at > NOW()-'2 hours'
CREATE INDEX IF NOT EXISTS idx_news_coin_time  ON news_sentiment(coin, published_at DESC);
CREATE INDEX IF NOT EXISTS idx_news_label      ON news_sentiment(label);


-- ────────────────────────────────────────────────────────────────
-- 3. ETHERSCAN WHALE TRANSACTIONS  (test.py writes here)
--    Matches: value_eth, tx['from'], tx['to'], tx['hash']
-- ────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS whale_transactions (
    id              SERIAL PRIMARY KEY,
    tx_hash         VARCHAR(100)  NOT NULL,   -- tx['hash'] — unique per tx
    coin            VARCHAR(10)   NOT NULL DEFAULT 'ETH',
    value_eth       NUMERIC(30,8) NOT NULL,   -- int(tx['value']) / 10**18
    from_address    VARCHAR(100)  NOT NULL,   -- tx['from']
    to_address      VARCHAR(100)  NOT NULL,   -- tx['to']
    direction       VARCHAR(15),              -- 'INFLOW' or 'OUTFLOW' (vs exchange)
    whale_signal    VARCHAR(15),              -- 'ACCUMULATING' or 'DISTRIBUTING'
    block_number    BIGINT,
    detected_at     TIMESTAMPTZ   DEFAULT NOW(),
    CONSTRAINT uq_tx_hash UNIQUE (tx_hash)   -- ON CONFLICT DO NOTHING works here
);

-- Signal generator queries: WHERE coin='ETH' AND detected_at > NOW()-'6 hours'
CREATE INDEX IF NOT EXISTS idx_whale_coin_time ON whale_transactions(coin, detected_at DESC);
CREATE INDEX IF NOT EXISTS idx_whale_direction ON whale_transactions(direction);


-- ────────────────────────────────────────────────────────────────
-- 4. SIGNALS  (signal_generator.py writes here, dashboard reads)
-- ────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS signals (
    id                  SERIAL PRIMARY KEY,
    coin                VARCHAR(10)   NOT NULL,
    signal              VARCHAR(5)    NOT NULL,   -- 'BUY', 'SELL', 'HOLD'
    confidence          NUMERIC(3,2),             -- 0.00 – 1.00
    sentiment_score     NUMERIC(5,3),             -- avg score used
    sentiment_label     VARCHAR(10),              -- dominant label
    price_direction     VARCHAR(10),              -- 'UP', 'DOWN', 'SIDEWAYS'
    predicted_price_4h  NUMERIC(20,8),            -- Prophet yhat 4h ahead
    current_price       NUMERIC(20,8),            -- price at signal time
    whale_signal        VARCHAR(15),              -- 'ACCUMULATING' etc.
    reason_text         TEXT,                     -- human-readable explanation
    created_at          TIMESTAMPTZ   DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_signals_coin_time ON signals(coin, created_at DESC);


-- ────────────────────────────────────────────────────────────────
-- 5. QUICK VERIFY — row counts after seeding
-- ────────────────────────────────────────────────────────────────

SELECT 'market_data_btcusdt' AS table_name, COUNT(*) FROM market_data_btcusdt
UNION ALL
SELECT 'market_data_ethusdt',               COUNT(*) FROM market_data_ethusdt
UNION ALL
SELECT 'market_data_bnbusdt',               COUNT(*) FROM market_data_bnbusdt
UNION ALL
SELECT 'news_sentiment',                    COUNT(*) FROM news_sentiment
UNION ALL
SELECT 'whale_transactions',               COUNT(*) FROM whale_transactions
UNION ALL
SELECT 'signals',                           COUNT(*) FROM signals;