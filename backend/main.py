from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import os
import json
from pathlib import Path
from typing import Optional, List
from dotenv import load_dotenv

from models import (
    DatasetUploadResponse, DatasetPreview, AnalysisRequest,
    ComparisonRequest, MetricResult, AnalysisResponse,
    ComparisonResponse, MetricDefinition
)
from fairness_metrics import FairnessMetrics
from metric_definitions import get_metric_definition, get_all_metrics
from assessment_classifier import classify_assessment, get_value_segment_info
from utils import (
    process_uploaded_dataset, get_dataset_statistics,
    validate_protected_attribute, prepare_dataframe_for_json
)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="AI Fairness Audit API",
    description="Backend API for AI Fairness Audit Dashboard",
    version="1.0.0"
)

# CORS configuration
origins = os.getenv("CORS_ORIGINS", "http://localhost,http://localhost:80,http://localhost:5173,http://localhost:5174").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage configuration
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./uploads"))
UPLOAD_DIR.mkdir(exist_ok=True)

# In-memory storage for dataset metadata (in production, use a database)
datasets = {}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Fairness Audit API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/api/upload",
            "dataset": "/api/dataset/{id}",
            "analyze": "/api/analyze",
            "compare": "/api/compare",
            "metrics": "/api/metrics"
        }
    }

@app.post("/api/upload", response_model=DatasetUploadResponse)
async def upload_dataset(file: UploadFile = File(...)):
    """
    Upload a CSV dataset for analysis
    Returns dataset ID and metadata
    """
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only CSV files are supported"
            )
        
        # Read CSV file
        contents = await file.read()
        
        # Check file size (max 10MB)
        max_size = int(os.getenv("MAX_FILE_SIZE", 10485760))
        if len(contents) > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds {max_size} bytes"
            )
        
        # Parse CSV
        try:
            df = pd.read_csv(pd.io.common.BytesIO(contents))
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error parsing CSV: {str(e)}"
            )
        
        # Process dataset
        df, metadata = process_uploaded_dataset(df, file.filename)
        
        # Save dataset
        dataset_id = metadata['dataset_id']
        dataset_path = UPLOAD_DIR / f"{dataset_id}.csv"
        df.to_csv(dataset_path, index=False)
        
        # Save metadata
        metadata_path = UPLOAD_DIR / f"{dataset_id}_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f)
        
        # Store in memory
        datasets[dataset_id] = {
            'df': df,
            'metadata': metadata
        }
        
        return DatasetUploadResponse(**metadata)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing upload: {str(e)}"
        )

@app.get("/api/dataset/{dataset_id}", response_model=DatasetPreview)
async def get_dataset(dataset_id: str, rows: Optional[int] = 100):
    """
    Get dataset preview and statistics
    """
    try:
        # Check if dataset exists
        if dataset_id not in datasets:
            # Try to load from disk
            dataset_path = UPLOAD_DIR / f"{dataset_id}.csv"
            metadata_path = UPLOAD_DIR / f"{dataset_id}_metadata.json"
            
            if not dataset_path.exists() or not metadata_path.exists():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Dataset not found"
                )
            
            # Load dataset
            df = pd.read_csv(dataset_path)
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            datasets[dataset_id] = {'df': df, 'metadata': metadata}
        
        df = datasets[dataset_id]['df']
        metadata = datasets[dataset_id]['metadata']
        
        # Get statistics
        statistics = get_dataset_statistics(df)
        
        # Prepare preview data
        preview_data = prepare_dataframe_for_json(df, max_rows=rows)
        
        return DatasetPreview(
            dataset_id=dataset_id,
            filename=metadata['filename'],
            rows=metadata['rows'],
            columns=metadata['columns'],
            data=preview_data,
            statistics=statistics
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving dataset: {str(e)}"
        )

