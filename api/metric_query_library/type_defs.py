"""
Type definitions for the Metric Query Library

This module provides TypedDict classes and Literal types for the Metric Query API,
ensuring proper type checking and validation.
"""

from typing import TypedDict, Literal, Optional, List, Dict, Any, Union

# Filter type literals
FilterType = Literal['gt', 'lt', 'ge', 'le', 'eq']

# Aggregation type literals
AggregationType = Literal['sum', 'avg', 'min', 'max']

# Time grouping type literals
TimeGroupingType = Literal['hour', 'minute', 'day']

class FilterSpec(TypedDict):
    """Filter specification for metric queries"""
    type: FilterType
    value: int

class TransformationSpec(TypedDict, total=False):
    """Transformation specification for metric queries
    
    All fields are optional, but at least one should be provided.
    """
    filter: Optional[FilterSpec]
    aggregation: Optional[AggregationType]
    time_grouping: Optional[TimeGroupingType]
    label_filter: Optional[str]

class MetricDict(TypedDict):
    """Dictionary representation of a Metric"""
    value: int
    timestamp: int

class LabeledMetricDict(TypedDict):
    """Dictionary representation of a LabeledMetric"""
    label: str
    value: int
    timestamp: int

class ApiErrorResponse(TypedDict):
    """Error response format for API endpoints"""
    error: str
    details: Optional[Dict[str, Any]]

class ApiSuccessResponse(TypedDict, total=False):
    """Success response format for API endpoints"""
    status: str
    id: Optional[int]
    data: Optional[Union[List[MetricDict], List[LabeledMetricDict]]]
    message: Optional[str]