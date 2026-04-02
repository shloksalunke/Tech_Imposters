// MetricCards.tsx — Live metric cards from prediction + sentiment APIs
import { useSentimentSummary, usePrediction } from "@/hooks/useApi";

const COINS = ["BTC", "ETH", "BNB"];

const LabelBadge = ({ label }: { label: string }) => {
  const cls =
    label === "BULLISH" ? "bg-bullish/15 text-bullish"
    : label === "BEARISH" ? "bg-bearish/15 text-bearish"
    : "bg-neutral/15 text-neutral";
  return (
    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${cls}`}>
      {label}
    </span>
  );
};

const CoinCard = ({ coin }: { coin: string }) => {
  const { data: pred, isLoading: predLoading } = usePrediction(coin);
  const { data: summaries, isLoading: sentLoading } = useSentimentSummary();

  const sentiment = summaries?.find((s: any) => s.coin === coin);
  const loading = predLoading || sentLoading;

  if (loading) {
    return (
      <div className="bg-card rounded-lg border border-border p-5 animate-pulse">
        <div className="h-4 bg-muted rounded w-1/2 mb-3" />
        <div className="h-8 bg-muted rounded w-3/4 mb-2" />
        <div className="h-3 bg-muted rounded w-full" />
      </div>
    );
  }

  const price = pred?.current_price ?? 0;
  const change = pred?.change_pct_24h ?? 0;
  const score = sentiment?.avg_score ?? 0.5;
  const label = sentiment?.dominant_label ?? "NEUTRAL";
  const direction = pred?.direction_24h ?? "SIDEWAYS";

  return (
    <div className="bg-card rounded-lg border border-border p-5">
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm font-medium text-muted-foreground font-mono">
          {coin}/USDT
        </span>
        <LabelBadge label={label} />
      </div>
      <div className="font-mono text-2xl font-bold text-foreground mb-1">
        ${price.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
      </div>
      <div className="flex items-center justify-between">
        <span className={`font-mono text-sm font-medium flex items-center gap-1 ${change >= 0 ? "text-bullish" : "text-bearish"}`}>
          {direction === "UP" ? "↑" : direction === "DOWN" ? "↓" : "→"}
          {change >= 0 ? "+" : ""}{change.toFixed(2)}% 24h
        </span>
        <span className="text-xs text-muted-foreground">
          Score: <span className={`font-mono font-medium ${score > 0.65 ? "text-bullish" : score < 0.4 ? "text-bearish" : "text-neutral"}`}>
            {score.toFixed(2)}
          </span>
        </span>
      </div>
    </div>
  );
};

const MetricCards = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 px-6">
      {COINS.map((coin) => (
        <CoinCard key={coin} coin={coin} />
      ))}
    </div>
  );
};

export default MetricCards;
