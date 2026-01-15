"""
Helper functions to classify fairness assessment based on value segments
"""
from metric_definitions import get_metric_definition


def classify_assessment(metric_name: str, value: float) -> str:
    """
    Classify the fairness assessment based on the metric value and value segments.
    
    Args:
        metric_name: Name of the metric
        value: The calculated metric value
        
    Returns:
        Assessment string: "Fair", "Warning", or "Violation"
    """
    metric_def = get_metric_definition(metric_name)
    value_segments = metric_def.get('value_segments', [])
    
    if not value_segments:
        # Fallback to default thresholds if no segments defined
        return default_assessment(metric_name, value)
    
    # Special handling for disparate_impact (uses min value logic)
    if metric_name == "disparate_impact":
        for segment in value_segments:
            min_val = segment.get('min', float('-inf'))
            max_val = segment.get('max', float('inf'))
            
            if min_val != float('-inf') and value >= min_val:
                return segment['severity']
            elif max_val != float('inf') and value < max_val:
                return segment['severity']
    
    # For all other metrics (uses max value logic with absolute values)
    abs_value = abs(value)
    
    for segment in value_segments:
        max_val = segment.get('max', float('inf'))
        
        if abs_value <= max_val:
            return segment['severity']
    
    # If no segment matched, return Violation
    return "Violation"


def default_assessment(metric_name: str, value: float) -> str:
    """
    Fallback assessment logic when value segments are not defined.
    """
    if metric_name == "disparate_impact":
        return "Fair" if value >= 0.8 else "Violation"
    elif metric_name == "theil_index":
        abs_val = abs(value)
        return "Fair" if abs_val < 0.5 else "Warning" if abs_val < 1.0 else "Violation"
    else:
        abs_val = abs(value)
        return "Fair" if abs_val < 0.05 else "Warning" if abs_val < 0.15 else "Violation"


def get_value_segment_info(metric_name: str, value: float) -> dict:
    """
    Get the interpretation and severity for a given metric value.
    
    Args:
        metric_name: Name of the metric
        value: The calculated metric value
        
    Returns:
        Dictionary with interpretation and severity
    """
    metric_def = get_metric_definition(metric_name)
    value_segments = metric_def.get('value_segments', [])
    
    if not value_segments:
        return {
            'interpretation': 'No segment information available',
            'severity': default_assessment(metric_name, value)
        }
    
    # Special handling for disparate_impact
    if metric_name == "disparate_impact":
        for segment in value_segments:
            min_val = segment.get('min', float('-inf'))
            max_val = segment.get('max', float('inf'))
            
            if min_val != float('-inf') and value >= min_val:
                return {
                    'interpretation': segment['interpretation'],
                    'severity': segment['severity']
                }
            elif max_val != float('inf') and value < max_val:
                return {
                    'interpretation': segment['interpretation'],
                    'severity': segment['severity']
                }
    
    # For all other metrics
    abs_value = abs(value)
    
    for segment in value_segments:
        max_val = segment.get('max', float('inf'))
        
        if abs_value <= max_val:
            return {
                'interpretation': segment['interpretation'],
                'severity': segment['severity']
            }
    
    # Default if no segment matched
    return {
        'interpretation': 'Exceeds all thresholds',
        'severity': 'Violation'
    }
