import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import Index from "./pages/Index.tsx";
import NotFound from "./pages/NotFound.tsx";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <div className="min-h-screen bg-black">
          {/* Animated background gradient */}
          <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
            <div className="absolute -top-40 -left-40 w-80 h-80 bg-cyan-500/20 rounded-full blur-3xl mix-blend-multiply filter opacity-50 animate-blob" />
            <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500/20 rounded-full blur-3xl mix-blend-multiply filter opacity-50 animate-blob animation-delay-2000" />
            <div className="absolute bottom-0 left-1/2 w-80 h-80 bg-pink-500/20 rounded-full blur-3xl mix-blend-multiply filter opacity-50 animate-blob animation-delay-4000" />
          </div>

          {/* Content */}
          <div className="relative z-10">
            <Routes>
              <Route path="/" element={<Index />} />
              {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
              <Route path="*" element={<NotFound />} />
            </Routes>
          </div>
        </div>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
