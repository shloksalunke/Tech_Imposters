// WhaleNews.tsx — Live whale transactions + news feed from APIs
import { useWhales, useSentimentLatest } from "@/hooks/useApi";
import { formatDistanceToNow } from "date-fns";

const WhaleNews = () => {
  const { data: whales, isLoading: whalesLoading } = useWhales();
  const { data: news, isLoading: newsLoading } = useSentimentLatest();

  return (
    <div className="bg-card rounded-lg border border-border p-5 h-full flex flex-col gap-5">

      {/* ── Whale Activity ───────────────────────────────────────── */}
      <div>
        <h2 className="text-sm font-semibold text-foreground mb-3">🐋 Whale Activity</h2>
        {whalesLoading && (
          <div className="space-y-2">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-5 bg-muted rounded animate-pulse" />
            ))}
          </div>
        )}
        {!whalesLoading && (!whales || whales.length === 0) && (
          <p className="text-xs text-muted-foreground">No whale activity recorded yet.</p>
        )}
        <div className="space-y-2">
          {(whales ?? []).slice(0, 6).map((entry: any, i: number) => (
            <div key={i} className="flex items-center justify-between text-xs gap-2">
              <span className="font-mono text-foreground font-medium whitespace-nowrap">
                {entry.value_eth.toFixed(1)} ETH
              </span>
              <span className={`font-medium whitespace-nowrap ${
                entry.direction === "INFLOW" ? "text-bearish" : "text-bullish"
              }`}>
                {entry.direction === "INFLOW" ? "↓ Inflow" : "↑ Outflow"}
              </span>
              <span className="text-muted-foreground truncate max-w-[80px]" title={entry.whale_label}>
                {entry.whale_label || entry.from_address}
              </span>
              {entry.detected_at && (
                <span className="text-muted-foreground whitespace-nowrap shrink-0">
                  {formatDistanceToNow(new Date(entry.detected_at), { addSuffix: true })}
                </span>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* ── News Feed ────────────────────────────────────────────── */}
      <div className="flex-1 min-h-0">
        <h2 className="text-sm font-semibold text-foreground mb-3">📰 News</h2>
        {newsLoading && (
          <div className="space-y-3">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-8 bg-muted rounded animate-pulse" />
            ))}
          </div>
        )}
        <div className="space-y-2 overflow-y-auto max-h-52">
          {(news ?? []).slice(0, 12).map((item: any, i: number) => {
            const dotColor =
              item.label === "BULLISH" ? "text-bullish"
              : item.label === "BEARISH" || item.label === "FUD" ? "text-bearish"
              : "text-neutral";
            return (
              <div key={i} className="text-xs">
                <div className="flex items-center gap-2">
                  <span className={`font-medium shrink-0 ${dotColor}`}>●</span>
                  <span className="text-foreground truncate">{item.title}</span>
                </div>
                <div className="flex items-center gap-2 mt-0.5 ml-4">
                  <span className="text-muted-foreground font-mono">{item.coin}</span>
                  <span className="text-muted-foreground">· {item.source}</span>
                  {item.published_at && (
                    <span className="text-muted-foreground ml-auto whitespace-nowrap">
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
