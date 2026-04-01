import { heatmapData, heatmapLabels } from "@/data/mockData";

const getCellColor = (score: number) => {
  if (score >= 0.7) return "bg-bullish/30 text-bullish";
  if (score <= 0.45) return "bg-bearish/30 text-bearish";
  return "bg-neutral/20 text-neutral";
};

const SentimentHeatmap = () => {
  const symbols = Object.keys(heatmapData);

  return (
    <div className="bg-card rounded-lg border border-border p-5 h-full">
      <h2 className="text-sm font-semibold text-foreground mb-4">Sentiment Heatmap</h2>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr>
              <th className="text-xs text-muted-foreground font-medium text-left pb-2 pr-3 w-12"></th>
              {heatmapLabels.map((label) => (
                <th key={label} className="text-xs text-muted-foreground font-medium text-center pb-2 px-1">
                  {label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {symbols.map((symbol) => (
              <tr key={symbol}>
                <td className="text-xs font-mono font-medium text-foreground py-1 pr-3">{symbol}</td>
                {heatmapData[symbol].map((score, i) => (
                  <td key={i} className="p-1">
                    <div className={`rounded text-center py-2 px-1 font-mono text-xs font-medium ${getCellColor(score)}`}>
                      {score.toFixed(2)}
                    </div>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default SentimentHeatmap;
