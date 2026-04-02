// SignalFeed.tsx — Live trading signals from /api/signals
import { useSignals } from "@/hooks/useApi";
import { formatDistanceToNow } from "date-fns";

const SignalBadge = ({ signal }: { signal: string }) => {
  const cls =
    signal === "BUY" ? "bg-bullish/15 text-bullish"
    : signal === "SELL" ? "bg-bearish/15 text-bearish"
    : "bg-neutral/15 text-neutral";
  return (
    <span className={`shrink-0 text-xs font-bold px-2 py-0.5 rounded ${cls}`}>
      {signal}
    </span>
  );
};

const SignalFeed = () => {
  const { data, isLoading, isError, dataUpdatedAt } = useSignals();

  return (
    <div className="bg-card rounded-lg border border-border p-5 h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-semibold text-foreground">Signal Feed</h2>
        {dataUpdatedAt > 0 && (
          <span className="text-xs text-muted-foreground">
            Updated {formatDistanceToNow(dataUpdatedAt, { addSuffix: true })}
          </span>
        )}
      </div>

      {isLoading && (
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-12 bg-muted rounded animate-pulse" />
          ))}
        </div>
      )}

      {isError && (
        <div className="text-xs text-bearish p-3 border border-bearish/20 rounded">
          ⚠️ Unable to fetch signals. Is the backend running?
        </div>
      )}

      {data && data.length === 0 && (
        <p className="text-xs text-muted-foreground">No signals generated yet. Pipelines still warming up.</p>
      )}

      <div className="space-y-4 flex-1 overflow-y-auto">
        {(data ?? []).map((sig: any, i: number) => {
          const reason = sig.reason_text
            ?.split("\n")
            .filter((l: string) => l.trim().startsWith("-"))
            .slice(0, 2)
            .join(" | ")
            .replace(/^-\s*/gm, "")
            || sig.reason_text?.slice(0, 120);

          return (
            <div key={i} className="flex items-start gap-3 text-sm">
              <SignalBadge signal={sig.signal} />
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="font-mono text-xs text-foreground font-bold">{sig.coin}/USDT</span>
                  <span className="font-mono text-xs text-prediction">{sig.confidence}%</span>
                  <span className={`text-xs font-medium ${sig.whale_signal === "Strong Buying" || sig.whale_signal === "Buying" ? "text-bullish" : sig.whale_signal === "Strong Selling" || sig.whale_signal === "Selling" ? "text-bearish" : "text-muted-foreground"}`}>
                    🐋 {sig.whale_signal}
                  </span>
                  {sig.generated_at && (
                    <span className="text-xs text-muted-foreground ml-auto shrink-0">
                      {formatDistanceToNow(new Date(sig.generated_at), { addSuffix: true })}
                    </span>
                  )}
                </div>
                <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">{reason}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default SignalFeed;
