from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union
from datetime import datetime

class DatasetUploadResponse(BaseModel):
    dataset_id: str
    filename: str
    rows: int
    columns: int
    column_names: List[str]
    upload_date: str
    has_age_group: bool

class DatasetPreview(BaseModel):
    dataset_id: str
    filename: str
    rows: int
    columns: int
    data: List[Dict[str, Any]]
    statistics: Dict[str, Any]

class AnalysisRequest(BaseModel):
    dataset_id: str
    protected_attr: str
    metric_name: Optional[str] = None

class ComparisonRequest(BaseModel):
    dataset_id_1: str
    dataset_id_2: str
    protected_attr: str

class MetricResult(BaseModel):
    metric_name: str
    values: Union[Dict[str, Any], float, int]
    visualization_data: Optional[Dict[str, Any]] = None
    fairness_assessment: str
    explanation: Dict[str, Any]  # Changed from Dict[str, str] to Dict[str, Any] to support lists and nested dicts

class AnalysisResponse(BaseModel):
    dataset_id: str
    protected_attr: str
    metrics: List[MetricResult]
    summary: Dict[str, Any]

class ComparisonResponse(BaseModel):
    dataset_1: str
    dataset_2: str
    protected_attr: str
    metrics_comparison: List[Dict[str, Any]]
    summary: Dict[str, Any]

class MetricDefinition(BaseModel):
    name: str
    display_name: str
    definition: str
    interpretation: str
    context: str
    what_this_means: Optional[str] = None
    what_is_wrong: Optional[str] = None
    root_causes: Optional[List[str]] = None
    recruiter_actions: Optional[List[str]] = None
    dashboard_recommendation: Optional[str] = None
    value_segments: Optional[List[Dict[str, Any]]] = None
