import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
from binance.client import Client
import psycopg2
from psycopg2.extras import execute_batch
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load env
load_dotenv()

api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")
db_host = os.getenv("DB_HOST", "localhost")
db_port = os.getenv("DB_PORT", "5432")
db_user = os.getenv("DB_USER", "postgres")
db_password = os.getenv("DB_PASSWORD", "postgres")
db_name = os.getenv("DB_NAME", "binance_data")

# Initialize Binance client
try:
    client = Client(api_key, api_secret)
    client.ping()
    logger.info("✅ Binance connection successful!")
except Exception as e:
    logger.error(f"❌ Failed to connect to Binance: {e}")
    sys.exit(1)

# Initialize PostgreSQL connection
def connect_db():
    """Create database connection"""
    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name
        )
        logger.info("✅ PostgreSQL connection successful!")
        return conn
    except Exception as e:
        logger.error(f"❌ Failed to connect to PostgreSQL: {e}")
        sys.exit(1)

def create_tables(conn):
    """Create necessary tables if they don't exist"""
    try:
        cursor = conn.cursor()
        
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS klines (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR(20) NOT NULL,
            interval VARCHAR(10) NOT NULL,
            open_time BIGINT NOT NULL,
            open_price DECIMAL(20, 8) NOT NULL,
            high_price DECIMAL(20, 8) NOT NULL,
            low_price DECIMAL(20, 8) NOT NULL,
            close_price DECIMAL(20, 8) NOT NULL,
            volume DECIMAL(20, 8) NOT NULL,
            close_time BIGINT NOT NULL,
            quote_asset_volume DECIMAL(20, 8),
            number_of_trades INTEGER,
            taker_buy_base_asset_volume DECIMAL(20, 8),
            taker_buy_quote_asset_volume DECIMAL(20, 8),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(symbol, interval, open_time)
        );
        """
        
        # Create indexes for better query performance
        create_indexes_sql = """
        CREATE INDEX IF NOT EXISTS idx_symbol_interval ON klines(symbol, interval);
        CREATE INDEX IF NOT EXISTS idx_open_time ON klines(open_time);
        CREATE INDEX IF NOT EXISTS idx_created_at ON klines(created_at);
        """
        
        cursor.execute(create_table_sql)
        cursor.execute(create_indexes_sql)
        conn.commit()
        logger.info("✅ Tables and indexes created successfully!")
        cursor.close()
    except Exception as e:
        logger.error(f"❌ Failed to create tables: {e}")
        conn.close()
        sys.exit(1)

def fetch_last_3_months(symbol="BTCUSDT", interval="15m"):
    """Fetch last 3 months of data from Binance"""
    try:
        end_time = datetime.now()
        start_time = end_time - timedelta(days=90)
        
        logger.info(f"📊 Fetching {symbol} data from {start_time} to {end_time}")
        
        all_klines = []
        current_time = int(start_time.timestamp() * 1000)
        end_timestamp = int(end_time.timestamp() * 1000)
        
        # Fetch data in chunks (Binance limit is 1000 per request)
        batch_count = 0
        while current_time < end_timestamp:
            klines = client.get_klines(
                symbol=symbol,
                interval=interval,
                startTime=current_time,
                limit=1000
            )
            
            if not klines:
                break
            
            all_klines.extend(klines)
            batch_count += 1
            current_time = klines[-1][6] + 1  # Use close_time of last kline
            
            logger.info(f"📥 Fetched batch {batch_count} ({len(all_klines)} total records)")
        
        logger.info(f"✅ Fetched {len(all_klines)} total klines!")
        return all_klines, symbol, interval
    except Exception as e:
        logger.error(f"❌ Failed to fetch data from Binance: {e}")
        return [], symbol, interval

def store_data(conn, klines, symbol, interval):
    """Store klines data in PostgreSQL efficiently using batch insert"""
    if not klines:
        logger.warning("⚠️ No data to store")
        return
    
    try:
        cursor = conn.cursor()
        
        # Prepare data for batch insert with proper type conversion
        data = []
        for kline in klines:
            data.append((
                symbol,
                interval,
                int(kline[0]),             # open_time (BIGINT)
                float(kline[1]),           # open_price
                float(kline[2]),           # high_price
                float(kline[3]),           # low_price
                float(kline[4]),           # close_price
                float(kline[5]),           # volume (base asset volume)
                int(kline[6]),             # close_time (BIGINT)
                float(kline[7]),           # quote_asset_volume
                int(kline[8]),             # number_of_trades (INTEGER)
                float(kline[9]),           # taker_buy_base_asset_volume
                float(kline[10])           # taker_buy_quote_asset_volume
            ))
        
        insert_sql = """
        INSERT INTO klines 
        (symbol, interval, open_time, open_price, high_price, low_price, close_price, 
         volume, close_time, quote_asset_volume, number_of_trades, 
         taker_buy_base_asset_volume, taker_buy_quote_asset_volume)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (symbol, interval, open_time) DO NOTHING;
        """
        
        # Batch insert for efficiency
        execute_batch(cursor, insert_sql, data, page_size=500)
        conn.commit()
        
        logger.info(f"✅ Successfully stored {len(data)} records in PostgreSQL!")
        cursor.close()
    except Exception as e:
        logger.error(f"❌ Failed to store data: {e}")
        conn.rollback()

def get_data_summary(conn, symbol):
    """Get summary of stored data"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                symbol,
                COUNT(*) as total_records,
                MIN(open_time) as earliest_time,
                MAX(open_time) as latest_time,
                MAX(close_price) as highest_price,
                MIN(close_price) as lowest_price,
                AVG(close_price) as avg_price
            FROM klines
            WHERE symbol = %s
            GROUP BY symbol;
        """, (symbol,))
        
        result = cursor.fetchone()
        if result:
            logger.info("\n📈 Data Summary:")
            logger.info(f"   Symbol: {result[0]}")
            logger.info(f"   Total Records: {result[1]}")
            logger.info(f"   Earliest Time: {datetime.fromtimestamp(result[2]/1000)}")
            logger.info(f"   Latest Time: {datetime.fromtimestamp(result[3]/1000)}")
            logger.info(f"   Highest Price: ${result[4]}")
            logger.info(f"   Lowest Price: ${result[5]}")
            logger.info(f"   Average Price: ${result[6]:.2f}\n")
        
        cursor.close()
    except Exception as e:
        logger.error(f"❌ Failed to get summary: {e}")

# Main execution
if __name__ == "__main__":
    logger.info("🚀 Starting Binance data fetcher...\n")
    
    # List of cryptocurrencies to fetch
    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "XRPUSDT", "DOGEUSDT"]
    interval = "15m"
    
    # Connect to database
    conn = connect_db()
    
    # Create tables and indexes
    create_tables(conn)
    
    # Fetch and store data for each cryptocurrency
    for symbol in symbols:
        logger.info(f"\n{'=' * 60}")
        logger.info(f"📊 Processing {symbol}")
        logger.info(f"{'=' * 60}")
        
        # Fetch last 3 months of data
        klines, fetched_symbol, fetched_interval = fetch_last_3_months(symbol, interval)
        
        # Store data in PostgreSQL
        store_data(conn, klines, fetched_symbol, fetched_interval)
        
        # Get and display summary
        get_data_summary(conn, symbol)
    
    # Final summary of all data
    logger.info(f"\n{'=' * 60}")
    logger.info("📈 OVERALL SUMMARY")
    logger.info(f"{'=' * 60}\n")
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                symbol,
                COUNT(*) as total_records,
                MIN(open_time) as earliest_time,
                MAX(open_time) as latest_time,
                MAX(close_price) as highest_price,
                MIN(close_price) as lowest_price,
                AVG(close_price) as avg_price
            FROM klines
            GROUP BY symbol
            ORDER BY symbol;
        """)
        
        results = cursor.fetchall()
        for result in results:
            logger.info(f"\n{result[0]}:")
            logger.info(f"   Total Records: {result[1]}")
            logger.info(f"   Earliest Time: {datetime.fromtimestamp(result[2]/1000)}")
            logger.info(f"   Latest Time: {datetime.fromtimestamp(result[3]/1000)}")
            logger.info(f"   Highest Price: ${result[4]}")
            logger.info(f"   Lowest Price: ${result[5]}")
            logger.info(f"   Average Price: ${result[6]:.2f}")
        
        cursor.close()
    except Exception as e:
        logger.error(f"❌ Failed to get final summary: {e}")
    
    # Close connection
    conn.close()
    logger.info(f"\n✅ All processes completed successfully!")