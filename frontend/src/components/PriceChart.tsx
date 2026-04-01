import { useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { priceHistory } from "@/data/mockData";

type Timeframe = "1H" | "4H" | "24H";

const PriceChart = () => {
  const [timeframe, setTimeframe] = useState<Timeframe>("1H");
  const data = priceHistory[timeframe];

  return (
    <div className="bg-card rounded-lg border border-border p-5 h-full">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-semibold text-foreground">BTC Price + Prediction</h2>
        <div className="flex gap-1">
          {(["1H", "4H", "24H"] as Timeframe[]).map((tf) => (
            <button
              key={tf}
              onClick={() => setTimeframe(tf)}
              className={`px-2.5 py-1 text-xs font-medium rounded transition-colors ${
                timeframe === tf
                  ? "bg-secondary text-foreground"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {tf}
            </button>
          ))}
        </div>
      </div>
      <div className="h-48">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
            <XAxis dataKey="time" tick={{ fontSize: 10, fill: "#C9D1D9" }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fontSize: 10, fill: "#C9D1D9" }} axisLine={false} tickLine={false} domain={["auto", "auto"]} />
            <Tooltip
              contentStyle={{ backgroundColor: "#161B22", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 8, fontSize: 12 }}
              labelStyle={{ color: "#C9D1D9" }}
            />
            <Line type="monotone" dataKey="price" stroke="#00D4AA" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="prediction" stroke="#7B68EE" strokeWidth={2} strokeDasharray="6 3" dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-3 text-xs text-muted-foreground flex items-center gap-2">
        Prediction: <span className="text-bullish font-mono font-medium">UP</span>
        <span className="text-prediction font-mono">| Confidence 84%</span>
      </div>
    </div>
  );
};

export default PriceChart;
