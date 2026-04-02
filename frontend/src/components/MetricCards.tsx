// MetricCards.tsx — Live metric cards with enhanced styling
import { useSentimentSummary, usePrediction } from "@/hooks/useApi";

const COINS = ["BTC", "ETH", "BNB"];

const COIN_COLORS = {
  BTC: "from-yellow-500/40 to-orange-600/40",
  ETH: "from-purple-500/40 to-blue-600/40",
  BNB: "from-amber-500/40 to-yellow-600/40",
};

const LabelBadge = ({ label }: { label: string }) => {
  const cls =
    label === "BULLISH" ? "bg-green-500/25 text-green-300 border border-green-500/50 shadow-lg shadow-green-500/20"
    : label === "BEARISH" ? "bg-red-500/25 text-red-300 border border-red-500/50 shadow-lg shadow-red-500/20"
    : "bg-blue-500/25 text-blue-300 border border-blue-500/50 shadow-lg shadow-blue-500/20";
  return (
    <span className={`text-xs font-bold px-3 py-1 rounded-full ${cls} backdrop-blur`}>
      {label === "BULLISH" ? "📈" : label === "BEARISH" ? "📉" : "↔️"} {label}
    </span>
  );
};

const CoinCard = ({ coin }: { coin: string }) => {
  const { data: pred, isLoading: predLoading } = usePrediction(coin);
  const { data: summaries, isLoading: sentLoading } = useSentimentSummary();

  const sentiment = summaries?.find((s: any) => s.coin === coin);
  const loading = predLoading || sentLoading;
  const gradient = COIN_COLORS[coin as keyof typeof COIN_COLORS];

  if (loading) {
    return (
      <div className={`relative rounded-2xl bg-gradient-to-br ${gradient} border border-gray-700/50 p-6 animate-pulse backdrop-blur overflow-hidden`}>
        <div className="relative space-y-4">
          <div className="h-5 bg-gray-700/50 rounded-lg w-1/3" />
          <div className="h-8 bg-gray-700/50 rounded-lg w-2/3" />
          <div className="h-4 bg-gray-700/50 rounded-lg w-full" />
        </div>
      </div>
    );
  }

  const price = pred?.current_price ?? 0;
  const change = pred?.change_pct_24h ?? 0;
  const score = sentiment?.avg_score ?? 0.5;
  const label = sentiment?.dominant_label ?? "NEUTRAL";
  const direction = pred?.direction_24h ?? "SIDEWAYS";

  return (
    <div className={`relative rounded-2xl bg-gradient-to-br ${gradient} border border-gray-700/50 p-6 backdrop-blur overflow-hidden group hover:shadow-2xl transition-all`}>
      {/* Glowing background effect */}
      <div className="absolute inset-0 bg-white/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500 blur-xl pointer-events-none" />
      
      <div className="relative space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-sm font-bold text-gray-200 font-mono tracking-widest">
            {coin}/USDT
          </span>
          <LabelBadge label={label} />
        </div>

        <div className="space-y-2">
          <div className="font-mono text-4xl font-black text-white drop-shadow-lg">
            ${price.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          
          <div className="flex items-center gap-2 text-sm">
            <span className={`font-mono font-bold flex items-center gap-1 text-lg ${change >= 0 ? "text-green-300" : "text-red-300"}`}>
              {direction === "UP" ? "📈" : direction === "DOWN" ? "📉" : "➡️"}
              {change >= 0 ? "+" : ""}{change.toFixed(2)}%
            </span>
            <span className="text-xs text-gray-300">24h Change</span>
          </div>
        </div>

        <div className="flex items-center justify-between pt-2 border-t border-white/10">
          <span className="text-xs text-gray-300">Sentiment</span>
          <div className={`px-3 py-1 rounded-full font-mono font-bold text-sm ${
            score > 0.65 ? "bg-green-500/30 text-green-300" : 
            score < 0.4 ? "bg-red-500/30 text-red-300" : 
            "bg-blue-500/30 text-blue-300"
          }`}>
            {score.toFixed(2)}
          </div>
        </div>
      </div>
    </div>
  );
};

const MetricCards = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 px-6">
      {COINS.map((coin) => (
        <CoinCard key={coin} coin={coin} />
      ))}
    </div>
  );
};

export default MetricCards;
