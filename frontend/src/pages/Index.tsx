import Header from "@/components/Header";
import MetricCards from "@/components/MetricCards";
import SignalFeed from "@/components/SignalFeed";
import PriceChart from "@/components/PriceChart";
import WhaleNews from "@/components/WhaleNews";

function Index() {
  return (
    <div className="min-h-screen bg-[#0a0a0f] text-gray-100">
      <Header />
      <main className="max-w-[1440px] mx-auto px-4 sm:px-6 py-6 space-y-6">
        {/* Metric cards */}
        <MetricCards />

        {/* Chart + Signals */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          <div className="lg:col-span-2">
            <PriceChart />
          </div>
          <div className="space-y-5">
            <SignalFeed />
            <WhaleNews />
          </div>
        </div>
      </main>
    </div>
  );
}

export default Index;
