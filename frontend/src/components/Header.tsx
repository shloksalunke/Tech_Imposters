const Header = () => {
  return (
    <header className="border-b border-gray-800/40 bg-[#0d0d14]">
      <div className="max-w-[1440px] mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-xl font-bold text-gray-100 tracking-tight">
            ⚡ CryptoMind
          </span>
          <span className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20">
            <span className="relative flex h-1.5 w-1.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-500" />
            </span>
            <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider">Live</span>
          </span>
        </div>

        <p className="hidden sm:block text-xs text-gray-500">
          LSTM Predictions · Ollama Sentiment · Whale Tracking
        </p>
      </div>
    </header>
  );
};

export default Header;
