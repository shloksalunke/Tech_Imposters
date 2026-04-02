const BASE = "http://localhost:8000";

async function fetcher(url: string) {
  const res = await fetch(`${BASE}${url}`);
  if (!res.ok) throw new Error(res.statusText);
  return res.json();
}

// ── generic polling hook ─────────────────────────────────────────
import { useEffect, useState } from "react";

export function useApi<T>(url: string, intervalMs = 15000) {
  const [data, setData] = useState<T | null>(null);
  const [isLoading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      try {
        const json = await fetcher(url);
        if (!cancelled) { setData(json); setError(null); }
      } catch (e: any) {
        if (!cancelled) setError(e.message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    load();
    const id = setInterval(load, intervalMs);
    return () => { cancelled = true; clearInterval(id); };
  }, [url, intervalMs]);

  return { data, isLoading, error };
}

// ── usePrediction  (MetricCards uses this) ───────────────────────
export interface PredictionData {
  coin: string;
  current_price: number;
  change_pct_24h: number;
  direction_24h: string;
  pred_1h: number;
  pred_4h: number;
  pred_24h: number;
}

export function usePrediction(coin: string) {
  return useApi<PredictionData>(`/api/prediction/${coin}`, 30_000);
}

// ── useSentimentSummary  (MetricCards + CryptoHeatmaps) ─────────
export interface SentimentSummary {
  coin: string;
  avg_score: number;
  dominant_label: string;
  bullish_pct?: number;
  bearish_pct?: number;
  total_news?: number;
}

export function useSentimentSummary() {
  return useApi<SentimentSummary[]>("/api/sentiment/summary", 15_000);
}

// ── useSentimentLatest  (WhaleNews uses this) ────────────────────
export function useSentimentLatest() {
  return useApi("/api/sentiment/latest", 15_000);
}

// ── useWhales  (WhaleNews uses this) ─────────────────────────────
export function useWhales() {
  return useApi("/api/whales", 15_000);
}

// ── useSignals  (SignalFeed uses this) ───────────────────────────
export function useSignals() {
  return useApi("/api/signals", 15_000);
}

// ── useChartData  (PriceChart uses this) ─────────────────────────
export interface HistoricalPoint { ts: string; price: number; }
export interface PredictionPoint { ts: string; pred_1h: number; pred_4h: number; pred_24h: number; }
export interface ChartData {
  symbol: string;
  historical: HistoricalPoint[];
  predictions: PredictionPoint[];
}

export function useChartData(symbol: string, days = 90) {
  return useApi<ChartData>(`/api/chart/${symbol}?days=${days}`, 60_000);
}