import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Shield, BarChart3, FileCheck } from 'lucide-react';

interface LandingPageProps {
  onGetStarted: () => void;
}

export function LandingPage({ onGetStarted }: LandingPageProps) {
  return (
    <div className="min-h-screen bg-black relative overflow-hidden flex items-center justify-center">
      {/* Decorative background */}
      <div className="fixed inset-0 dot-mesh-pattern opacity-40 pointer-events-none"></div>
      <div className="fixed top-0 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-orange-500/10 rounded-full blur-3xl pointer-events-none"></div>
      <div className="fixed bottom-0 right-0 w-[400px] h-[400px] bg-amber-500/10 rounded-full blur-3xl pointer-events-none"></div>
      
      <div className="relative container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto text-center">
          {/* Hero Section */}
          <div className="mb-8">
            <div className="inline-flex items-center justify-center mb-6">
              <div className="relative">
                <div className="absolute inset-0 bg-orange-500/20 rounded-full blur-xl"></div>
                <Shield className="relative h-16 w-16 text-orange-400" />
              </div>
            </div>
            <h1 className="text-5xl md:text-6xl font-bold text-slate-50 mb-4">
              AI Fairness Audit Dashboard
            </h1>
            <p className="text-xl md:text-2xl text-slate-300 mb-8 max-w-2xl mx-auto">
              Detect bias and ensure fairness in your AI systems with comprehensive analysis and actionable insights.
            </p>
            <Button
              onClick={onGetStarted}
              size="lg"
              className="bg-orange-600 hover:bg-orange-700 text-white px-8 py-6 text-lg font-semibold rounded-lg shadow-lg hover:shadow-orange-500/50 transition-all"
            >
              Get Started
            </Button>
          </div>

          {/* Feature Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-16">
            <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700/50 hover:border-orange-500/50 transition-all">
              <CardContent className="p-6 text-center">
                <div className="inline-flex items-center justify-center mb-4">
                  <div className="p-3 bg-orange-950/50 rounded-full border border-orange-500/50">
                    <BarChart3 className="h-8 w-8 text-orange-400" />
                  </div>
                </div>
                <h3 className="text-lg font-semibold text-slate-100 mb-2">13 Fairness Metrics</h3>
                <p className="text-sm text-slate-400">
                  Comprehensive bias detection across demographic parity, equal opportunity, and calibration
                </p>
              </CardContent>
            </Card>

            <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700/50 hover:border-amber-500/50 transition-all">
              <CardContent className="p-6 text-center">
                <div className="inline-flex items-center justify-center mb-4">
                  <div className="p-3 bg-amber-950/50 rounded-full border border-amber-500/50">
                    <Shield className="h-8 w-8 text-amber-400" />
                  </div>
                </div>
                <h3 className="text-lg font-semibold text-slate-100 mb-2">Visual Analysis</h3>
                <p className="text-sm text-slate-400">
                  Interactive charts and detailed explanations for every fairness metric
                </p>
              </CardContent>
            </Card>

            <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700/50 hover:border-red-500/50 transition-all">
              <CardContent className="p-6 text-center">
                <div className="inline-flex items-center justify-center mb-4">
                  <div className="p-3 bg-red-950/50 rounded-full border border-red-500/50">
                    <FileCheck className="h-8 w-8 text-red-400" />
                  </div>
                </div>
                <h3 className="text-lg font-semibold text-slate-100 mb-2">Export Reports</h3>
                <p className="text-sm text-slate-400">
                  Generate professional PDF audit reports for compliance and documentation
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
