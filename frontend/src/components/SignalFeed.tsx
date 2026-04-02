// SignalFeed.tsx — Live trading signals with enhanced styling
import { useSignals } from "@/hooks/useApi";
import { formatDistanceToNow } from "date-fns";

const SignalBadge = ({ signal }: { signal: string }) => {
  const cls =
    signal === "BUY" ? "bg-green-500/30 text-green-300 border border-green-500/50 shadow-lg shadow-green-500/20"
    : signal === "SELL" ? "bg-red-500/30 text-red-300 border border-red-500/50 shadow-lg shadow-red-500/20"
    : "bg-blue-500/30 text-blue-300 border border-blue-500/50 shadow-lg shadow-blue-500/20";
  return (
    <span className={`shrink-0 text-xs font-bold px-3 py-1 rounded-full backdrop-blur ${cls}`}>
      {signal === "BUY" ? "🟢" : signal === "SELL" ? "🔴" : "⚪"} {signal}
    </span>
  );
};

const SignalFeed = () => {
  const { data, isLoading, isError, dataUpdatedAt } = useSignals();

  return (
    <div className="relative rounded-2xl bg-gradient-to-br from-gray-900/40 to-black/40 border border-gray-800/50 p-6 h-full flex flex-col backdrop-blur backdrop-blur-xl overflow-hidden group hover:shadow-2xl transition-all">
      {/* Glowing effect */}
      <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/10 via-transparent to-blue-500/10 blur-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />

      <div className="relative z-10 flex flex-col h-full gap-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
              ⚡ Trading Signals
            </h2>
            <p className="text-xs text-gray-400 mt-0.5">AI-generated trading signals</p>
          </div>
          {dataUpdatedAt > 0 && (
            <span className="text-xs text-gray-400 whitespace-nowrap">
              {formatDistanceToNow(dataUpdatedAt, { addSuffix: true })}
            </span>
          )}
        </div>

        {isLoading && (
          <div className="space-y-3 flex-1">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-16 bg-gray-700/30 rounded-lg animate-pulse" />
            ))}
          </div>
        )}

        {isError && (
          <div className="text-xs text-red-300 p-4 border border-red-500/30 rounded-lg bg-red-500/10">
            ⚠️ Unable to fetch signals. Backend may be unavailable.
          </div>
        )}

        {data && data.length === 0 && (
          <p className="text-xs text-gray-400 py-8 text-center">Waiting for signals... Pipelines warming up.</p>
        )}

        <div className="space-y-3 flex-1 overflow-y-auto">
          {(data ?? []).map((sig: any, i: number) => {
            const reason = sig.reason_text
              ?.split("\n")
              .filter((l: string) => l.trim().startsWith("-"))
              .slice(0, 2)
              .join(" | ")
              .replace(/^-\s*/gm, "")
              || sig.reason_text?.slice(0, 120);

            return (
              <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-gray-800/50 border border-gray-700/50 hover:bg-gray-800/70 transition-colors">
                <SignalBadge signal={sig.signal} />
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 flex-wrap gap-y-1">
                    <span className="font-mono text-xs font-bold text-cyan-300">{sig.coin}</span>
                    <span className="font-mono text-xs px-2 py-0.5 rounded bg-purple-500/20 text-purple-300">{sig.confidence}%</span>
                    <span className={`text-xs font-bold ${
                      sig.whale_signal === "Strong Buying" || sig.whale_signal === "Buying" ? "text-green-300" : 
                      sig.whale_signal === "Strong Selling" || sig.whale_signal === "Selling" ? "text-red-300" : 
                      "text-gray-400"
                    }`}>
                      🐋 {sig.whale_signal}
                    </span>
                    {sig.generated_at && (
                      <span className="text-xs text-gray-400 ml-auto shrink-0">
                        {formatDistanceToNow(new Date(sig.generated_at), { addSuffix: true })}
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-gray-400 mt-1 line-clamp-2">{reason}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default SignalFeed;
