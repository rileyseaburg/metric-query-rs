"""
Input validation utilities for Metric Query API

This module provides validation functions for API inputs to ensure they meet
the requirements before being passed to the Rust library.
"""

from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime
from .type_defs import (
    FilterSpec, TransformationSpec, MetricDict, LabeledMetricDict,
    FilterType, AggregationType, TimeGroupingType, LabelFilterType
)

# Valid filter types
VALID_FILTER_TYPES = {'gt', 'lt', 'ge', 'le', 'eq'}

# Valid aggregation types
VALID_AGGREGATION_TYPES = {'sum', 'avg', 'min', 'max'}

# Valid time grouping types
VALID_TIME_GROUPING_TYPES = {'hour', 'minute', 'day'}

# Valid label filter types
VALID_LABEL_FILTER_TYPES = {'label_eq', 'label_in'}

# Linux epoch timestamp
LINUX_EPOCH = datetime(1970, 1, 1).timestamp()

def validate_metric(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate metric data

    Args:
        data: Dictionary containing metric data

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not data:
        return False, "Empty metric data"
    
    if 'value' not in data:
        return False, "Missing required field: value"
    
    try:
        value = int(data['value'])
    except (ValueError, TypeError):
        return False, "Value must be an integer"
    
    # Validate timestamp if provided
    if 'timestamp' in data:
        try:
            timestamp = int(data['timestamp'])
        except (ValueError, TypeError):
            return False, "Timestamp must be an integer"
        
        # Check timestamp is after Linux epoch
        if timestamp < LINUX_EPOCH:
            return False, f"Timestamp must be after Linux epoch ({LINUX_EPOCH})"
        
        # Check timestamp is not in the future
        now = datetime.now().timestamp()
        if timestamp > now:
            return False, "Timestamp cannot be in the future"
    
    return True, None

def validate_labeled_metric(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate labeled metric data

    Args:
        data: Dictionary containing labeled metric data

    Returns:
        Tuple of (is_valid, error_message)
    """
    # First validate as a regular metric
    is_valid, error = validate_metric(data)
    if not is_valid:
        return False, error
    
    # Additionally validate label
    if 'label' not in data:
        return False, "Missing required field: label"
    
    if not isinstance(data['label'], str):
        return False, "Label must be a string"
    
    if not data['label'].strip():
        return False, "Label cannot be empty"
    
    return True, None

def validate_filter(filter_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate filter data

    Args:
        filter_data: Dictionary containing filter data

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not filter_data:
        return False, "Empty filter data"
    
    if 'type' not in filter_data:
        return False, "Missing required field: type"
    
    if 'value' not in filter_data:
        return False, "Missing required field: value"
    
    filter_type = filter_data['type']
    if filter_type not in VALID_FILTER_TYPES:
        return False, f"Invalid filter type. Expected one of: {', '.join(VALID_FILTER_TYPES)}"
    
    try:
        value = int(filter_data['value'])
    except (ValueError, TypeError):
        return False, "Filter value must be an integer"
    
    return True, None

def validate_aggregation(aggregation: str) -> Tuple[bool, Optional[str]]:
    """
    Validate aggregation type

    Args:
        aggregation: Aggregation type string

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not aggregation:
        return False, "Empty aggregation type"
    
    if aggregation not in VALID_AGGREGATION_TYPES:
        return False, f"Invalid aggregation type. Expected one of: {', '.join(VALID_AGGREGATION_TYPES)}"
    
    return True, None

def validate_time_grouping(time_grouping: str) -> Tuple[bool, Optional[str]]:
    """
    Validate time grouping type

    Args:
        time_grouping: Time grouping type string

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not time_grouping:
        return False, "Empty time grouping type"
    
    if time_grouping not in VALID_TIME_GROUPING_TYPES:
        return False, f"Invalid time grouping type. Expected one of: {', '.join(VALID_TIME_GROUPING_TYPES)}"
    
    return True, None

def validate_label_filter(label_filter_type: str, label_value: Union[str, List[str]]) -> Tuple[bool, Optional[str]]:
    """
    Validate label filter type and value
    
    Args:
        label_filter_type: Label filter type string
        label_value: Label value (string or list of strings)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not label_filter_type:
        return False, "Empty label filter type"
    
    if label_filter_type not in VALID_LABEL_FILTER_TYPES:
        return False, f"Invalid label filter type. Expected one of: {', '.join(VALID_LABEL_FILTER_TYPES)}"
    
    # For label_eq, value must be a string
    if label_filter_type == 'label_eq':
        if not isinstance(label_value, str):
            return False, "Label value must be a string for label_eq filter"
        if not label_value.strip():
            return False, "Label value cannot be empty"
    
    # For label_in, value must be a list of strings
    elif label_filter_type == 'label_in':
        if not isinstance(label_value, list):
            return False, "Label value must be a list of strings for label_in filter"
        if not label_value:
            return False, "Label value list cannot be empty"
        for label in label_value:
            if not isinstance(label, str) or not label.strip():
                return False, "All labels in the list must be non-empty strings"
    
    return True, None

def validate_transformation(transform_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate transformation data

    Args:
        transform_data: Dictionary containing transformation data

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not transform_data:
        return False, "Empty transformation data"
    
    # At least one transformation operation must be specified
    if not any(key in transform_data for key in ['filter', 'aggregation', 'time_grouping', 'label_filter']):
        return False, "Transformation must include at least one operation (filter, aggregation, time_grouping, or label_filter)"
    
    # Validate filter if provided
    if 'filter' in transform_data:
        filter_data = transform_data['filter']
        is_valid, error = validate_filter(filter_data)
        if not is_valid:
            return False, f"Invalid filter: {error}"
    
    # Validate aggregation if provided
    if 'aggregation' in transform_data:
        is_valid, error = validate_aggregation(transform_data['aggregation'])
        if not is_valid:
            return False, f"Invalid aggregation: {error}"
    
    # Validate time grouping if provided
    if 'time_grouping' in transform_data:
        is_valid, error = validate_time_grouping(transform_data['time_grouping'])
        if not is_valid:
            return False, f"Invalid time grouping: {error}"
    
    # Validate label filter if provided
    if 'label_filter' in transform_data:
        label_filter = transform_data['label_filter']
        
        # Single label string (label_eq filter)
        if isinstance(label_filter, str):
            is_valid, error = validate_label_filter('label_eq', label_filter)
            if not is_valid:
                return False, f"Invalid label filter: {error}"
        # List of labels (label_in filter)
        elif isinstance(label_filter, list):
            is_valid, error = validate_label_filter('label_in', label_filter)
            if not is_valid:
                return False, f"Invalid label filter: {error}"
        else:
            return False, "Label filter must be a string or list of strings"
    
    # Check if time grouping is provided without aggregation
    if 'time_grouping' in transform_data and 'aggregation' not in transform_data:
        return False, "Time grouping requires an aggregation to be specified"
    
    return True, None

def validate_transformations(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate transformations request data

    Args:
        data: Dictionary containing transformations request data

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not data:
        return False, "Empty request data"
    
    if 'transformations' not in data:
        return False, "Missing required field: transformations"
    
    transformations = data['transformations']
    if not isinstance(transformations, list):
        return False, "Transformations must be an array"
    
    if not transformations:
        return False, "Transformations array cannot be empty"
    
    # Validate each transformation
    for i, transform_data in enumerate(transformations):
        is_valid, error = validate_transformation(transform_data)
        if not is_valid:
            return False, f"Invalid transformation at index {i}: {error}"
    
    return True, None