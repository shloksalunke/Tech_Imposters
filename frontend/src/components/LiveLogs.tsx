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
        <div className="bg-card border border-border rounded-xl flex flex-col overflow-hidden">
            {/* header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-border flex-wrap gap-2">
                <div className="flex items-center gap-2">
                    <span className="relative flex h-2.5 w-2.5">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                        <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500" />
                    </span>
                    <h2 className="text-sm font-semibold text-foreground">Pipeline Logs</h2>
                    <span className="text-xs text-muted-foreground">{logs.length} lines</span>
                </div>

                <div className="flex items-center gap-2">
                    <input
                        type="text"
                        placeholder="Filter..."
                        value={filter}
                        onChange={(e) => setFilter(e.target.value)}
                        className="text-xs bg-background border border-border rounded-md px-2 py-1 text-foreground placeholder:text-muted-foreground w-32 focus:outline-none focus:border-primary"
                    />
                    <button
                        onClick={() => setPaused((p) => !p)}
                        className={`text-xs px-2 py-1 rounded-md border transition-colors ${paused
                                ? "border-amber-500 text-amber-400 bg-amber-500/10"
                                : "border-border text-muted-foreground hover:bg-muted"
                            }`}
                    >
                        {paused ? "▶ Resume" : "⏸ Pause"}
                    </button>
                </div>
            </div>

            {/* log body */}
            <div className="h-64 overflow-y-auto font-mono text-xs leading-5 p-3 space-y-0.5 bg-black/20">
                {visible.length === 0 && (
                    <p className="text-muted-foreground italic">Waiting for pipeline output...</p>
                )}
                {visible.map((log, i) => {
                    const { tag, msg } = parseLine(log);
                    return (
                        <div key={i} className="flex gap-2 hover:bg-white/5 rounded px-1">
                            <span className={`shrink-0 ${tagColor(tag)}`}>[{tag}]</span>
                            <span className={
                                msg.includes("❌") || msg.toLowerCase().includes("error") ? "text-red-400" :
                                    msg.includes("✅") || msg.includes("BULLISH") ? "text-emerald-400" :
                                        msg.includes("⚠️") || msg.includes("BEARISH") ? "text-amber-400" :
                                            msg.includes("FUD") ? "text-red-400" :
                                                "text-slate-300"
                            }>
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