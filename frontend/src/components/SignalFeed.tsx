import { useSignals } from "@/hooks/useApi";
import { formatDistanceToNow } from "date-fns";

const SignalFeed = () => {
  const { data, isLoading, error } = useSignals();

  return (
    <div className="rounded-xl bg-[#111118] border border-gray-800/50 p-5 flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-gray-200">⚡ Trading Signals</h2>
        <span className="text-[10px] text-gray-500 uppercase tracking-wider"></span>
      </div>

      {isLoading && (
        <div className="space-y-2">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-14 bg-gray-800/40 rounded-lg animate-pulse" />
          ))}
        </div>
      )}

      {error && (
        <p className="text-xs text-red-400/70 py-4 text-center">⚠ Unable to fetch signals</p>
      )}

      {data && data.length === 0 && (
        <p className="text-xs text-gray-500 py-6 text-center">Waiting for signals...</p>
      )}

      <div className="space-y-2">
        {(data ?? []).map((sig: any, i: number) => {
          const signalColor =
            sig.signal === "BUY" ? "text-emerald-400 bg-emerald-500/10 border-emerald-500/20"
              : sig.signal === "SELL" ? "text-red-400 bg-red-500/10 border-red-500/20"
                : "text-blue-400 bg-blue-500/10 border-blue-500/20";

          const reason = sig.reason_text
            ?.split("\n")
            .filter((l: string) => l.trim().startsWith("-"))
            .slice(0, 2)
            .join(" | ")
            .replace(/^-\s*/gm, "")
            || sig.reason_text?.slice(0, 100);

          return (
            <div key={i} className="p-3 rounded-lg bg-gray-900/40 border border-gray-800/40">
              <div className="flex items-center gap-2 mb-1.5">
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${signalColor}`}>
                  {sig.signal}
                </span>
                <span className="text-xs font-mono text-gray-300 font-medium">{sig.coin}</span>
                <span className="text-[10px] font-mono text-gray-500 px-1.5 py-0.5 rounded bg-gray-800/60">
                  {sig.confidence}%
                </span>
                {sig.whale_signal && (
                  <span className="text-[10px] text-gray-500">
                    🐋 {sig.whale_signal}
                  </span>
                )}
                {sig.generated_at && (
                  <span className="text-[10px] text-gray-600 ml-auto">
                    {formatDistanceToNow(new Date(sig.generated_at), { addSuffix: true })}
                  </span>
                )}
              </div>
              {reason && (
                <p className="text-[11px] text-gray-500 line-clamp-2 leading-relaxed">{reason}</p>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default SignalFeed;
