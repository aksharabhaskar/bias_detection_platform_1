import pandas as pd
import numpy as np
from typing import Optional
import uuid
from datetime import datetime

def generate_age_group(age: int) -> str:
    """Generate age group from age value"""
    if 20 <= age <= 30:
        return "20-30"
    elif 31 <= age <= 40:
        return "31-40"
    elif 41 <= age <= 50:
        return "41-50"
    elif 51 <= age <= 60:
        return "51-60"
    else:
        return "Other"

def process_uploaded_dataset(df: pd.DataFrame, filename: str) -> dict:
    """
    Process uploaded dataset: generate age_group, validate columns, create metadata
    """
    # Generate unique dataset ID
    dataset_id = str(uuid.uuid4())
    
    # Generate age_group if age column exists and age_group doesn't
    if 'age' in df.columns and 'age_group' not in df.columns:
        df['age_group'] = df['age'].apply(generate_age_group)
        has_age_group = True
    else:
        has_age_group = 'age_group' in df.columns
    
    # Validate required columns
    required_columns = ['shortlisted']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    # Create metadata
    metadata = {
        'dataset_id': dataset_id,
        'filename': filename,
        'rows': len(df),
        'columns': len(df.columns),
        'column_names': df.columns.tolist(),
        'upload_date': datetime.now().isoformat(),
        'has_age_group': has_age_group,
        'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()}
    }
    
    return df, metadata

def get_dataset_statistics(df: pd.DataFrame) -> dict:
    """Calculate basic statistics for the dataset"""
    stats = {
        'rows': len(df),
        'columns': len(df.columns),
        'numeric_columns': df.select_dtypes(include=[np.number]).columns.tolist(),
        'categorical_columns': df.select_dtypes(include=['object', 'category']).columns.tolist(),
        'missing_values': df.isnull().sum().to_dict(),
        'column_stats': {}
    }
    
    # Get basic stats for numeric columns
    for col in stats['numeric_columns']:
        stats['column_stats'][col] = {
            'mean': float(df[col].mean()) if not df[col].isnull().all() else None,
            'median': float(df[col].median()) if not df[col].isnull().all() else None,
            'min': float(df[col].min()) if not df[col].isnull().all() else None,
            'max': float(df[col].max()) if not df[col].isnull().all() else None,
            'std': float(df[col].std()) if not df[col].isnull().all() else None
        }
    
    # Get value counts for categorical columns
    for col in stats['categorical_columns']:
        value_counts = df[col].value_counts().head(10).to_dict()
        stats['column_stats'][col] = {
            'unique_values': int(df[col].nunique()),
            'top_values': {str(k): int(v) for k, v in value_counts.items()}
        }
    
    return stats

def validate_protected_attribute(df: pd.DataFrame, protected_attr: str) -> bool:
    """Validate that the protected attribute exists and has valid values"""
    if protected_attr not in df.columns:
        raise ValueError(f"Protected attribute '{protected_attr}' not found in dataset")
    
    if df[protected_attr].isnull().all():
        raise ValueError(f"Protected attribute '{protected_attr}' has no valid values")
    
    unique_values = df[protected_attr].nunique()
    if unique_values < 2:
        raise ValueError(f"Protected attribute '{protected_attr}' must have at least 2 unique values")
    
    return True

def prepare_dataframe_for_json(df: pd.DataFrame, max_rows: Optional[int] = None) -> list:
    """Convert DataFrame to JSON-serializable list of dicts"""
    if max_rows:
        df = df.head(max_rows)
    
    # Replace NaN with None for JSON serialization
    df = df.replace({np.nan: None})
    
    # Convert to list of dicts
    return df.to_dict(orient='records')
