import { useEffect, useRef, useState } from "react";
import { useLiveLogs } from "@/hooks/useApi";

const TAG_COLOR: Record<string, string> = {
    "sentiment_pipeline": "text-violet-400",
    "whale_pipeline": "text-cyan-400",
    "signal_generator": "text-emerald-400",
    "lstm_predict": "text-amber-400",
    "manager": "text-slate-400",
};

function parseLine(log: string) {
    const match = log.match(/^\[([^\]]+)\]\s*(.*)/);
    if (!match) return { tag: "system", msg: log };
    return { tag: match[1], msg: match[2] };
}

function tagColor(tag: string) {
    for (const [key, cls] of Object.entries(TAG_COLOR)) {
        if (tag.includes(key)) return cls;
    }
    return "text-slate-400";
}

export default function LiveLogs() {
    const logs = useLiveLogs(300);
    const bottomRef = useRef<HTMLDivElement>(null);
    const [paused, setPaused] = useState(false);
    const [filter, setFilter] = useState("");

    useEffect(() => {
        if (!paused) bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [logs, paused]);

    const visible = filter
        ? logs.filter((l) => l.toLowerCase().includes(filter.toLowerCase()))
        : logs;

    return (
        <div className="relative rounded-2xl bg-gradient-to-br from-gray-900/40 to-black/40 border border-gray-800/50 flex flex-col overflow-hidden backdrop-blur group hover:shadow-2xl transition-all">
            {/* Glowing effect */}
            <div className="absolute inset-0 bg-gradient-to-br from-slate-500/10 via-transparent to-blue-500/10 blur-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />

            {/* header */}
            <div className="relative z-10 flex items-center justify-between px-6 py-4 border-b border-gray-800/50 flex-wrap gap-3 bg-gradient-to-r from-gray-900/50 to-transparent">
                <div className="flex items-center gap-3">
                    <span className="relative flex h-3 w-3">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                        <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500" />
                    </span>
                    <h2 className="text-lg font-bold bg-gradient-to-r from-slate-400 to-gray-400 bg-clip-text text-transparent">
                        📡 Pipeline Logs
                    </h2>
                    <span className="text-xs text-gray-400 font-mono">{logs.length} lines</span>
                </div>

                <div className="flex items-center gap-3">
                    <input
                        type="text"
                        placeholder="Filter logs..."
                        value={filter}
                        onChange={(e) => setFilter(e.target.value)}
                        className="text-xs bg-gray-800/50 border border-gray-700/50 rounded-lg px-3 py-2 text-gray-300 placeholder:text-gray-500 w-40 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/30 transition-all"
                    />
                    <button
                        onClick={() => setPaused((p) => !p)}
                        className={`text-xs px-3 py-2 rounded-lg border font-semibold transition-all ${paused
                                ? "border-amber-500/60 text-amber-300 bg-amber-500/20 shadow-lg shadow-amber-500/20"
                                : "border-gray-700/50 text-gray-300 hover:bg-gray-700/50 hover:border-gray-600"
                            }`}
                    >
                        {paused ? "▶ Resume" : "⏸ Pause"}
                    </button>
                </div>
            </div>

            {/* log body */}
            <div className="relative z-10 h-72 overflow-y-auto font-mono text-xs leading-6 p-4 space-y-0.5 bg-black/50 scroll-smooth">
                {visible.length === 0 && (
                    <p className="text-gray-500 italic">Waiting for pipeline output...</p>
                )}
                {visible.map((log, i) => {
                    const { tag, msg } = parseLine(log);
                    const isError = msg.includes("❌") || msg.toLowerCase().includes("error");
                    const isSuccess = msg.includes("✅") || msg.includes("BULLISH");
                    const isWarning = msg.includes("⚠️") || msg.includes("BEARISH") || msg.includes("FUD");

                    return (
                        <div key={i} className={`flex gap-3 hover:bg-white/10 rounded px-2 py-1 transition-colors ${isError ? "text-red-400" : isSuccess ? "text-green-400" : isWarning ? "text-amber-400" : "text-gray-300"}`}>
                            <span className={`shrink-0 font-bold ${tagColor(tag)}`}>[{tag}]</span>
                            <span className={isError ? "text-red-300" : isSuccess ? "text-green-300" : isWarning ? "text-amber-300" : "text-gray-300"}>
                                {msg}
                            </span>
                        </div>
                    );
                })}
                <div ref={bottomRef} />
            </div>
        </div>
    );
}