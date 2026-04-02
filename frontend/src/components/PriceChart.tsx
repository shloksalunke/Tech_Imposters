import { useState } from "react";
import {
  ResponsiveContainer, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
} from "recharts";
import { useChartData } from "@/hooks/useApi";

const SYMBOLS = ["BTC", "ETH", "BNB"] as const;
type Symbol = typeof SYMBOLS[number];

// Enhanced vibrant colors with gradients
const COLOR = { 
  actual: "#06b6d4",      // Cyan - vibrant actual price
  pred_1h: "#ec4899",     // Pink - 1h prediction
  pred_4h: "#10b981",     // Emerald - 4h prediction
  pred_24h: "#f59e0b"     // Amber - 24h prediction
};

function fmt(ts: string) {
  const d = new Date(ts);
  return `${d.getMonth() + 1}/${d.getDate()}`;
}

function fmtPrice(v: number) {
  return v >= 1000 ? `$${(v / 1000).toFixed(1)}k` : `$${v.toFixed(2)}`;
}

export default function PriceChart() {
  const [symbol, setSymbol]   = useState<Symbol>("BTC");
  const [days, setDays]       = useState(30);
  const [showPred, setShowPred] = useState(true);
  const { data, loading, error } = useChartData(symbol, days);

  // merge historical + latest prediction point for chart
  const chartData = (() => {
    if (!data) return [];
    const hist = data.historical.map((h) => ({ ts: h.ts, actual: h.price }));

    if (showPred && data.predictions.length > 0) {
      const latest = data.predictions[0];   // most recent forecast
      const lastTs  = data.historical.at(-1)?.ts ?? "";
      // add 3 future points from last actual price
      const lastPrice = data.historical.at(-1)?.price ?? 0;
      hist.push(
        { ts: lastTs, actual: lastPrice, pred_1h: latest.pred_1h } as any,
        { ts: "→ 1h",  actual: undefined as any, pred_1h: latest.pred_1h } as any,
        { ts: "→ 4h",  actual: undefined as any, pred_4h: latest.pred_4h } as any,
        { ts: "→ 24h", actual: undefined as any, pred_24h: latest.pred_24h } as any,
      );
    }
    return hist;
  })();

  return (
    <div className="relative rounded-2xl bg-gradient-to-br from-gray-900/40 to-black/40 border border-gray-800/50 p-6 flex flex-col gap-4 backdrop-blur overflow-hidden group hover:shadow-2xl transition-all">
      {/* Glowing background effect */}
      <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/10 via-purple-500/5 to-pink-500/10 blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
      
      <div className="relative z-10">
        {/* ── header ── */}
        <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
          <div>
            <h2 className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
              📊 Price Analysis
            </h2>
            <p className="text-xs text-gray-400 mt-1">Historical prices & LSTM predictions</p>
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            {/* symbol tabs */}
            <div className="flex rounded-lg overflow-hidden border border-gray-700 text-sm backdrop-blur">
              {SYMBOLS.map((s) => (
                <button
                  key={s}
                  onClick={() => setSymbol(s)}
                  className={`px-4 py-2 transition-all font-semibold ${
                    symbol === s
                      ? "bg-gradient-to-r from-cyan-500 to-blue-500 text-white shadow-lg shadow-cyan-500/50"
                      : "bg-gray-800/50 text-gray-300 hover:bg-gray-700/50"
                  }`}
                >
                  {s}
                </button>
              ))}
            </div>

            {/* days selector */}
            <select
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
              className="text-sm bg-gray-800/50 border border-gray-700 rounded-lg px-3 py-2 text-gray-300 font-medium backdrop-blur hover:bg-gray-700/50 transition-colors"
            >
              <option value={7}>7 days</option>
              <option value={30}>30 days</option>
              <option value={90}>90 days</option>
            </select>

            {/* prediction toggle */}
            <button
              onClick={() => setShowPred((p) => !p)}
              className={`text-sm px-3 py-2 rounded-lg border transition-all font-semibold ${
                showPred
                  ? "border-amber-500/50 text-amber-300 bg-amber-500/20 shadow-lg shadow-amber-500/30"
                  : "border-gray-700 text-gray-400 bg-gray-800/50 hover:bg-gray-700/50"
              }`}
            >
              {showPred ? "▶ Predictions" : "⏸ Disabled"}
            </button>
          </div>
        </div>

        {/* ── chart ── */}
        <div className="h-80 w-full rounded-xl bg-black/30 p-3 border border-gray-800/30">
          {loading && (
            <div className="h-full flex items-center justify-center text-gray-400 text-sm">
              <div className="flex flex-col items-center gap-3">
                <div className="animate-spin rounded-full h-8 w-8 border-2 border-cyan-500 border-t-transparent" />
                Loading chart data...
              </div>
            </div>
          )}
          {error && (
            <div className="h-full flex items-center justify-center text-red-400 text-sm">
              ⚠️ {error}
            </div>
          )}
          {!loading && !error && (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(100,116,139,0.15)" />
                <XAxis
                  dataKey="ts"
                  tickFormatter={fmt}
                  tick={{ fontSize: 11, fill: "rgb(148,163,184)" }}
                  interval={Math.floor(chartData.length / 6)}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  tickFormatter={fmtPrice}
                  tick={{ fontSize: 11, fill: "rgb(148,163,184)" }}
                  axisLine={false}
                  tickLine={false}
                  width={60}
                />
                <Tooltip
                  contentStyle={{
                    background: "rgba(17, 24, 39, 0.95)",
                    border: "1px solid rgba(100, 116, 139, 0.3)",
                    borderRadius: 12,
                    fontSize: 12,
                    backdropFilter: "blur(10px)",
                  }}
                  formatter={(v: any) => [`$${Number(v).toLocaleString()}`, undefined]}
                  labelFormatter={(l) => `${l}`}
                  cursor={{ stroke: "rgba(79, 172, 254, 0.3)" }}
                />
                <Legend 
                  wrapperStyle={{ fontSize: 12, paddingTop: 12 }}
                  iconType="line"
                />

                <Line
                  type="monotone" dataKey="actual"
                  stroke={COLOR.actual} strokeWidth={3}
                  dot={false} name="Actual Price"
                  connectNulls={false}
                  isAnimationActive={true}
                  animationDuration={800}
                />
                {showPred && <>
                  <Line 
                    type="monotone" dataKey="pred_1h"  
                    stroke={COLOR.pred_1h}  strokeWidth={2.5} 
                    strokeDasharray="5 3" dot={false} name="1h Pred" 
                    isAnimationActive={true}
                    animationDuration={1000}
                  />
                  <Line 
                    type="monotone" dataKey="pred_4h"  
                    stroke={COLOR.pred_4h}  strokeWidth={2.5} 
                    strokeDasharray="5 3" dot={false} name="4h Pred"
                    isAnimationActive={true}
                    animationDuration={1100}
                  />
                  <Line 
                    type="monotone" dataKey="pred_24h" 
                    stroke={COLOR.pred_24h} strokeWidth={2.5} 
                    strokeDasharray="5 3" dot={false} name="24h Pred"
                    isAnimationActive={true}
                    animationDuration={1200}
                  />
                </>}
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </div>
  );
}