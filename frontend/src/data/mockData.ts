export interface CoinData {
  pair: string;
  symbol: string;
  price: number;
  change24h: number;
  sentiment: "BULLISH" | "BEARISH" | "NEUTRAL";
  sentimentScore: number;
}

export interface Signal {
  type: "BUY" | "SELL" | "HOLD";
  pair: string;
  confidence: number;
  reason: string;
  time: string;
}

export interface WhaleEntry {
  amount: string;
  direction: "inflow" | "outflow";
  exchange: string;
  time: string;
}

export interface NewsItem {
  title: string;
  sentiment: "BULLISH" | "BEARISH" | "NEUTRAL";
  source: string;
  time: string;
}

export const coins: CoinData[] = [
  { pair: "BTCUSDT", symbol: "BTC", price: 67842.5, change24h: 2.34, sentiment: "BULLISH", sentimentScore: 0.82 },
  { pair: "ETHUSDT", symbol: "ETH", price: 3521.18, change24h: -1.12, sentiment: "NEUTRAL", sentimentScore: 0.51 },
  { pair: "BNBUSDT", symbol: "BNB", price: 612.45, change24h: 0.78, sentiment: "BULLISH", sentimentScore: 0.68 },
];

export const heatmapData: Record<string, number[]> = {
  BTC: [0.78, 0.82, 0.75, 0.88, 0.91, 0.82],
  ETH: [0.55, 0.48, 0.52, 0.45, 0.58, 0.51],
  BNB: [0.62, 0.71, 0.65, 0.58, 0.72, 0.68],
};

export const heatmapLabels = ["-5h", "-4h", "-3h", "-2h", "-1h", "Now"];

export const signals: Signal[] = [
  { type: "BUY", pair: "BTCUSDT", confidence: 87, reason: "Strong bullish divergence on 4H RSI", time: "2m ago" },
  { type: "SELL", pair: "ETHUSDT", confidence: 72, reason: "Death cross forming on daily MA", time: "5m ago" },
  { type: "HOLD", pair: "BNBUSDT", confidence: 65, reason: "Consolidation near support level", time: "8m ago" },
  { type: "BUY", pair: "BTCUSDT", confidence: 91, reason: "Whale accumulation detected", time: "12m ago" },
  { type: "SELL", pair: "ETHUSDT", confidence: 68, reason: "Bearish engulfing on 1H candle", time: "18m ago" },
  { type: "BUY", pair: "BNBUSDT", confidence: 76, reason: "Breakout above key resistance", time: "25m ago" },
  { type: "HOLD", pair: "BTCUSDT", confidence: 58, reason: "Low volume, waiting for confirmation", time: "32m ago" },
];

export const priceHistory = {
  "1H": Array.from({ length: 12 }, (_, i) => ({
    time: `${i * 5}m`,
    price: 67000 + Math.sin(i * 0.5) * 400 + i * 50,
    prediction: i >= 8 ? 67000 + Math.sin(i * 0.5) * 400 + i * 50 + (i - 8) * 120 : undefined,
  })),
  "4H": Array.from({ length: 16 }, (_, i) => ({
    time: `${i * 15}m`,
    price: 66500 + Math.sin(i * 0.4) * 600 + i * 80,
    prediction: i >= 12 ? 66500 + Math.sin(i * 0.4) * 600 + i * 80 + (i - 12) * 150 : undefined,
  })),
  "24H": Array.from({ length: 24 }, (_, i) => ({
    time: `${i}h`,
    price: 65000 + Math.sin(i * 0.3) * 1200 + i * 100,
    prediction: i >= 20 ? 65000 + Math.sin(i * 0.3) * 1200 + i * 100 + (i - 20) * 200 : undefined,
  })),
};

export const whaleActivity: WhaleEntry[] = [
  { amount: "1,250 BTC", direction: "inflow", exchange: "Binance", time: "3m ago" },
  { amount: "8,400 ETH", direction: "outflow", exchange: "Coinbase", time: "11m ago" },
  { amount: "45,000 BNB", direction: "inflow", exchange: "Binance", time: "24m ago" },
  { amount: "520 BTC", direction: "outflow", exchange: "Kraken", time: "38m ago" },
];

export const news: NewsItem[] = [
  { title: "Bitcoin ETF inflows hit record $1.2B in single day", sentiment: "BULLISH", source: "CoinDesk", time: "15m" },
  { title: "SEC delays decision on Ethereum spot ETF", sentiment: "BEARISH", source: "Bloomberg", time: "32m" },
  { title: "BNB Chain launches new DeFi incentive program", sentiment: "BULLISH", source: "CryptoSlate", time: "1h" },
  { title: "Fed signals potential rate pause in upcoming meeting", sentiment: "NEUTRAL", source: "Reuters", time: "2h" },
  { title: "Major exchange reports security vulnerability patched", sentiment: "BEARISH", source: "TheBlock", time: "3h" },
];
