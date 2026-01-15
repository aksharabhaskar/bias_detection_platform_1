import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { X } from 'lucide-react';
import { useStore } from '@/lib/store';
import { api } from '@/lib/api';

export function CompareModal() {
  const {
    datasets,
    protectedAttribute,
    showCompareModal,
    setShowCompareModal,
    setComparisonResults,
    setLoading,
    setError,
  } = useStore();

  const [dataset1Id, setDataset1Id] = useState<string>('');
  const [dataset2Id, setDataset2Id] = useState<string>('');

  const handleCompare = async () => {
    if (!dataset1Id || !dataset2Id) {
      setError('Please select two datasets to compare');
      return;
    }

    if (dataset1Id === dataset2Id) {
      setError('Please select two different datasets');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const results = await api.compareDatasets(dataset1Id, dataset2Id, protectedAttribute);
      setComparisonResults(results);
      setShowCompareModal(false);
    } catch (error: any) {
      console.error('Comparison error:', error);
      setError(error.response?.data?.detail || 'Failed to compare datasets');
    } finally {
      setLoading(false);
    }
  };

  if (!showCompareModal) return null;

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <Card className="w-full max-w-md bg-slate-800/95 backdrop-blur-md border-slate-700/50">
        <CardHeader>
          <div className="flex justify-between items-start">
            <div>
              <CardTitle className="text-slate-100">Compare Datasets</CardTitle>
              <CardDescription className="text-slate-400">Select two datasets to compare their fairness metrics</CardDescription>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setShowCompareModal(false)}
              className="text-slate-400 hover:text-slate-200 hover:bg-slate-700"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium mb-2 block text-slate-300">First Dataset</label>
            <select
              className="w-full border border-slate-600 bg-slate-900/50 text-slate-200 rounded-md p-2 focus:outline-none focus:ring-2 focus:ring-orange-500"
              value={dataset1Id}
              onChange={(e) => setDataset1Id(e.target.value)}
            >
              <option value="">Select dataset...</option>
              {datasets.map((ds) => (
                <option key={ds.dataset_id} value={ds.dataset_id}>
                  {ds.filename}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-sm font-medium mb-2 block text-slate-300">Second Dataset</label>
            <select
              className="w-full border border-slate-600 bg-slate-900/50 text-slate-200 rounded-md p-2 focus:outline-none focus:ring-2 focus:ring-orange-500"
              value={dataset2Id}
              onChange={(e) => setDataset2Id(e.target.value)}
            >
              <option value="">Select dataset...</option>
              {datasets.map((ds) => (
                <option key={ds.dataset_id} value={ds.dataset_id}>
                  {ds.filename}
                </option>
              ))}
            </select>
          </div>

          <div className="text-sm text-slate-400">
            <p>Protected attribute: <span className="font-medium text-slate-200">{protectedAttribute}</span></p>
          </div>

          <div className="flex gap-2">
            <Button
              className="flex-1 bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-500 hover:to-orange-400 shadow-lg shadow-orange-500/30 hover:shadow-orange-500/50"
              onClick={handleCompare}
              disabled={!dataset1Id || !dataset2Id}
            >
              Compare
            </Button>
            <Button
              className="flex-1 border-slate-600 bg-slate-900/50 text-slate-200 hover:bg-slate-800"
              variant="outline"
              onClick={() => setShowCompareModal(false)}
            >
              Cancel
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
