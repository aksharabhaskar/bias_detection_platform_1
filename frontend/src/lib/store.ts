import { create } from 'zustand';

interface Dataset {
  dataset_id: string;
  filename: string;
  rows: number;
  columns: number;
  column_names: string[];
  upload_date: string;
  has_age_group: boolean;
}

interface MetricExplanation {
  display_name: string;
  description: string;
  interpretation: string;
  context?: string;
  what_this_means?: string;
  what_is_wrong?: string;
  root_causes?: string[];
  recruiter_actions?: string[];
  dashboard_recommendation?: string;
}

interface Metric {
  metric_name: string;
  values: Record<string, any> | number;
  visualization_data?: Record<string, any>;
  fairness_assessment: string;
  explanation: MetricExplanation;
}

interface AnalysisResults {
  dataset_id: string;
  protected_attr: string;
  metrics: Metric[];
  summary: {
    total_metrics: number;
    violations: number;
    warnings: number;
    acceptable: number;
  };
}

interface ComparisonResults {
  dataset_1: string;
  dataset_2: string;
  protected_attr: string;
  metrics_comparison: Array<{
    metric_name: string;
    dataset1_value: number;
    dataset2_value: number;
    difference: number;
    percentage_change: number;
    interpretation: string;
  }>;
  summary: Record<string, any>;
}

interface Store {
  // State
  currentDataset: Dataset | null;
  comparisonDataset: Dataset | null;
  datasets: Dataset[];
  protectedAttribute: string;
  analysisResults: AnalysisResults | null;
  comparisonResults: ComparisonResults | null;
  isLoading: boolean;
  error: string | null;
  showLandingPage: boolean;
  showCompareModal: boolean;
  showSuccessMessage: boolean;

  // Actions
  setCurrentDataset: (dataset: Dataset | null) => void;
  setComparisonDataset: (dataset: Dataset | null) => void;
  addDataset: (dataset: Dataset) => void;
  setProtectedAttribute: (attribute: string) => void;
  setAnalysisResults: (results: AnalysisResults | null) => void;
  setComparisonResults: (results: ComparisonResults | null) => void;
  setIsLoading: (loading: boolean) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setShowLandingPage: (show: boolean) => void;
  setShowCompareModal: (show: boolean) => void;
  setShowSuccessMessage: (show: boolean) => void;
  reset: () => void;
}

export const useStore = create<Store>((set) => ({
  // Initial state
  currentDataset: null,
  comparisonDataset: null,
  datasets: [],
  protectedAttribute: '',
  analysisResults: null,
  comparisonResults: null,
  isLoading: false,
  error: null,
  showLandingPage: true,
  showCompareModal: false,
  showSuccessMessage: false,

  // Actions
  setCurrentDataset: (dataset) => set({ currentDataset: dataset }),
  setComparisonDataset: (dataset) => set({ comparisonDataset: dataset }),
  addDataset: (dataset) => set((state) => ({
    datasets: [...state.datasets, dataset],
    currentDataset: dataset,
  })),
  setProtectedAttribute: (attribute) => set({ protectedAttribute: attribute }),
  setAnalysisResults: (results) => set({ analysisResults: results }),
  setComparisonResults: (results) => set({ comparisonResults: results }),
  setIsLoading: (loading) => set({ isLoading: loading }),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error: error }),
  setShowLandingPage: (show) => set({ showLandingPage: show }),
  setShowCompareModal: (show) => set({ showCompareModal: show }),
  setShowSuccessMessage: (show) => set({ showSuccessMessage: show }),
  reset: () =>
    set({
      currentDataset: null,
      comparisonDataset: null,
      protectedAttribute: '',
      analysisResults: null,
      comparisonResults: null,
      isLoading: false,
      error: null,
      showCompareModal: false,
      showSuccessMessage: false,
    }),
}));