@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_dataset(request: AnalysisRequest):
    """
    Analyze dataset for fairness metrics
    If metric_name is provided, calculate only that metric
    Otherwise, calculate all metrics
    """
    try:
        # Load dataset
        if request.dataset_id not in datasets:
            dataset_path = UPLOAD_DIR / f"{request.dataset_id}.csv"
            if not dataset_path.exists():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Dataset not found"
                )
            df = pd.read_csv(dataset_path)
            metadata_path = UPLOAD_DIR / f"{request.dataset_id}_metadata.json"
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            datasets[request.dataset_id] = {'df': df, 'metadata': metadata}
        
        df = datasets[request.dataset_id]['df']
        
        # Validate protected attribute
        validate_protected_attribute(df, request.protected_attr)
        
        # Initialize fairness metrics calculator
        fairness = FairnessMetrics(df, request.protected_attr)
        
        # Define all metric methods
        metric_methods = {
            'demographic_parity': fairness.demographic_parity,
            'disparate_impact': fairness.disparate_impact,
            'equal_opportunity': fairness.equal_opportunity,
            'predictive_equality': fairness.predictive_equality,
            'calibration_by_group': fairness.calibration_by_group,
            'false_negative_rate_parity': fairness.false_negative_rate_parity,
            'false_discovery_rate_parity': fairness.false_discovery_rate_parity,
            'accuracy_equality': fairness.accuracy_equality,
            'predictive_parity_ppv': fairness.predictive_parity_ppv,
            'equalized_odds': fairness.equalized_odds,
            'statistical_parity_difference': fairness.statistical_parity_difference,
            'average_odds_difference': fairness.average_odds_difference,
            'theil_index': fairness.theil_index
        }
        
        # Calculate metrics
        metrics_to_calculate = [request.metric_name] if request.metric_name else list(metric_methods.keys())
        results = []
        
        for metric_name in metrics_to_calculate:
            if metric_name not in metric_methods:
                continue
            
            # Calculate metric
            metric_result = metric_methods[metric_name]()
            
            # Get definition
            definition = get_metric_definition(metric_name)
            
            # Extract the primary value for classification
            values = metric_result.get('values', metric_result.get('value', {}))
            
            # Determine the assessment value based on metric type
            if metric_name == 'disparate_impact':
                # For DI, use the minimum ratio
                if isinstance(values, dict):
                    numeric_values = [v for v in values.values() if isinstance(v, (int, float))]
                    assessment_value = min(numeric_values) if numeric_values else 1.0
                else:
                    assessment_value = float(values) if isinstance(values, (int, float)) else 1.0
            elif metric_name in ['demographic_parity', 'equal_opportunity', 'predictive_equality', 
                                  'false_negative_rate_parity', 'false_discovery_rate_parity',
                                  'accuracy_equality', 'predictive_parity_ppv', 'calibration_by_group']:
                # For these, calculate max difference between groups
                if isinstance(values, dict):
                    numeric_values = [v for v in values.values() if isinstance(v, (int, float))]
                    assessment_value = max(numeric_values) - min(numeric_values) if numeric_values else 0.0
                else:
                    assessment_value = abs(float(values)) if isinstance(values, (int, float)) else 0.0
            elif metric_name == 'equalized_odds':
                # For equalized odds, get max of TPR and FPR differences
                if isinstance(values, dict):
                    tpr_values = [v.get('tpr', 0) for v in values.values() if isinstance(v, dict) and 'tpr' in v]
                    fpr_values = [v.get('fpr', 0) for v in values.values() if isinstance(v, dict) and 'fpr' in v]
                    tpr_diff = max(tpr_values) - min(tpr_values) if len(tpr_values) > 1 else 0
                    fpr_diff = max(fpr_values) - min(fpr_values) if len(fpr_values) > 1 else 0
                    assessment_value = max(tpr_diff, fpr_diff)
                else:
                    assessment_value = abs(float(values)) if isinstance(values, (int, float)) else 0.0
            else:
                # For single value metrics (SPD, AOD, Theil)
                assessment_value = abs(float(values)) if isinstance(values, (int, float)) else 0.0
            
            # Classify assessment using value segments
            fairness_assessment = classify_assessment(metric_name, assessment_value)
            
            # Get value segment information
            segment_info = get_value_segment_info(metric_name, assessment_value)
            
            # Add segment info to definition
            definition_with_segment = {**definition, 'current_segment': segment_info}
            
            # Create result
            result = MetricResult(
                metric_name=metric_name,
                values=values,
                visualization_data=metric_result,
                fairness_assessment=fairness_assessment,
                explanation=definition_with_segment
            )
            results.append(result)
        
        # Create summary
        fair_count = sum(1 for r in results if r.fairness_assessment == "Fair")
        warning_count = sum(1 for r in results if r.fairness_assessment == "Warning")
        violation_count = sum(1 for r in results if r.fairness_assessment == "Violation")
        
        summary = {
            'total_metrics': len(results),
            'fair': fair_count,
            'warning': warning_count,
            'violation': violation_count,
            'overall_assessment': 'Fair' if violation_count == 0 and warning_count == 0 else 'Needs Attention'
        }
        
        return AnalysisResponse(
            dataset_id=request.dataset_id,
            protected_attr=request.protected_attr,
            metrics=results,
            summary=summary
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing dataset: {str(e)}"
        )

