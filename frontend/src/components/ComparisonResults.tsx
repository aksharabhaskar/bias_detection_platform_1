import { useStore } from '@/lib/store';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft, TrendingDown, TrendingUp } from 'lucide-react';

export function ComparisonResults() {
  const { comparisonResults, setComparisonResults } = useStore();

  if (!comparisonResults) return null;

  const { dataset_1, dataset_2, protected_attr, metrics_comparison, summary } = comparisonResults;

  // Debug logging
  console.log('Comparison Results:', comparisonResults);
  console.log('Metrics Comparison:', metrics_comparison);

  return (
    <div className="space-y-6">
      <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700/50">
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle className="text-slate-100">Dataset Comparison</CardTitle>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setComparisonResults(null)}
              className="border-slate-600 bg-slate-900/50 text-slate-200 hover:bg-slate-800 hover:border-slate-500"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Analysis
            </Button>
          </div>
          <div className="text-sm text-slate-400 mt-2">
            <p><span className="font-medium text-slate-300">Dataset 1:</span> {dataset_1}</p>
            <p><span className="font-medium text-slate-300">Dataset 2:</span> {dataset_2}</p>
            <p><span className="font-medium text-slate-300">Protected Attribute:</span> {protected_attr}</p>
          </div>
        </CardHeader>
      </Card>

      {summary && (
        <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700/50">
          <CardHeader>
            <CardTitle className="text-slate-100">Comparison Summary</CardTitle>
          </CardHeader>
          <CardContent>
            {/* Overall Improvement Display */}
            <div className="mb-6 p-6 bg-gradient-to-br from-slate-900/80 to-slate-800/80 border border-slate-700/50 rounded-lg">
              <div className="text-center mb-4">
                <p className="text-sm text-slate-400 mb-2">Overall Improvement</p>
                <div className="flex items-center justify-center gap-4">
                  <span className="text-3xl font-bold text-slate-300">
                    {summary.unchanged + summary.worsened}/{summary.improved + summary.unchanged + summary.worsened}
                  </span>
                  <TrendingUp className="h-8 w-8 text-orange-400" />
                  <span className="text-3xl font-bold text-orange-400">
                    {summary.improved}/{summary.improved + summary.unchanged + summary.worsened}
                  </span>
                </div>
                <p className="text-lg font-semibold text-orange-300 mt-2">
                  {((summary.improved / (summary.improved + summary.unchanged + summary.worsened)) * 100).toFixed(0)}% Improvement
                </p>
              </div>
            </div>

            {/* Detailed Breakdown */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-green-950/30 border border-green-500/50 rounded-lg p-4 backdrop-blur-sm">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm text-green-300">Improved Metrics</p>
                  <TrendingUp className="h-5 w-5 text-green-400" />
                </div>
                <p className="text-3xl font-bold text-green-400">{summary.improved || 0}</p>
                <div className="mt-2 h-2 bg-slate-900/50 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-green-500 rounded-full transition-all"
                    style={{ width: `${(summary.improved / (summary.improved + summary.unchanged + summary.worsened)) * 100}%` }}
                  ></div>
                </div>
              </div>
              <div className="bg-red-950/30 border border-red-500/50 rounded-lg p-4 backdrop-blur-sm">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm text-red-300">Worsened Metrics</p>
                  <TrendingDown className="h-5 w-5 text-red-400" />
                </div>
                <p className="text-3xl font-bold text-red-400">{summary.worsened || 0}</p>
                <div className="mt-2 h-2 bg-slate-900/50 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-red-500 rounded-full transition-all"
                    style={{ width: `${(summary.worsened / (summary.improved + summary.unchanged + summary.worsened)) * 100}%` }}
                  ></div>
                </div>
              </div>
              <div className="bg-slate-800/50 border border-slate-600/50 rounded-lg p-4 backdrop-blur-sm">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm text-slate-300">Unchanged Metrics</p>
                  <div className="h-5 w-5 flex items-center justify-center text-slate-400 font-bold">-</div>
                </div>
                <p className="text-3xl font-bold text-slate-400">{summary.unchanged || 0}</p>
                <div className="mt-2 h-2 bg-slate-900/50 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-slate-600 rounded-full transition-all"
                    style={{ width: `${(summary.unchanged / (summary.improved + summary.unchanged + summary.worsened)) * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="space-y-4">
        {metrics_comparison?.map((comparison: any, idx: number) => (
          <Card key={idx} className="bg-slate-800/50 backdrop-blur-sm border-slate-700/50">
            <CardHeader>
              <CardTitle className="text-lg text-slate-100">{comparison.metric_display_name || comparison.metric_name}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Dataset 1 */}
                <div>
                  <h4 className="font-medium mb-2 text-sm text-slate-400">Dataset 1</h4>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-1 rounded text-xs font-medium backdrop-blur-sm ${
                        comparison.dataset_1_assessment === 'Fair'
                          ? 'bg-orange-950/50 border border-orange-500/50 text-orange-300'
                          : comparison.dataset_1_assessment === 'Warning'
                          ? 'bg-amber-950/50 border border-amber-500/50 text-amber-300'
                          : 'bg-red-950/50 border border-red-500/50 text-red-300'
                      }`}>
                        {comparison.dataset_1_assessment}
                      </span>
                    </div>
                    {comparison.dataset_1_value !== undefined && comparison.dataset_1_value !== null && (
                      <div className="text-sm">
                        <span className="text-slate-400">Value: </span>
                        <span className="font-medium text-slate-200">
                          {typeof comparison.dataset_1_value === 'number'
                            ? comparison.dataset_1_value.toFixed(3)
                            : JSON.stringify(comparison.dataset_1_value)}
                        </span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Dataset 2 */}
                <div>
                  <h4 className="font-medium mb-2 text-sm text-slate-400">Dataset 2</h4>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-1 rounded text-xs font-medium backdrop-blur-sm ${
                        comparison.dataset_2_assessment === 'Fair'
                          ? 'bg-orange-950/50 border border-orange-500/50 text-orange-300'
                          : comparison.dataset_2_assessment === 'Warning'
                          ? 'bg-amber-950/50 border border-amber-500/50 text-amber-300'
                          : 'bg-red-950/50 border border-red-500/50 text-red-300'
                      }`}>
                        {comparison.dataset_2_assessment}
                      </span>
                    </div>
                    {comparison.dataset_2_value !== undefined && comparison.dataset_2_value !== null && (
                      <div className="text-sm">
                        <span className="text-slate-400">Value: </span>
                        <span className="font-medium text-slate-200">
                          {typeof comparison.dataset_2_value === 'number'
                            ? comparison.dataset_2_value.toFixed(3)
                            : JSON.stringify(comparison.dataset_2_value)}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Change Indicator */}
              {comparison.change && (
                <div className={`mt-4 p-3 rounded-lg flex items-center gap-2 backdrop-blur-sm ${
                  comparison.change === 'improved'
                    ? 'bg-orange-950/30 border border-orange-500/30 text-orange-300'
                    : comparison.change === 'worsened'
                    ? 'bg-red-950/30 border border-red-500/30 text-red-300'
                    : 'bg-slate-800/50 border border-slate-600/30 text-slate-300'
                }`}>
                  {comparison.change === 'improved' && <TrendingUp className="h-4 w-4" />}
                  {comparison.change === 'worsened' && <TrendingDown className="h-4 w-4" />}
                  <span className="text-sm font-medium capitalize">{comparison.change}</span>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
