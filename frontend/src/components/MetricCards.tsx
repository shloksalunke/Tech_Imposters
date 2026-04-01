import { coins } from "@/data/mockData";

const getSentimentColor = (sentiment: string) => {
  switch (sentiment) {
    case "BULLISH": return "text-bullish";
    case "BEARISH": return "text-bearish";
    default: return "text-neutral";
  }
};

const getSentimentBg = (sentiment: string) => {
  switch (sentiment) {
    case "BULLISH": return "bg-bullish/15 text-bullish";
    case "BEARISH": return "bg-bearish/15 text-bearish";
    default: return "bg-neutral/15 text-neutral";
  }
};

const MetricCards = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 px-6">
      {coins.map((coin) => (
        <div
          key={coin.pair}
          className="bg-card rounded-lg border border-border p-5"
        >
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-medium text-muted-foreground">{coin.pair}</span>
            <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${getSentimentBg(coin.sentiment)}`}>
              {coin.sentiment}
            </span>
          </div>
          <div className="font-mono text-2xl font-bold text-foreground mb-1">
            ${coin.price.toLocaleString("en-US", { minimumFractionDigits: 2 })}
          </div>
          <div className="flex items-center justify-between">
            <span className={`font-mono text-sm font-medium ${coin.change24h >= 0 ? "text-bullish" : "text-bearish"}`}>
              {coin.change24h >= 0 ? "+" : ""}{coin.change24h}%
            </span>
            <span className="text-xs text-muted-foreground">
              Score: <span className={`font-mono ${getSentimentColor(coin.sentiment)}`}>{coin.sentimentScore.toFixed(2)}</span>
            </span>
          </div>
        </div>
      ))}
    </div>
  );
};

export default MetricCards;
