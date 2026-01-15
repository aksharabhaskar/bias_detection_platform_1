import { useStore } from '@/lib/store';
import { LandingPage } from '@/components/LandingPage';
import { DatasetUpload } from '@/components/DatasetUpload';
import { ProtectedAttributeSelector } from '@/components/ProtectedAttributeSelector';
import { ActionPanel } from '@/components/ActionPanel';
import { MetricVisualization } from '@/components/MetricVisualization';
import { CompareModal } from '@/components/CompareModal';
import { ComparisonResults } from '@/components/ComparisonResults';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { AlertCircle, BarChart3, Database, Shield, CheckCircle, X } from 'lucide-react';

function App() {
  const { 
    currentDataset, 
    analysisResults, 
    comparisonResults, 
    isLoading, 
    error,
    showLandingPage,
    showSuccessMessage,
    setShowLandingPage,
    setShowSuccessMessage,
    setError
  } = useStore();

  // Show landing page if flag is set
  if (showLandingPage) {
    return <LandingPage onGetStarted={() => setShowLandingPage(false)} />;
  }

  // Calculate priority issue for overall summary
  const getPriorityIssue = () => {
    if (!analysisResults) return null;
    const violations = analysisResults.metrics.filter((m: any) => m.fairness_assessment === 'Violation');
    if (violations.length > 0) {
      return violations[0].explanation.display_name;
    }
    return null;
  };

  const formatErrorMessage = (error: string) => {
    if (error.toLowerCase().includes('csv')) {
      return 'Please upload a valid CSV file with proper formatting.';
    }
    if (error.toLowerCase().includes('network') || error.toLowerCase().includes('fetch')) {
      return 'Unable to connect to the server. Please check your connection and try again.';
    }
    if (error.toLowerCase().includes('column') || error.toLowerCase().includes('attribute')) {
      return 'The selected attribute was not found in your dataset. Please select a valid attribute.';
    }
    return 'An unexpected error occurred. Please try again or contact support if the issue persists.';
  };

  return (
    <div className="min-h-screen bg-black relative overflow-hidden">
      {/* Decorative background with dot mesh */}
      <div className="fixed inset-0 dot-mesh-pattern opacity-40 pointer-events-none"></div>
      <div className="fixed top-0 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-orange-500/10 rounded-full blur-3xl pointer-events-none"></div>
      <div className="fixed bottom-0 right-0 w-[400px] h-[400px] bg-amber-500/10 rounded-full blur-3xl pointer-events-none"></div>
      
      {/* Header */}
      <header className="relative bg-slate-900/70 backdrop-blur-lg shadow-2xl border-b border-slate-700/50">
        <div className="container mx-auto px-4 md:px-6 py-5 md:py-7">
          <div className="flex items-center gap-3 md:gap-4">
            <div className="relative">
              <div className="absolute inset-0 bg-orange-500/20 rounded-full blur-xl"></div>
              <Shield className="relative h-7 w-7 md:h-9 md:w-9 text-orange-400" />
            </div>
            <div>
              <h1 className="text-xl md:text-3xl font-bold text-slate-50 tracking-tight">AI Fairness Audit Dashboard</h1>
              <p className="text-xs md:text-sm text-slate-400 mt-1">
                Bias detection and fairness analysis for AI systems
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative container mx-auto px-4 md:px-6 py-6 md:py-10">
        {/* Horizontal Control Panel */}
        {currentDataset && (
          <div className="mb-8 space-y-5">
            {/* Dataset Info Bar */}
            <Card className="bg-slate-800/60 backdrop-blur-md border-slate-700/50 shadow-xl">
              <CardContent className="py-4 px-6">
                <div className="flex items-center gap-8 text-sm">
                  <div className="flex items-center gap-2">
                    <span className="text-slate-400 font-medium">File:</span>
                    <span className="font-semibold text-slate-100">{currentDataset.filename}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-slate-400 font-medium">Rows:</span>
                    <span className="font-semibold text-slate-100">{currentDataset.rows.toLocaleString()}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-slate-400 font-medium">Columns:</span>
                    <span className="font-semibold text-slate-100">{currentDataset.columns}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* All Controls on One Row */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
              <DatasetUpload />
              <ProtectedAttributeSelector />
              <ActionPanel />
            </div>
          </div>
        )}

        {/* Upload only when no dataset */}
        {!currentDataset && (
          <div className="mb-8">
            <DatasetUpload />
          </div>
        )}

        {/* Main Analysis Area */}
        <div>
          {/* Comparison Results */}
            {comparisonResults && (
              <ComparisonResults />
            )}

            {/* Loading State */}
            {isLoading && !comparisonResults && (
              <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700/50">
                <CardContent className="flex items-center justify-center py-12">
                  <div className="text-center">
                    <div className="animate-spin mx-auto h-12 w-12 border-4 border-orange-400 border-t-transparent rounded-full"></div>
                    <p className="mt-4 text-slate-300">Processing...</p>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Error State */}
            {error && !comparisonResults && (
              <Card className="border-red-500/50 bg-red-950/30 backdrop-blur-sm">
                <CardContent className="flex items-start gap-3 py-6">
                  <AlertCircle className="h-5 w-5 text-red-400 mt-0.5" />
                  <div>
                    <h3 className="font-semibold text-red-300">Error</h3>
                    <p className="text-sm text-red-200 mt-1">{formatErrorMessage(error)}</p>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Success Message */}
            {showSuccessMessage && analysisResults && !comparisonResults && (
              <Card className="border-green-500/50 bg-green-950/30 backdrop-blur-sm mb-6">
                <CardContent className="flex items-start gap-3 py-4">
                  <CheckCircle className="h-5 w-5 text-green-400 mt-0.5" />
                  <div className="flex-1">
                    <h3 className="font-semibold text-green-300">Analysis Complete</h3>
                    <p className="text-sm text-green-200 mt-1">
                      Found {analysisResults.summary.violation} fairness violation{analysisResults.summary.violation !== 1 ? 's' : ''} and {analysisResults.summary.warning} warning{analysisResults.summary.warning !== 1 ? 's' : ''}
                    </p>
                  </div>
                  <button
                    onClick={() => setShowSuccessMessage(false)}
                    className="text-green-300 hover:text-green-200"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </CardContent>
              </Card>
            )}

            {/* Empty State */}
            {!isLoading && !error && !analysisResults && !currentDataset && !comparisonResults && (
              <Card className="h-full bg-slate-800/50 backdrop-blur-sm border-slate-700/50 ambient-glow-orange gradient-overlay-orange">
                <CardContent className="flex flex-col items-center justify-center py-20 text-center">
                  <Database className="h-16 w-16 text-slate-600 mb-4" />
                  <h2 className="text-2xl font-semibold text-slate-100 mb-2">
                    Welcome to AI Fairness Audit Dashboard
                  </h2>
                  <p className="text-slate-400 max-w-md mb-6">
                    Upload a dataset to begin analyzing your AI system for bias and fairness issues.
                    Get comprehensive metrics, visualizations, and actionable recommendations.
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-2xl mt-8">
                    <div className="p-4 bg-orange-950/30 border border-orange-500/30 rounded-lg backdrop-blur-sm card-hover-accent ambient-glow-orange">
                      <h3 className="font-semibold text-orange-300 mb-2">13 Metrics</h3>
                      <p className="text-sm text-orange-200/80">
                        Comprehensive fairness analysis across multiple dimensions
                      </p>
                    </div>
                    <div className="p-4 bg-amber-950/30 border border-amber-500/30 rounded-lg backdrop-blur-sm card-hover-accent ambient-glow-amber">
                      <h3 className="font-semibold text-amber-300 mb-2">Visual Reports</h3>
                      <p className="text-sm text-amber-200/80">
                        Interactive charts and detailed explanations
                      </p>
                    </div>
                    <div className="p-4 bg-red-950/30 border border-red-500/30 rounded-lg backdrop-blur-sm card-hover-accent">
                      <h3 className="font-semibold text-red-300 mb-2">PDF Export</h3>
                      <p className="text-sm text-red-200/80">
                        Generate professional audit reports
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Dataset uploaded but no analysis */}
            {!isLoading && !error && currentDataset && !analysisResults && !comparisonResults && (
              <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700/50">
                <CardContent className="flex flex-col items-center justify-center py-16 text-center">
                  <BarChart3 className="h-16 w-16 text-slate-600 mb-4" />
                  <h2 className="text-xl font-semibold text-slate-100 mb-2">
                    Dataset Loaded Successfully
                  </h2>
                  <p className="text-slate-400 max-w-md mb-6">
                    Your dataset is ready for analysis. Select a protected attribute and click
                    "Analyze Fairness" to begin.
                  </p>
                </CardContent>
              </Card>
            )}

            {/* Analysis Results */}
            {!isLoading && analysisResults && !comparisonResults && (
              <div className="space-y-6 md:space-y-8">
                {/* Summary Cards */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-5">
                  <Card className="bg-slate-800/60 backdrop-blur-md border-slate-700/50 shadow-xl card-hover-accent">
                    <CardHeader className="pb-3 md:pb-4">
                      <CardTitle className="text-xs md:text-sm font-medium text-slate-400">
                        Total Metrics
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-3xl md:text-4xl font-bold text-slate-100">{analysisResults.summary.total_metrics}</div>
                    </CardContent>
                  </Card>
                  <Card className="border-orange-500/50 bg-gradient-to-br from-orange-950/40 to-orange-900/20 backdrop-blur-md card-hover-accent ambient-glow-orange shadow-xl">
                    <CardHeader className="pb-3 md:pb-4">
                      <CardTitle className="text-xs md:text-sm font-medium text-orange-300">Fair</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-3xl md:text-4xl font-bold text-orange-400">
                        {analysisResults.summary.fair}
                      </div>
                    </CardContent>
                  </Card>
                  <Card className="border-amber-500/50 bg-gradient-to-br from-amber-950/40 to-amber-900/20 backdrop-blur-md card-hover-accent ambient-glow-amber shadow-xl">
                    <CardHeader className="pb-3 md:pb-4">
                      <CardTitle className="text-xs md:text-sm font-medium text-amber-300">
                        Warnings
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-3xl md:text-4xl font-bold text-amber-400">
                        {analysisResults.summary.warning}
                      </div>
                    </CardContent>
                  </Card>
                  <Card className="border-red-500/50 bg-gradient-to-br from-red-950/40 to-red-900/20 backdrop-blur-md card-hover-accent shadow-xl">
                    <CardHeader className="pb-3 md:pb-4">
                      <CardTitle className="text-xs md:text-sm font-medium text-red-300">
                        Violations
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-3xl md:text-4xl font-bold text-red-400">
                        {analysisResults.summary.violation}
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Overall Fairness Summary Card */}
                {analysisResults && (
                  <Card className="bg-slate-800/60 backdrop-blur-md border-slate-700/50 shadow-xl mb-8">
                    <CardHeader>
                      <CardTitle className="text-slate-100 text-xl">Overall Fairness Summary</CardTitle>
                      <CardDescription className="text-slate-400">
                        Protected Attribute: <strong className="text-slate-200">{analysisResults.protected_attr}</strong>
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {/* Score Display */}
                        <div className="flex flex-col justify-center items-center p-8 bg-gradient-to-br from-slate-900/80 to-slate-800/60 border border-slate-700/50 rounded-xl shadow-inner">
                          <div className="text-6xl font-bold text-orange-400 mb-3">
                            {analysisResults.summary.fair}/{analysisResults.summary.total_metrics}
                          </div>
                          <div className="text-lg font-semibold text-slate-200 mb-1">Fair Metrics</div>
                          <div className={`text-sm font-medium px-3 py-1 rounded-full ${
                            analysisResults.summary.violation === 0 
                              ? 'bg-green-950/50 border border-green-500/50 text-green-300'
                              : analysisResults.summary.violation <= 2
                              ? 'bg-amber-950/50 border border-amber-500/50 text-amber-300'
                              : 'bg-red-950/50 border border-red-500/50 text-red-300'
                          }`}>
                            {analysisResults.summary.violation === 0 
                              ? 'Overall: Fair'
                              : analysisResults.summary.violation <= 2
                              ? 'Overall: Needs Attention'
                              : 'Overall: Critical'}
                          </div>
                        </div>

                        {/* Status Breakdown */}
                        <div className="space-y-3">
                          <div className="flex items-center justify-between p-3 bg-red-950/30 border border-red-500/50 rounded-lg">
                            <div className="flex items-center gap-2">
                              <div className="w-2 h-2 rounded-full bg-red-400"></div>
                              <span className="text-sm font-medium text-red-300">Violations</span>
                            </div>
                            <span className="text-2xl font-bold text-red-400">{analysisResults.summary.violation}</span>
                          </div>
                          <div className="flex items-center justify-between p-3 bg-amber-950/30 border border-amber-500/50 rounded-lg">
                            <div className="flex items-center gap-2">
                              <div className="w-2 h-2 rounded-full bg-amber-400"></div>
                              <span className="text-sm font-medium text-amber-300">Warnings</span>
                            </div>
                            <span className="text-2xl font-bold text-amber-400">{analysisResults.summary.warning}</span>
                          </div>
                          <div className="flex items-center justify-between p-3 bg-green-950/30 border border-green-500/50 rounded-lg">
                            <div className="flex items-center gap-2">
                              <div className="w-2 h-2 rounded-full bg-green-400"></div>
                              <span className="text-sm font-medium text-green-300">Fair</span>
                            </div>
                            <span className="text-2xl font-bold text-green-400">{analysisResults.summary.fair}</span>
                          </div>

                          {/* Priority Issue */}
                          {getPriorityIssue() && (
                            <div className="mt-4 p-3 bg-orange-950/30 border border-orange-500/50 rounded-lg">
                              <p className="text-xs font-semibold text-orange-300 mb-1">Priority Fix</p>
                              <p className="text-sm text-orange-200">{getPriorityIssue()}</p>
                            </div>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Overall Assessment */}
                <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700/50">
                  <CardHeader>
                    <CardTitle className="text-slate-100">Overall Assessment</CardTitle>
                    <CardDescription className="text-slate-400">
                      Protected Attribute: <strong className="text-slate-200">{analysisResults.protected_attr}</strong>
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="text-lg font-semibold">
                      {analysisResults.summary.overall_assessment}
                    </div>
                    <p className="text-sm text-gray-600 mt-2">
                      {analysisResults.summary.overall_assessment === 'Fair'
                        ? 'This dataset shows no significant fairness violations. Continue monitoring for changes.'
                        : 'This dataset requires attention. Review the metrics below for detailed findings and recommendations.'}
                    </p>
                  </CardContent>
                </Card>

                {/* Metrics Tabs */}
                <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700/50">
                  <CardHeader>
                    <CardTitle className="text-slate-100">Fairness Metrics</CardTitle>
                    <CardDescription className="text-slate-400">
                      Detailed analysis of {analysisResults.metrics.length} fairness metrics
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="px-3 md:px-6">
                    <Tabs defaultValue="all" className="w-full">
                      <TabsList className="grid w-full grid-cols-4 h-auto bg-slate-900/50 border-slate-700">
                        <TabsTrigger value="all" className="text-xs md:text-sm py-2 data-[state=active]:bg-orange-600 data-[state=active]:text-white">All</TabsTrigger>
                        <TabsTrigger value="fair" className="text-xs md:text-sm py-2 data-[state=active]:bg-orange-600 data-[state=active]:text-white">Fair ({analysisResults.summary.fair})</TabsTrigger>
                        <TabsTrigger value="warning" className="text-xs md:text-sm py-2 data-[state=active]:bg-orange-600 data-[state=active]:text-white">
                          Warnings ({analysisResults.summary.warning})
                        </TabsTrigger>
                        <TabsTrigger value="violation" className="text-xs md:text-sm py-2 data-[state=active]:bg-orange-600 data-[state=active]:text-white">
                          Violations ({analysisResults.summary.violation})
                        </TabsTrigger>
                      </TabsList>
                      
                      <TabsContent value="all" className="mt-4 md:mt-6 space-y-4 md:space-y-6">
                        {analysisResults.metrics.map((metric: any, index: number) => (
                          <MetricVisualization key={index} metric={metric} />
                        ))}
                      </TabsContent>
                      
                      <TabsContent value="fair" className="mt-4 md:mt-6 space-y-4 md:space-y-6">
                        {analysisResults.metrics
                          .filter((m: any) => m.fairness_assessment === 'Fair')
                          .map((metric: any, index: number) => (
                            <MetricVisualization key={index} metric={metric} />
                          ))}
                      </TabsContent>
                      
                      <TabsContent value="warning" className="mt-4 md:mt-6 space-y-4 md:space-y-6">
                        {analysisResults.metrics
                          .filter((m: any) => m.fairness_assessment === 'Warning')
                          .map((metric: any, index: number) => (
                            <MetricVisualization key={index} metric={metric} />
                          ))}
                      </TabsContent>
                      
                      <TabsContent value="violation" className="mt-4 md:mt-6 space-y-4 md:space-y-6">
                        {analysisResults.metrics
                          .filter((m: any) => m.fairness_assessment === 'Violation')
                          .map((metric: any, index: number) => (
                            <MetricVisualization key={index} metric={metric} />
                          ))}
                      </TabsContent>
                    </Tabs>
                  </CardContent>
                </Card>
              </div>
            )}
          </div>
      </main>

      {/* Footer */}
      <footer className="bg-slate-900/50 backdrop-blur-md border-t border-slate-700/50 mt-8 md:mt-12">
        <div className="container mx-auto px-4 py-4 md:py-6">
          <p className="text-center text-xs md:text-sm text-slate-400">
            AI Fairness Audit Dashboard © 2025
          </p>
        </div>
      </footer>

      {/* Compare Modal */}
      <CompareModal />
    </div>
  );
}

export default App;
