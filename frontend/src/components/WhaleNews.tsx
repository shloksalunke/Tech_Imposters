// WhaleNews.tsx — Live whale transactions + news with enhanced styling
import { useWhales, useSentimentLatest } from "@/hooks/useApi";
import { formatDistanceToNow } from "date-fns";

const WhaleNews = () => {
  const { data: whales, isLoading: whalesLoading } = useWhales();
  const { data: news, isLoading: newsLoading } = useSentimentLatest();

  return (
    <div className="relative rounded-2xl bg-gradient-to-br from-gray-900/40 to-black/40 border border-gray-800/50 p-6 h-full flex flex-col gap-6 backdrop-blur overflow-hidden group hover:shadow-2xl transition-all">
      {/* Glowing effect */}
      <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/10 via-transparent to-pink-500/10 blur-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />

      <div className="relative z-10">
        {/* ── Whale Activity ───────────────────────────────────────── */}
        <div className="space-y-3">
          <h2 className="text-lg font-bold bg-gradient-to-r from-cyan-400 to-teal-400 bg-clip-text text-transparent">
            🐋 Whale Activity
          </h2>
          {whalesLoading && (
            <div className="space-y-2">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="h-6 bg-gray-700/30 rounded-lg animate-pulse" />
              ))}
            </div>
          )}
          {!whalesLoading && (!whales || whales.length === 0) && (
            <p className="text-xs text-gray-400 py-4">No whale activity recorded yet.</p>
          )}
          <div className="space-y-2">
            {(whales ?? []).slice(0, 5).map((entry: any, i: number) => (
              <div key={i} className="flex items-center justify-between text-xs gap-2 p-2 rounded-lg bg-gray-800/40 border border-gray-700/50 hover:bg-gray-800/60 transition-colors">
                <span className="font-mono font-bold text-cyan-300">
                  {entry.value_eth.toFixed(1)} ETH
                </span>
                <span className={`font-bold whitespace-nowrap px-2 py-0.5 rounded ${
                  entry.direction === "INFLOW" ? "bg-red-500/20 text-red-300" : "bg-green-500/20 text-green-300"
                }`}>
                  {entry.direction === "INFLOW" ? "⬇️ Inflow" : "⬆️ Outflow"}
                </span>
                <span className="text-gray-400 truncate max-w-[100px]" title={entry.whale_label}>
                  {entry.whale_label || entry.from_address}
                </span>
                {entry.detected_at && (
                  <span className="text-gray-500 whitespace-nowrap shrink-0 text-xs">
                    {formatDistanceToNow(new Date(entry.detected_at), { addSuffix: true })}
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* ── News Feed ────────────────────────────────────────────── */}
        <div className="flex-1 min-h-0 space-y-3 border-t border-gray-700/50 pt-6">
          <h2 className="text-lg font-bold bg-gradient-to-r from-amber-400 to-orange-400 bg-clip-text text-transparent">
            📰 Sentiment News
          </h2>
          {newsLoading && (
            <div className="space-y-2">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="h-8 bg-gray-700/30 rounded-lg animate-pulse" />
              ))}
            </div>
          )}
          <div className="space-y-2 overflow-y-auto max-h-64">
            {(news ?? []).slice(0, 10).map((item: any, i: number) => {
              const dotColor =
                item.label === "BULLISH" ? "bg-green-500 text-green-300"
                : item.label === "BEARISH" || item.label === "FUD" ? "bg-red-500 text-red-300"
                : "bg-blue-500 text-blue-300";
              return (
                <div key={i} className="text-xs p-2 rounded-lg bg-gray-800/40 border border-gray-700/50 hover:bg-gray-800/60 transition-colors">
                  <div className="flex items-start gap-2">
                    <span className={`font-bold shrink-0 text-sm ${dotColor}`}>●</span>
                    <span className="text-foreground font-medium truncate flex-1">{item.title}</span>
                  </div>
                  <div className="flex items-center gap-2 mt-1 ml-4 text-gray-400">
                    <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                      item.label === "BULLISH" ? "bg-green-500/20 text-green-300" :
                      item.label === "BEARISH" ? "bg-red-500/20 text-red-300" :
                      "bg-blue-500/20 text-blue-300"
                    }`}>
                      {item.label}
                    </span>
                    <span className="font-mono">{item.coin}</span>
                    <span>·</span>
                    <span className="truncate">{item.source}</span>
                    {item.published_at && (
                      <span className="ml-auto whitespace-nowrap text-xs">
                        {formatDistanceToNow(new Date(item.published_at), { addSuffix: true })}
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default WhaleNews;
