import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileCheck, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { api } from '@/lib/api';
import { useStore } from '@/lib/store';
import { cn } from '@/lib/utils';

export function DatasetUpload() {
  const { addDataset, setLoading, setError } = useStore();
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
  const [uploadedFile, setUploadedFile] = useState<string | null>(null);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    setUploadStatus('uploading');
    setLoading(true);
    setError(null);

    try {
      const response = await api.uploadDataset(file);
      addDataset(response);
      setUploadedFile(file.name);
      setUploadStatus('success');
    } catch (error: any) {
      console.error('Upload error:', error);
      setError(error.response?.data?.detail || 'Failed to upload dataset');
      setUploadStatus('error');
    } finally {
      setLoading(false);
    }
  }, [addDataset, setLoading, setError]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
    },
    maxFiles: 1,
    maxSize: 10485760, // 10MB
  });

  return (
    <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700/50">
      <CardHeader>
        <CardTitle className="text-slate-100">Upload Dataset</CardTitle>
        <CardDescription className="text-slate-400">
          Upload a CSV file containing recruitment data for fairness analysis
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div
          {...getRootProps()}
          className={cn(
            'border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors',
            isDragActive ? 'border-orange-400 bg-orange-950/30' : 'border-slate-600 hover:border-orange-400',
            uploadStatus === 'success' && 'border-orange-500 bg-orange-950/30',
            uploadStatus === 'error' && 'border-red-500 bg-red-950/30'
          )}
        >
          <input {...getInputProps()} />
          
          {uploadStatus === 'idle' && (
            <>
              <Upload className="mx-auto h-12 w-12 text-slate-400" />
              <p className="mt-4 text-sm text-slate-300">
                {isDragActive ? 'Drop the CSV file here' : 'Drag & drop a CSV file here, or click to select'}
              </p>
              <p className="mt-2 text-xs text-slate-400">Maximum file size: 10MB</p>
            </>
          )}
          
          {uploadStatus === 'uploading' && (
            <>
              <div className="animate-spin mx-auto h-12 w-12 border-4 border-orange-500 border-t-transparent rounded-full"></div>
              <p className="mt-4 text-sm text-slate-300">Uploading and processing...</p>
            </>
          )}
          
          {uploadStatus === 'success' && (
            <>
              <FileCheck className="mx-auto h-12 w-12 text-orange-400" />
              <p className="mt-4 text-sm text-orange-300">Successfully uploaded: {uploadedFile}</p>
              <Button
                variant="outline"
                size="sm"
                className="mt-4"
                onClick={(e) => {
                  e.stopPropagation();
                  setUploadStatus('idle');
                  setUploadedFile(null);
                }}
              >
                Upload Another File
              </Button>
            </>
          )}
          
          {uploadStatus === 'error' && (
            <>
              <AlertCircle className="mx-auto h-12 w-12 text-red-400" />
              <p className="mt-4 text-sm text-red-300">Upload failed. Please try again.</p>
              <Button
                variant="outline"
                size="sm"
                className="mt-4"
                onClick={(e) => {
                  e.stopPropagation();
                  setUploadStatus('idle');
                }}
              >
                Try Again
              </Button>
            </>
          )}
        </div>

        {uploadStatus === 'success' && (
          <div className="mt-4 p-4 bg-slate-800/50 border border-slate-700 rounded-lg">
            <p className="text-sm text-slate-300">
              <strong className="text-orange-400">Note:</strong> If your dataset contains an 'age' column, age groups (20-30, 31-40, 41-50, 51-60) 
              have been automatically generated for fairness analysis.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
