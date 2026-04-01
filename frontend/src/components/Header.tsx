const Header = () => {
  const now = new Date();
  const time = now.toLocaleTimeString("en-US", { hour12: false });

  return (
    <header className="flex items-center justify-between px-6 py-4 border-b border-border">
      <div>
        <h1 className="text-2xl font-bold text-foreground tracking-tight">
          CryptoMind Terminal
        </h1>
        <p className="text-sm text-muted-foreground">
          AI Sentiment + Prediction Dashboard
        </p>
      </div>
      <div className="text-sm text-muted-foreground font-mono">
        Last Updated: {time}
      </div>
    </header>
  );
};

export default Header;
