import Header from "@/components/Header";
import MetricCards from "@/components/MetricCards";
import SentimentHeatmap from "@/components/SentimentHeatmap";
import SignalFeed from "@/components/SignalFeed";
import PriceChart from "@/components/PriceChart";
import WhaleNews from "@/components/WhaleNews";
import LiveLogs from "@/components/LiveLogs";

function Index() {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="py-5 space-y-4">
        <MetricCards />
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-4 px-6">
          <div className="lg:col-span-3">
            <SentimentHeatmap />
          </div>
          <div className="lg:col-span-2">
            <SignalFeed />
          </div>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-4 px-6">
          <div className="lg:col-span-3">
            <PriceChart />
          </div>
          <div className="lg:col-span-2">
            <WhaleNews />
          </div>
        </div>
        <div className="px-6">
          <LiveLogs />
        </div>
      </main>
    </div>
  );
}

export default Index;
