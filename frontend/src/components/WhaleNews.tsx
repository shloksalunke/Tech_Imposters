import { whaleActivity, news } from "@/data/mockData";

const WhaleNews = () => {
  return (
    <div className="bg-card rounded-lg border border-border p-5 h-full flex flex-col gap-5">
      {/* Whale Activity */}
      <div>
        <h2 className="text-sm font-semibold text-foreground mb-3">Whale Activity</h2>
        <div className="space-y-2">
          {whaleActivity.map((entry, i) => (
            <div key={i} className="flex items-center justify-between text-xs">
              <span className="font-mono text-foreground">{entry.amount}</span>
              <span className={`font-medium ${entry.direction === "inflow" ? "text-bearish" : "text-bullish"}`}>
                {entry.direction === "inflow" ? "↓ Inflow" : "↑ Outflow"}
              </span>
              <span className="text-muted-foreground">{entry.exchange}</span>
              <span className="text-muted-foreground">{entry.time}</span>
            </div>
          ))}
        </div>
      </div>

      {/* News */}
      <div>
        <h2 className="text-sm font-semibold text-foreground mb-3">News</h2>
        <div className="space-y-2">
          {news.map((item, i) => {
            const tagColor = item.sentiment === "BULLISH" ? "text-bullish" : item.sentiment === "BEARISH" ? "text-bearish" : "text-neutral";
            return (
              <div key={i} className="text-xs">
                <div className="flex items-center gap-2">
                  <span className={`font-medium shrink-0 ${tagColor}`}>●</span>
                  <span className="text-foreground truncate">{item.title}</span>
                </div>
                <div className="flex items-center gap-2 mt-0.5 ml-4">
                  <span className="text-muted-foreground">{item.source}</span>
                  <span className="text-muted-foreground">· {item.time}</span>
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
