const Header = () => {
  const now = new Date();
  const time = now.toLocaleTimeString("en-US", { hour12: false });

  return (
    <header className="relative border-b border-gray-800/50 backdrop-blur-xl bg-gradient-to-r from-gray-900/80 via-gray-900/60 to-black/80 overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -left-40 -top-40 w-80 h-80 bg-gradient-to-br from-cyan-500/20 to-blue-500/20 rounded-full blur-3xl animate-pulse" />
        <div className="absolute right-0 top-20 w-96 h-96 bg-gradient-to-br from-purple-500/10 to-pink-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: "1s" }} />
      </div>

      <div className="relative px-8 py-6 flex items-center justify-between">
        <div className="space-y-1">
          <div className="flex items-center gap-3">
            <div className="text-3xl font-black bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-500 bg-clip-text text-transparent">
              ⚡ CryptoMind
            </div>
            <div className="hidden sm:flex items-center gap-1">
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-3 w-3 bg-cyan-500" />
              </span>
              <span className="text-xs font-bold text-cyan-400">LIVE</span>
            </div>
          </div>
          <p className="text-sm text-gray-400 font-medium">
            🤖 AI Sentiment + LSTM Predictions + 🐋 Whale Tracking
          </p>
        </div>

        <div className="flex items-center gap-4">
          <div className="hidden md:flex flex-col items-end gap-1">
            <div className="text-xs text-gray-500 font-mono">SERVER TIME</div>
            <div className="text-lg font-bold font-mono text-emerald-400">
              {time}
            </div>
          </div>

          {/* Status indicators */}
          <div className="flex items-center gap-3 px-4 py-2 rounded-lg bg-gray-800/40 border border-gray-700/50 backdrop-blur">
            <div className="flex items-center gap-2">
              <span className="flex h-2.5 w-2.5 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-xs text-gray-300 font-medium">API</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
