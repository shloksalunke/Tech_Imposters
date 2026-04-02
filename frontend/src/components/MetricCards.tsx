import { useSentimentSummary, usePrediction } from "@/hooks/useApi";

const COINS = ["BTC", "ETH", "BNB"];

const CoinCard = ({ coin }: { coin: string }) => {
  const { data: pred, isLoading: predLoading } = usePrediction(coin);
  const { data: summaries, isLoading: sentLoading } = useSentimentSummary();

  const sentiment = summaries?.find((s: any) => s.coin === coin);
  const loading = predLoading || sentLoading;

  if (loading) {
    return (
      <div className="rounded-xl bg-[#111118] border border-gray-800/50 p-5 animate-pulse">
        <div className="h-4 bg-gray-800 rounded w-20 mb-3" />
        <div className="h-7 bg-gray-800 rounded w-32 mb-2" />
        <div className="h-3 bg-gray-800 rounded w-24" />
      </div>
    );
  }

  const price = pred?.current_price ?? 0;
  const change = pred?.change_pct_24h ?? 0;
  const score = sentiment?.avg_score ?? 0.5;
  const label = sentiment?.dominant_label ?? "NEUTRAL";
  const direction = pred?.direction_24h ?? "SIDEWAYS";

  const labelColor =
    label === "BULLISH" ? "text-emerald-400 bg-emerald-500/10 border-emerald-500/20"
    : label === "BEARISH" ? "text-red-400 bg-red-500/10 border-red-500/20"
    : "text-blue-400 bg-blue-500/10 border-blue-500/20";

  return (
    <div className="rounded-xl bg-[#111118] border border-gray-800/50 p-5 hover:border-gray-700/60 transition-colors">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-medium text-gray-400 tracking-wide">{coin}/USDT</span>
        <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${labelColor}`}>
          {label}
        </span>
      </div>

      <div className="text-2xl font-bold text-gray-100 font-mono tracking-tight">
        ${price.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
      </div>

      <div className="flex items-center justify-between mt-2">
        <span className={`text-sm font-mono font-medium ${change >= 0 ? "text-emerald-400" : "text-red-400"}`}>
          {direction === "UP" ? "↑" : direction === "DOWN" ? "↓" : "→"}{" "}
          {change >= 0 ? "+" : ""}{change.toFixed(2)}%
        </span>
        <span className="text-xs text-gray-500">
          Score: <span className={`font-mono font-medium ${score > 0.65 ? "text-emerald-400" : score < 0.4 ? "text-red-400" : "text-blue-400"}`}>
            {score.toFixed(2)}
          </span>
        </span>
      </div>
    </div>
  );
};

const MetricCards = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {COINS.map((coin) => (
        <CoinCard key={coin} coin={coin} />
      ))}
    </div>
  );
};

export default MetricCards;
