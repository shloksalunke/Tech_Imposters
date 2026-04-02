// CryptoHeatmaps.tsx — 3 separate glowing heatmaps for BTC, ETH, BNB
import { useSentimentSummary } from "@/hooks/useApi";

const COINS = ["BTC", "ETH", "BNB"];
const COIN_COLORS = {
  BTC: { glow: "from-yellow-500/40 to-orange-600/40", border: "border-yellow-500/30", text: "text-yellow-400", bg: "bg-yellow-500/5" },
  ETH: { glow: "from-purple-500/40 to-blue-600/40", border: "border-purple-500/30", text: "text-purple-400", bg: "bg-purple-500/5" },
  BNB: { glow: "from-amber-500/40 to-yellow-600/40", border: "border-amber-500/30", text: "text-amber-400", bg: "bg-amber-500/5" },
};

const getCellColor = (value: number, type: string) => {
  if (type === "avg_score") {
    if (value >= 0.65) return "bg-green-500/30 text-green-300";
    if (value <= 0.4) return "bg-red-500/30 text-red-300";
    return "bg-blue-500/20 text-blue-300";
  }
  if (type === "bullish") {
    if (value >= 60) return "bg-green-500/30 text-green-300";
    if (value <= 30) return "bg-gray-500/20 text-gray-300";
    return "bg-blue-500/20 text-blue-300";
  }
  if (type === "bearish") {
    if (value >= 60) return "bg-red-500/30 text-red-300";
    if (value <= 30) return "bg-green-500/20 text-green-300";
    return "bg-blue-500/20 text-blue-300";
  }
  return "bg-gray-500/20 text-gray-300";
};

const HeatmapCard = ({ coin, data }: { coin: string; data: any }) => {
  const colors = COIN_COLORS[coin as keyof typeof COIN_COLORS];
  
  if (!data) {
    return (
      <div className={`relative rounded-2xl border ${colors.border} ${colors.bg} p-6 backdrop-blur overflow-hidden group`}>
        <div className={`absolute inset-0 bg-gradient-to-br ${colors.glow} blur-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none`} />
        <div className="relative space-y-4">
          <h3 className={`text-lg font-bold ${colors.text}`}>{coin}/USDT</h3>
          <div className="space-y-2">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-10 bg-gray-700/30 rounded-lg animate-pulse" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`relative rounded-2xl border ${colors.border} ${colors.bg} p-6 backdrop-blur overflow-hidden group transition-all hover:shadow-2xl`}>
      <div className={`absolute inset-0 bg-gradient-to-br ${colors.glow} blur-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none`} />
      <div className="relative space-y-4">
        <h3 className={`text-lg font-bold ${colors.text} flex items-center gap-2`}>
          <span className="animate-pulse">◆</span>
          {coin}/USDT
        </h3>
        
        <div className="space-y-3">
          {/* Avg Score */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs">
              <span className="text-gray-400">Sentiment Score</span>
              <span className="font-mono font-bold text-foreground">{data.avg_score.toFixed(2)}</span>
            </div>
            <div className={`rounded-lg py-2 px-3 font-mono text-sm font-bold text-center ${getCellColor(data.avg_score, "avg_score")} transition-colors`}>
              {data.avg_score.toFixed(2)}
            </div>
          </div>

          {/* Bullish % */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs">
              <span className="text-gray-400">Bullish</span>
              <span className="font-mono text-green-400">{data.bullish_pct}%</span>
            </div>
            <div className="bg-gray-800/50 rounded-lg h-2 overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-green-500 to-green-400 transition-all duration-300"
                style={{ width: `${data.bullish_pct}%` }}
              />
            </div>
          </div>

          {/* Bearish % */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs">
              <span className="text-gray-400">Bearish</span>
              <span className="font-mono text-red-400">{data.bearish_pct}%</span>
            </div>
            <div className="bg-gray-800/50 rounded-lg h-2 overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-red-500 to-red-400 transition-all duration-300"
                style={{ width: `${data.bearish_pct}%` }}
              />
            </div>
          </div>

          {/* News Count */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs">
              <span className="text-gray-400">News Count</span>
              <span className="font-mono font-bold">{data.total_news}</span>
            </div>
            <div className="bg-blue-500/20 rounded-lg py-2 px-3 text-center text-xs font-bold text-blue-400">
              {data.total_news} {data.total_news === 1 ? "article" : "articles"}
            </div>
          </div>

          {/* Dominant Label */}
          <div className={`rounded-lg py-2 px-3 text-center text-sm font-bold transition-colors ${
            data.dominant_label === "BULLISH" ? "bg-green-500/20 text-green-300" :
            data.dominant_label === "BEARISH" ? "bg-red-500/20 text-red-300" :
            "bg-blue-500/20 text-blue-300"
          }`}>
            {data.dominant_label === "BULLISH" ? "📈" : data.dominant_label === "BEARISH" ? "📉" : "↔️"} {data.dominant_label}
          </div>
        </div>
      </div>
    </div>
  );
};

const CryptoHeatmaps = () => {
  const { data: summaries, isLoading } = useSentimentSummary();

  return (
    <div className="rounded-2xl bg-gradient-to-br from-gray-900/20 to-black/20 border border-gray-800/50 p-8 space-y-6 backdrop-blur">
      <div className="space-y-2">
        <h2 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
          🔥 Market Sentiment Heatmaps
        </h2>
        <p className="text-sm text-gray-400">Real-time sentiment analysis across top cryptocurrencies</p>
      </div>

      {isLoading && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {COINS.map((coin) => (
            <div key={coin} className="animate-pulse">
              <HeatmapCard coin={coin} data={null} />
            </div>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {COINS.map((coin) => {
          const coinData = summaries?.find((s: any) => s.coin === coin);
          return (
            <HeatmapCard key={coin} coin={coin} data={coinData} />
          );
        })}
      </div>

      {summaries && summaries.length === 0 && (
        <div className="text-center py-12 text-gray-400">
          <p>No sentiment data available yet. Pipelines warming up...</p>
        </div>
      )}
    </div>
  );
};

export default CryptoHeatmaps;
