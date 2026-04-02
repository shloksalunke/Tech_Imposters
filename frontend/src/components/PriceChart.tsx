import { useState } from "react";
import {
  ResponsiveContainer, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
} from "recharts";
import { useChartData } from "@/hooks/useApi";

const SYMBOLS = ["BTC", "ETH", "BNB"] as const;
type Symbol = typeof SYMBOLS[number];

const COLOR = { actual: "#6366f1", pred_1h: "#f59e0b", pred_4h: "#10b981", pred_24h: "#ef4444" };

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
    <div className="bg-card border border-border rounded-xl p-5 flex flex-col gap-4">

      {/* ── header ── */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-lg font-semibold text-foreground">Price Chart</h2>

        <div className="flex items-center gap-2 flex-wrap">
          {/* symbol tabs */}
          <div className="flex rounded-lg overflow-hidden border border-border text-sm">
            {SYMBOLS.map((s) => (
              <button
                key={s}
                onClick={() => setSymbol(s)}
                className={`px-3 py-1.5 transition-colors ${
                  symbol === s
                    ? "bg-primary text-primary-foreground"
                    : "bg-background text-muted-foreground hover:bg-muted"
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
            className="text-sm bg-background border border-border rounded-lg px-2 py-1.5 text-foreground"
          >
            <option value={7}>7d</option>
            <option value={30}>30d</option>
            <option value={90}>90d</option>
          </select>

          {/* prediction toggle */}
          <button
            onClick={() => setShowPred((p) => !p)}
            className={`text-sm px-3 py-1.5 rounded-lg border transition-colors ${
              showPred
                ? "border-amber-500 text-amber-400 bg-amber-500/10"
                : "border-border text-muted-foreground"
            }`}
          >
            {showPred ? "Predictions ON" : "Predictions OFF"}
          </button>
        </div>
      </div>

      {/* ── chart ── */}
      <div className="h-72 w-full">
        {loading && (
          <div className="h-full flex items-center justify-center text-muted-foreground text-sm">
            Loading chart data...
          </div>
        )}
        {error && (
          <div className="h-full flex items-center justify-center text-red-400 text-sm">
            {error}
          </div>
        )}
        {!loading && !error && (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis
                dataKey="ts"
                tickFormatter={fmt}
                tick={{ fontSize: 11, fill: "var(--muted-foreground)" }}
                interval={Math.floor(chartData.length / 6)}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                tickFormatter={fmtPrice}
                tick={{ fontSize: 11, fill: "var(--muted-foreground)" }}
                axisLine={false}
                tickLine={false}
                width={60}
              />
              <Tooltip
                contentStyle={{
                  background: "var(--card)",
                  border: "1px solid var(--border)",
                  borderRadius: 8,
                  fontSize: 12,
                }}
                formatter={(v: any) => [`$${Number(v).toLocaleString()}`, undefined]}
                labelFormatter={(l) => `Time: ${l}`}
              />
              <Legend wrapperStyle={{ fontSize: 12 }} />

              <Line
                type="monotone" dataKey="actual"
                stroke={COLOR.actual} strokeWidth={2}
                dot={false} name="Actual Price"
                connectNulls={false}
              />
              {showPred && <>
                <Line type="monotone" dataKey="pred_1h"  stroke={COLOR.pred_1h}  strokeWidth={2} strokeDasharray="5 3" dot={false} name="Pred 1h" />
                <Line type="monotone" dataKey="pred_4h"  stroke={COLOR.pred_4h}  strokeWidth={2} strokeDasharray="5 3" dot={false} name="Pred 4h" />
                <Line type="monotone" dataKey="pred_24h" stroke={COLOR.pred_24h} strokeWidth={2} strokeDasharray="5 3" dot={false} name="Pred 24h" />
              </>}
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}