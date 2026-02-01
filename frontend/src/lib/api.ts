import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
// PDF service base URL - prefer full URL from env, otherwise default to local PDF service
const PDF_BASE_URL = (import.meta.env.VITE_PDF_SERVICE_URL && String(import.meta.env.VITE_PDF_SERVICE_URL).startsWith('http'))
  ? String(import.meta.env.VITE_PDF_SERVICE_URL)
  : 'http://localhost:5001';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

// Types
export interface DatasetUploadResponse {
  dataset_id: string;
  filename: string;
  rows: number;
  columns: number;
  column_names: string[];
  upload_date: string;
  has_age_group: boolean;
}

export interface MetricExplanation {
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

export interface MetricResult {
  metric_name: string;
  values: Record<string, any> | number;
  visualization_data?: Record<string, any>;
  fairness_assessment: string;
  explanation: MetricExplanation;
}

export interface AnalysisResponse {
  dataset_id: string;
  protected_attr: string;
  metrics: MetricResult[];
  summary: {
    total_metrics: number;
    violations: number;
    warnings: number;
    acceptable: number;
  };
}

export interface ComparisonMetric {
  metric_name: string;
  dataset1_value: number;
  dataset2_value: number;
  difference: number;
  percentage_change: number;
  interpretation: string;
}

export interface ComparisonResponse {
  dataset_1: string;
  dataset_2: string;
  protected_attr: string;
  metrics_comparison: ComparisonMetric[];
  summary: Record<string, any>;
}

export interface PDFRequest {
  dataset_name: string;
  rows: number;
  columns: number;
  upload_date: string;
  protected_attr: string;
  metrics: MetricResult[];
  summary: Record<string, any>;
}

// API methods
export const api = {
  // Upload dataset
  uploadDataset: async (file: File): Promise<DatasetUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    // Let axios/browser set the Content-Type (including boundary) for FormData
    const response = await apiClient.post('/upload', formData);

    return response.data;
  },

  // Get dataset details
  getDataset: async (datasetId: string): Promise<any> => {
    const response = await apiClient.get(`/dataset/${datasetId}`);
    return response.data;
  },

  // Analyze dataset
  analyzeDataset: async (
    datasetId: string,
    protectedAttr: string
  ): Promise<AnalysisResponse> => {
    const response = await apiClient.post('/analyze', {
      dataset_id: datasetId,
      protected_attr: protectedAttr,
    });

    return response.data;
  },

  // Compare datasets
  compareDatasets: async (
    dataset1Id: string,
    dataset2Id: string,
    protectedAttr: string
  ): Promise<ComparisonResponse> => {
    const response = await apiClient.post('/compare', {
      dataset_id_1: dataset1Id,
      dataset_id_2: dataset2Id,
      protected_attr: protectedAttr,
    });

    return response.data;
  },

  // Get metric definitions
  getMetrics: async (): Promise<any> => {
    const response = await apiClient.get('/metrics');
    return response.data;
  },

  // Generate PDF report
  generatePDF: async (data: PDFRequest): Promise<Blob> => {
    const response = await axios.post(`${PDF_BASE_URL}/generate-pdf`, data, {
      responseType: 'blob',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    return response.data;
  },
};

export default api;
