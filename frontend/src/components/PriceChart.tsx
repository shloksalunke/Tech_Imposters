import { useState } from "react";
import {
  ResponsiveContainer, ComposedChart, Line, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine,
} from "recharts";
import { useChartData, usePrediction } from "@/hooks/useApi";

const SYMBOLS = ["BTC", "ETH", "BNB"] as const;
type Symbol = (typeof SYMBOLS)[number];

function fmtDate(ts: string) {
  if (ts.startsWith("→")) return ts;
  const d = new Date(ts);
  return `${d.getMonth() + 1}/${d.getDate()}`;
}

function fmtPrice(v: number) {
  if (v >= 1000) return `$${(v / 1000).toFixed(1)}k`;
  return `$${v.toFixed(2)}`;
}

export default function PriceChart() {
  const [symbol, setSymbol] = useState<Symbol>("BTC");
  const [days, setDays] = useState(30);
  const { data, isLoading, error } = useChartData(symbol, days);
  const { data: pred } = usePrediction(symbol);

  // Build chart data: historical + future prediction points
  const chartData = (() => {
    if (!data?.historical?.length) return [];

    // Sample historical data to max ~120 points for clean chart
    const hist = data.historical;
    const step = Math.max(1, Math.floor(hist.length / 120));
    const sampled = hist.filter((_, i) => i % step === 0 || i === hist.length - 1);

    const points = sampled.map((h) => ({
      ts: h.ts,
      actual: h.price,
      pred_1h: undefined as number | undefined,
      pred_4h: undefined as number | undefined,
      pred_24h: undefined as number | undefined,
    }));

    // Add future prediction points from the /api/prediction endpoint
    if (pred) {
      const lastPrice = hist[hist.length - 1]?.price ?? 0;
      const lastTs = hist[hist.length - 1]?.ts ?? "";

      // Bridge point — connects actual line to prediction lines
      points[points.length - 1] = {
        ...points[points.length - 1],
        pred_1h: lastPrice,
        pred_4h: lastPrice,
        pred_24h: lastPrice,
      };

      // Future points
      if (pred.pred_1h) {
        points.push({
          ts: "→ 1h",
          actual: undefined as any,
          pred_1h: pred.pred_1h,
          pred_4h: undefined,
          pred_24h: undefined,
        });
      }
      if (pred.pred_4h) {
        points.push({
          ts: "→ 4h",
          actual: undefined as any,
          pred_1h: undefined,
          pred_4h: pred.pred_4h,
          pred_24h: undefined,
        });
      }
      if (pred.pred_24h) {
        points.push({
          ts: "→ 24h",
          actual: undefined as any,
          pred_1h: undefined,
          pred_4h: undefined,
          pred_24h: pred.pred_24h,
        });
      }
    }

    return points;
  })();

  const currentPrice = pred?.current_price;
  const change24h = pred?.change_pct_24h ?? 0;

  return (
    <div className="rounded-xl bg-[#111118] border border-gray-800/60 p-5 flex flex-col gap-4">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-base font-semibold text-gray-100 flex items-center gap-2">
            📊 {symbol}/USDT
            {currentPrice && (
              <span className="text-lg font-bold ml-1">
                ${currentPrice.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </span>
            )}
            {change24h !== 0 && (
              <span className={`text-xs font-mono px-2 py-0.5 rounded ${change24h >= 0 ? "bg-emerald-500/15 text-emerald-400" : "bg-red-500/15 text-red-400"}`}>
                {change24h >= 0 ? "+" : ""}{change24h.toFixed(2)}%
              </span>
            )}
          </h2>
          <p className="text-xs text-gray-500 mt-0.5">Historical prices + LSTM forecast</p>
        </div>

        <div className="flex items-center gap-2">
          {/* Symbol tabs */}
          <div className="flex rounded-lg overflow-hidden border border-gray-700/60 text-xs">
            {SYMBOLS.map((s) => (
              <button
                key={s}
                onClick={() => setSymbol(s)}
                className={`px-3 py-1.5 font-medium transition-all ${
                  symbol === s
                    ? "bg-cyan-500/20 text-cyan-400 border-r border-cyan-500/30"
                    : "bg-transparent text-gray-400 hover:text-gray-200 border-r border-gray-700/40 last:border-r-0"
                }`}
              >
                {s}
              </button>
            ))}
          </div>

          {/* Days selector */}
          <select
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            className="text-xs bg-transparent border border-gray-700/60 rounded-lg px-2 py-1.5 text-gray-400 focus:outline-none"
          >
            <option value={7}>7d</option>
            <option value={30}>30d</option>
            <option value={90}>90d</option>
          </select>
        </div>
      </div>

      {/* Chart */}
      <div className="h-72 w-full">
        {isLoading && (
          <div className="h-full flex items-center justify-center text-gray-500 text-sm">
            <div className="flex items-center gap-2">
              <div className="animate-spin rounded-full h-4 w-4 border border-cyan-500 border-t-transparent" />
              Loading...
            </div>
          </div>
        )}
        {error && (
          <div className="h-full flex items-center justify-center text-red-400/70 text-sm">
            ⚠ {error}
          </div>
        )}
        {!isLoading && !error && chartData.length > 0 && (
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData} margin={{ top: 4, right: 12, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="areaFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#06b6d4" stopOpacity={0.12} />
                  <stop offset="100%" stopColor="#06b6d4" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(75,85,99,0.15)" />
              <XAxis
                dataKey="ts"
                tickFormatter={fmtDate}
                tick={{ fontSize: 10, fill: "rgb(107,114,128)" }}
                interval={Math.max(1, Math.floor(chartData.length / 6))}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                tickFormatter={fmtPrice}
                tick={{ fontSize: 10, fill: "rgb(107,114,128)" }}
                axisLine={false}
                tickLine={false}
                width={55}
                domain={["auto", "auto"]}
              />
              <Tooltip
                contentStyle={{
                  background: "rgba(17,17,24,0.95)",
                  border: "1px solid rgba(75,85,99,0.3)",
                  borderRadius: 8,
                  fontSize: 11,
                  padding: "8px 12px",
                }}
                formatter={(v: any, name: string) => [
                  `$${Number(v).toLocaleString("en-US", { minimumFractionDigits: 2 })}`,
                  name,
                ]}
                labelStyle={{ color: "rgb(156,163,175)", fontSize: 10 }}
                labelFormatter={(l) => `${l}`}
                cursor={{ stroke: "rgba(6,182,212,0.2)" }}
              />

              {/* Actual price line + area fill */}
              <Area
                type="monotone"
                dataKey="actual"
                stroke="#06b6d4"
                strokeWidth={2}
                fill="url(#areaFill)"
                dot={false}
                name="Price"
                connectNulls={false}
                isAnimationActive={false}
              />

              {/* Future prediction lines — dashed */}
              <Line
                type="monotone"
                dataKey="pred_1h"
                stroke="#f472b6"
                strokeWidth={2}
                strokeDasharray="6 3"
                dot={{ r: 4, fill: "#f472b6", strokeWidth: 0 }}
                name="1h Prediction"
                connectNulls={false}
                isAnimationActive={false}
              />
              <Line
                type="monotone"
                dataKey="pred_4h"
                stroke="#34d399"
                strokeWidth={2}
                strokeDasharray="6 3"
                dot={{ r: 4, fill: "#34d399", strokeWidth: 0 }}
                name="4h Prediction"
                connectNulls={false}
                isAnimationActive={false}
              />
              <Line
                type="monotone"
                dataKey="pred_24h"
                stroke="#fbbf24"
                strokeWidth={2}
                strokeDasharray="6 3"
                dot={{ r: 4, fill: "#fbbf24", strokeWidth: 0 }}
                name="24h Prediction"
                connectNulls={false}
                isAnimationActive={false}
              />

              {/* Current price reference line */}
              {currentPrice && (
                <ReferenceLine
                  y={currentPrice}
                  stroke="rgba(6,182,212,0.25)"
                  strokeDasharray="3 3"
                />
              )}
            </ComposedChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Prediction summary bar */}
      {pred && (
        <div className="flex items-center gap-4 text-xs border-t border-gray-800/50 pt-3">
          <span className="text-gray-500 font-medium">LSTM Forecast:</span>
          {pred.pred_1h && (
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-pink-400" />
              <span className="text-gray-400">1h</span>
              <span className={`font-mono font-medium ${pred.pred_1h > (pred.current_price ?? 0) ? "text-emerald-400" : "text-red-400"}`}>
                ${pred.pred_1h.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </span>
            </span>
          )}
          {pred.pred_4h && (
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-emerald-400" />
              <span className="text-gray-400">4h</span>
              <span className={`font-mono font-medium ${pred.pred_4h > (pred.current_price ?? 0) ? "text-emerald-400" : "text-red-400"}`}>
                ${pred.pred_4h.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </span>
            </span>
          )}
          {pred.pred_24h && (
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-amber-400" />
              <span className="text-gray-400">24h</span>
              <span className={`font-mono font-medium ${pred.pred_24h > (pred.current_price ?? 0) ? "text-emerald-400" : "text-red-400"}`}>
                ${pred.pred_24h.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </span>
            </span>
          )}
        </div>
      )}
    </div>
  );
}