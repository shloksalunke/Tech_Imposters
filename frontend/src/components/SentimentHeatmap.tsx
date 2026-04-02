// SentimentHeatmap.tsx — Live sentiment heatmap from /api/sentiment/summary
import { useSentimentSummary } from "@/hooks/useApi";
import { formatDistanceToNow } from "date-fns";

const LABELS = ["Avg Score", "Bullish %", "Bearish %", "News Count"];

const getCellColor = (value: number, type: string) => {
  if (type === "Avg Score") {
    if (value >= 0.65) return "bg-bullish/30 text-bullish";
    if (value <= 0.4)  return "bg-bearish/30 text-bearish";
    return "bg-neutral/20 text-neutral";
  }
  if (type === "Bullish %") {
    if (value >= 60) return "bg-bullish/30 text-bullish";
    if (value <= 30) return "bg-bearish/20 text-muted-foreground";
    return "bg-neutral/10 text-neutral";
  }
  if (type === "Bearish %") {
    if (value >= 60) return "bg-bearish/30 text-bearish";
    if (value <= 30) return "bg-bullish/20 text-muted-foreground";
    return "bg-neutral/10 text-neutral";
  }
  return "bg-muted/20 text-muted-foreground";
};

const SentimentHeatmap = () => {
  const { data, isLoading, isError, dataUpdatedAt } = useSentimentSummary();

  return (
    <div className="bg-card rounded-lg border border-border p-5 h-full">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-semibold text-foreground">Sentiment Heatmap</h2>
        {dataUpdatedAt > 0 && (
          <span className="text-xs text-muted-foreground">
            {formatDistanceToNow(dataUpdatedAt, { addSuffix: true })}
          </span>
        )}
      </div>

      {isLoading && (
        <div className="space-y-2">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-8 bg-muted rounded animate-pulse" />
          ))}
        </div>
      )}

      {isError && (
        <div className="text-xs text-bearish p-3 border border-bearish/20 rounded">
          ⚠️ Backend connection failed. Start the FastAPI server.
        </div>
      )}

      {data && data.length === 0 && (
        <p className="text-xs text-muted-foreground">
          No sentiment data from the last 3 hours. Sentiment pipeline may be warming up.
        </p>
      )}

      {data && data.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr>
                <th className="text-xs text-muted-foreground font-medium text-left pb-2 pr-3 w-12" />
                {LABELS.map((label) => (
                  <th key={label} className="text-xs text-muted-foreground font-medium text-center pb-2 px-1">
                    {label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((row: any) => (
                <tr key={row.coin}>
                  <td className="text-xs font-mono font-medium text-foreground py-1 pr-3">
                    {row.coin}
                  </td>
                  <td className="p-1">
                    <div className={`rounded text-center py-2 px-1 font-mono text-xs font-medium ${getCellColor(row.avg_score, "Avg Score")}`}>
                      {row.avg_score.toFixed(2)}
                    </div>
                  </td>
                  <td className="p-1">
                    <div className={`rounded text-center py-2 px-1 font-mono text-xs font-medium ${getCellColor(row.bullish_pct, "Bullish %")}`}>
                      {row.bullish_pct}%
                    </div>
                  </td>
                  <td className="p-1">
                    <div className={`rounded text-center py-2 px-1 font-mono text-xs font-medium ${getCellColor(row.bearish_pct, "Bearish %")}`}>
                      {row.bearish_pct}%
                    </div>
                  </td>
                  <td className="p-1">
                    <div className="rounded text-center py-2 px-1 font-mono text-xs font-medium bg-muted/20 text-muted-foreground">
                      {row.total_news}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default SentimentHeatmap;
