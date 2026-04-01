import { signals } from "@/data/mockData";

const getTypeBadge = (type: string) => {
  switch (type) {
    case "BUY": return "bg-bullish/15 text-bullish";
    case "SELL": return "bg-bearish/15 text-bearish";
    default: return "bg-neutral/15 text-neutral";
  }
};

const SignalFeed = () => {
  return (
    <div className="bg-card rounded-lg border border-border p-5 h-full">
      <h2 className="text-sm font-semibold text-foreground mb-4">Signal Feed</h2>
      <div className="space-y-3">
        {signals.map((signal, i) => (
          <div key={i} className="flex items-start gap-3 text-sm">
            <span className={`shrink-0 text-xs font-bold px-2 py-0.5 rounded ${getTypeBadge(signal.type)}`}>
              {signal.type}
            </span>
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs text-foreground">{signal.pair}</span>
                <span className="font-mono text-xs text-prediction">{signal.confidence}%</span>
                <span className="text-xs text-muted-foreground ml-auto shrink-0">{signal.time}</span>
              </div>
              <p className="text-xs text-muted-foreground truncate mt-0.5">{signal.reason}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SignalFeed;