@app.post("/api/compare", response_model=ComparisonResponse)
async def compare_datasets(request: ComparisonRequest):
    """
    Compare fairness metrics between two datasets
    """
    try:
        # Load both datasets
        datasets_to_compare = []
        for dataset_id in [request.dataset_id_1, request.dataset_id_2]:
            if dataset_id not in datasets:
                dataset_path = UPLOAD_DIR / f"{dataset_id}.csv"
                if not dataset_path.exists():
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Dataset {dataset_id} not found"
                    )
                df = pd.read_csv(dataset_path)
                metadata_path = UPLOAD_DIR / f"{dataset_id}_metadata.json"
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                datasets[dataset_id] = {'df': df, 'metadata': metadata}
            
            datasets_to_compare.append(datasets[dataset_id])
        
        # Validate protected attribute for both datasets
        for ds in datasets_to_compare:
            validate_protected_attribute(ds['df'], request.protected_attr)
        
        # Calculate metrics for both datasets
        comparison_results = []
        all_metrics = get_all_metrics()
        
        # Create FairnessMetrics instances
        dataset_1_fairness = FairnessMetrics(datasets_to_compare[0]['df'], request.protected_attr)
        dataset_2_fairness = FairnessMetrics(datasets_to_compare[1]['df'], request.protected_attr)
        
        for metric_name, metric_info in all_metrics.items():
            method_name = metric_info.get('method_name', metric_name)
            
            # Calculate metrics
            result_1 = getattr(dataset_1_fairness, method_name)()
            result_2 = getattr(dataset_2_fairness, method_name)()
            
            # Extract assessment values for classification (MUST match logic in analyze endpoint)
            try:
                # Extract values from results
                values_1 = result_1.get('values', result_1.get('value', {}))
                values_2 = result_2.get('values', result_2.get('value', {}))
                
                if metric_name == 'disparate_impact':
                    # For DI, use the minimum ratio
                    if isinstance(values_1, dict):
                        numeric_values = [v for v in values_1.values() if isinstance(v, (int, float))]
                        value_1 = min(numeric_values) if numeric_values else 1.0
                    else:
                        value_1 = float(values_1) if isinstance(values_1, (int, float)) else 1.0
                    
                    if isinstance(values_2, dict):
                        numeric_values = [v for v in values_2.values() if isinstance(v, (int, float))]
                        value_2 = min(numeric_values) if numeric_values else 1.0
                    else:
                        value_2 = float(values_2) if isinstance(values_2, (int, float)) else 1.0
                        
                elif metric_name in ['demographic_parity', 'equal_opportunity', 'predictive_equality', 
                                      'false_negative_rate_parity', 'false_discovery_rate_parity',
                                      'accuracy_equality', 'predictive_parity_ppv', 'calibration_by_group']:
                    # For these, calculate max difference between groups
                    if isinstance(values_1, dict):
                        numeric_values = [v for v in values_1.values() if isinstance(v, (int, float))]
                        value_1 = max(numeric_values) - min(numeric_values) if numeric_values else 0.0
                    else:
                        value_1 = abs(float(values_1)) if isinstance(values_1, (int, float)) else 0.0
                    
                    if isinstance(values_2, dict):
                        numeric_values = [v for v in values_2.values() if isinstance(v, (int, float))]
                        value_2 = max(numeric_values) - min(numeric_values) if numeric_values else 0.0
                    else:
                        value_2 = abs(float(values_2)) if isinstance(values_2, (int, float)) else 0.0
                        
                elif metric_name == 'equalized_odds':
                    # For equalized odds, get max of TPR and FPR differences
                    if isinstance(values_1, dict):
                        tpr_values = [v.get('tpr', 0) for v in values_1.values() if isinstance(v, dict) and 'tpr' in v]
                        fpr_values = [v.get('fpr', 0) for v in values_1.values() if isinstance(v, dict) and 'fpr' in v]
                        tpr_diff = max(tpr_values) - min(tpr_values) if len(tpr_values) > 1 else 0
                        fpr_diff = max(fpr_values) - min(fpr_values) if len(fpr_values) > 1 else 0
                        value_1 = max(tpr_diff, fpr_diff)
                    else:
                        value_1 = abs(float(values_1)) if isinstance(values_1, (int, float)) else 0.0
                    
                    if isinstance(values_2, dict):
                        tpr_values = [v.get('tpr', 0) for v in values_2.values() if isinstance(v, dict) and 'tpr' in v]
                        fpr_values = [v.get('fpr', 0) for v in values_2.values() if isinstance(v, dict) and 'fpr' in v]
                        tpr_diff = max(tpr_values) - min(tpr_values) if len(tpr_values) > 1 else 0
                        fpr_diff = max(fpr_values) - min(fpr_values) if len(fpr_values) > 1 else 0
                        value_2 = max(tpr_diff, fpr_diff)
                    else:
                        value_2 = abs(float(values_2)) if isinstance(values_2, (int, float)) else 0.0
                else:
                    # For single value metrics (SPD, AOD, Theil)
                    value_1 = abs(float(values_1)) if isinstance(values_1, (int, float)) else 0.0
                    value_2 = abs(float(values_2)) if isinstance(values_2, (int, float)) else 0.0
            except Exception as e:
                print(f"Error extracting value for {metric_name}: {e}")
                value_1 = 0
                value_2 = 0
            
            # Classify assessments
            assessment_1 = classify_assessment(metric_name, value_1) if value_1 is not None else "Unknown"
            assessment_2 = classify_assessment(metric_name, value_2) if value_2 is not None else "Unknown"
            
            # Determine change
            severity_order = {"Fair": 0, "Warning": 1, "Violation": 2, "Unknown": 3}
            severity_1 = severity_order.get(assessment_1, 3)
            severity_2 = severity_order.get(assessment_2, 3)
            
            if severity_2 < severity_1:
                change = "improved"
            elif severity_2 > severity_1:
                change = "worsened"
            else:
                change = "unchanged"
            
            comparison = {
                'metric_name': metric_name,
                'metric_display_name': metric_info.get('display_name', metric_name),
                'dataset_1_value': value_1,
                'dataset_2_value': value_2,
                'dataset_1_assessment': assessment_1,
                'dataset_2_assessment': assessment_2,
                'change': change
            }
            comparison_results.append(comparison)
        
        # Create summary
        improved = sum(1 for r in comparison_results if r['change'] == 'improved')
        worsened = sum(1 for r in comparison_results if r['change'] == 'worsened')
        unchanged = sum(1 for r in comparison_results if r['change'] == 'unchanged')
        
        summary = {
            'total_metrics': len(comparison_results),
            'improved': improved,
            'worsened': worsened,
            'unchanged': unchanged,
            'overall': 'Improved' if improved > worsened else 'Worsened' if worsened > improved else 'Similar'
        }
        
        return ComparisonResponse(
            dataset_1=datasets_to_compare[0]['metadata']['filename'],
            dataset_2=datasets_to_compare[1]['metadata']['filename'],
            protected_attr=request.protected_attr,
            metrics_comparison=comparison_results,
            summary=summary
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error comparing datasets: {str(e)}"
        )

@app.get("/api/metrics", response_model=List[MetricDefinition])
async def get_metrics():
    """
    Get all available fairness metrics with their definitions
    """
    try:
        all_metrics = get_all_metrics()
        return [MetricDefinition(**metric) for metric in all_metrics.values()]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving metrics: {str(e)}"
        )

@app.delete("/api/dataset/{dataset_id}")
async def delete_dataset(dataset_id: str):
    """
    Delete a dataset
    """
    try:
        # Remove from memory
        if dataset_id in datasets:
            del datasets[dataset_id]
        
        # Remove from disk
        dataset_path = UPLOAD_DIR / f"{dataset_id}.csv"
        metadata_path = UPLOAD_DIR / f"{dataset_id}_metadata.json"
        
        if dataset_path.exists():
            dataset_path.unlink()
        if metadata_path.exists():
            metadata_path.unlink()
        
        return {"message": "Dataset deleted successfully"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting dataset: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("FASTAPI_HOST", "localhost")
    port = int(os.getenv("FASTAPI_PORT", 8000))
    uvicorn.run(app, host=host, port=port)
