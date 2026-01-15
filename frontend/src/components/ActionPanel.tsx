
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { BarChart3, FileDown, GitCompare } from 'lucide-react';
import { useStore } from '@/lib/store';
import { api } from '@/lib/api';

export function ActionPanel() {
  const {
    currentDataset,
    protectedAttribute,
    setAnalysisResults,
    setLoading,
    setError,
    analysisResults,
    datasets,
    setShowCompareModal,
    setShowSuccessMessage,
  } = useStore();

  const handleAnalyze = async () => {
    if (!currentDataset) {
      setError('Please upload a dataset first');
      return;
    }

    setLoading(true);
    setError(null);
    setShowSuccessMessage(false);

    try {
      const results = await api.analyzeDataset(currentDataset.dataset_id, protectedAttribute);
      setAnalysisResults(results);
      setShowSuccessMessage(true);
    } catch (error: any) {
      console.error('Analysis error:', error);
      setError(error.response?.data?.detail || 'Failed to analyze dataset');
    } finally {
      setLoading(false);
    }
  };

  const handleExportPDF = async () => {
    if (!analysisResults || !currentDataset) {
      setError('Please analyze a dataset first');
      return;
    }

    setLoading(true);

    try {
      const pdfData = {
        dataset_name: currentDataset.filename,
        rows: currentDataset.rows,
        columns: currentDataset.columns,
        upload_date: currentDataset.upload_date,
        protected_attr: protectedAttribute,
        metrics: analysisResults.metrics,
        summary: analysisResults.summary,
      };

      const blob = await api.generatePDF(pdfData);
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `fairness_audit_${currentDataset.filename.replace('.csv', '')}_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error: any) {
      console.error('PDF generation error:', error);
      setError('Failed to generate PDF report');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700/50">
      <CardHeader>
        <CardTitle className="text-slate-100">Actions</CardTitle>
        <CardDescription className="text-slate-400">Analyze your dataset and export results</CardDescription>
      </CardHeader>
      <CardContent className="space-y-2">
        <Button
          className="w-full bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-500 hover:to-orange-400 text-white shadow-lg shadow-orange-500/30 hover:shadow-orange-500/50 transition-all disabled:opacity-50 disabled:shadow-none"
          onClick={handleAnalyze}
          disabled={!currentDataset}
        >
          <BarChart3 className="mr-2 h-4 w-4" />
          Analyze Fairness
        </Button>

        <Button
          className="w-full border-slate-600 bg-slate-900/50 text-slate-200 hover:bg-slate-800 hover:border-slate-500 hover:shadow-lg hover:shadow-blue-500/20 transition-all disabled:opacity-50"
          variant="outline"
          onClick={handleExportPDF}
          disabled={!analysisResults}
        >
          <FileDown className="mr-2 h-4 w-4" />
          Export PDF Report
        </Button>

        <Button
          className="w-full border-slate-600 bg-slate-900/50 text-slate-200 hover:bg-slate-800 hover:border-slate-500 hover:shadow-lg hover:shadow-violet-500/20 transition-all disabled:opacity-50"
          variant="outline"
          onClick={() => setShowCompareModal(true)}
          disabled={datasets.length < 2}
        >
          <GitCompare className="mr-2 h-4 w-4" />
          Compare Datasets
        </Button>

        {!currentDataset && (
          <p className="text-xs text-gray-500 mt-2">
            Upload a dataset to enable analysis
          </p>
        )}
      </CardContent>
    </Card>
  );
}
