import { useWhales, useSentimentLatest } from "@/hooks/useApi";
import { formatDistanceToNow } from "date-fns";

const WhaleNews = () => {
  const { data: whales, isLoading: whalesLoading } = useWhales();
  const { data: news, isLoading: newsLoading } = useSentimentLatest();

  return (
    <div className="rounded-xl bg-[#111118] border border-gray-800/50 p-5 flex flex-col gap-4">
      {/* ── Whale Activity ── */}
      <div>
        <h2 className="text-sm font-semibold text-gray-200 mb-2">🐋 Whale Activity</h2>
        {whalesLoading && (
          <div className="space-y-1.5">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-5 bg-gray-800/40 rounded animate-pulse" />
            ))}
          </div>
        )}
        {!whalesLoading && (!whales || whales.length === 0) && (
          <p className="text-xs text-gray-500 py-3">No whale activity recorded.</p>
        )}
        <div className="space-y-1">
          {(whales ?? []).slice(0, 5).map((entry: any, i: number) => (
            <div key={i} className="flex items-center justify-between text-xs gap-2 py-1.5 px-2 rounded bg-gray-900/30">
              <span className="font-mono font-medium text-gray-300">
                {entry.value_eth.toFixed(1)} ETH
              </span>
              <span className={`text-[10px] font-medium ${
                entry.direction === "INFLOW" ? "text-red-400" : entry.direction === "OUTFLOW" ? "text-emerald-400" : "text-gray-400"
              }`}>
                {entry.direction === "INFLOW" ? "↓ Inflow" : entry.direction === "OUTFLOW" ? "↑ Outflow" : "— Transfer"}
              </span>
              <span className="text-gray-600 text-[10px] truncate max-w-[80px]">
                {entry.whale_label || entry.whale_signal}
              </span>
              {entry.detected_at && (
                <span className="text-gray-600 text-[10px] shrink-0">
                  {formatDistanceToNow(new Date(entry.detected_at), { addSuffix: true })}
                </span>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* ── News Feed ── */}
      <div className="border-t border-gray-800/40 pt-3">
        <h2 className="text-sm font-semibold text-gray-200 mb-2">📰 Latest News</h2>
        {newsLoading && (
          <div className="space-y-1.5">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-6 bg-gray-800/40 rounded animate-pulse" />
            ))}
          </div>
        )}
        <div className="space-y-1 max-h-48 overflow-y-auto">
          {(news ?? []).slice(0, 8).map((item: any, i: number) => {
            const labelColor =
              item.label === "BULLISH" ? "text-emerald-400"
              : item.label === "BEARISH" || item.label === "FUD" ? "text-red-400"
              : "text-blue-400";
            return (
              <div key={i} className="py-1.5 px-2 rounded bg-gray-900/30 text-xs">
                <div className="flex items-start gap-1.5">
                  <span className={`${labelColor} text-[10px] font-bold shrink-0 mt-0.5`}>●</span>
                  <span className="text-gray-300 leading-snug line-clamp-1">{item.title}</span>
                </div>
                <div className="flex items-center gap-2 mt-0.5 ml-4 text-gray-600">
                  <span className={`${labelColor} text-[10px] font-medium`}>{item.label}</span>
                  <span className="text-[10px]">{item.coin}</span>
                  {item.published_at && (
                    <span className="text-[10px] ml-auto">
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
  );
};

export default WhaleNews;
