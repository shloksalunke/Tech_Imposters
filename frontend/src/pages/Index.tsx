import Header from "@/components/Header";
import MetricCards from "@/components/MetricCards";
import CryptoHeatmaps from "@/components/CryptoHeatmaps";
import SignalFeed from "@/components/SignalFeed";
import PriceChart from "@/components/PriceChart";
import WhaleNews from "@/components/WhaleNews";
import LiveLogs from "@/components/LiveLogs";

function Index() {
  return (
    <div className="min-h-screen bg-black text-white">
      <Header />
      <main className="py-10 space-y-8">
        {/* Top Metrics */}
        <div className="px-6">
          <MetricCards />
        </div>

        {/* Sentiment Heatmaps */}
        <div className="px-6">
          <CryptoHeatmaps />
        </div>

        {/* Charts and signals section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 px-6">
          <div className="lg:col-span-2">
            <PriceChart />
          </div>
          <div className="space-y-6">
            <SignalFeed />
            <WhaleNews />
          </div>
        </div>

        {/* Live Logs */}
        <div className="px-6">
          <LiveLogs />
        </div>
      </main>
    </div>
  );
}

export default Index;
