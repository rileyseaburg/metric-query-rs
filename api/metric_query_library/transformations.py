"""
Transformation utilities for Metric Query API

This module provides a fluent interface for working with metric transformations,
wrapping the underlying Rust library with a more Pythonic API.
"""

from typing import List, Dict, Any, Optional, Union, Callable
# Import directly from the parent package to avoid circular imports
from . import (
    Metric, LabeledMetric, Filter, Aggregation, TimeGrouping, Transformation,
    transform, _create_raw_pipeline, get_registry,
    MetricPipeline, TransformationRegistry
)
from .type_defs import (
    FilterSpec, TransformationSpec, MetricDict, LabeledMetricDict,
    FilterType, AggregationType, TimeGroupingType
)
from .validation import (
    validate_filter, validate_aggregation, validate_time_grouping
)

class MetricTransformationPipeline:
    """
    A fluent interface for building and executing metric transformations.
    
    This class wraps the underlying Rust library's MetricPipeline with a more
    Pythonic API, allowing chained method calls and easy execution.
    
    Example:
        pipeline = MetricTransformationPipeline(metrics)
        result = (
            pipeline
            .filter(type="gt", value=100)
            .group_by_hour()
            .aggregate("sum")
            .execute()
        )
    """
    
    def __init__(self, metrics: List[Union[Metric, Dict[str, Any]]]):
        """
        Initialize a new transformation pipeline with the given metrics.
        
        Args:
            metrics: List of Metric objects or dictionaries with value and timestamp
        """
        # Convert dictionaries to Metric objects if needed
        self._metrics = []
        for metric in metrics:
            if isinstance(metric, dict):
                self._metrics.append(Metric(
                    value=int(metric['value']),
                    timestamp=int(metric.get('timestamp', 0))
                ))
            else:
                self._metrics.append(metric)
        
        # Create the underlying pipeline
        self._pipeline = _create_raw_pipeline(self._metrics)
    
    def filter(self, type: FilterType, value: int) -> 'MetricTransformationPipeline':
        """
        Add a filter to the pipeline.
        
        Args:
            type: Filter type ('gt', 'lt', 'ge', 'le', 'eq')
            value: Value to compare against
            
        Returns:
            Self for method chaining
        """
        # Validate
        is_valid, error = validate_filter({'type': type, 'value': value})
        if not is_valid:
            raise ValueError(f"Invalid filter: {error}")
        
        # Create the filter based on type
        registry = get_registry()
        filter_type_map = {
            'gt': 'gt',
            'lt': 'lt',
            'ge': 'ge',
            'le': 'le',
            'eq': 'eq'
        }
        
        # Create old-style filter (compatibility layer will convert it)
        filter_obj = Filter(type, value)
        
        # Add to pipeline
        self._pipeline.filter(filter_obj)
        return self
    
    def greater_than(self, value: int) -> 'MetricTransformationPipeline':
        """Add a greater than filter"""
        return self.filter('gt', value)
    
    def less_than(self, value: int) -> 'MetricTransformationPipeline':
        """Add a less than filter"""
        return self.filter('lt', value)
    
    def greater_than_or_equal(self, value: int) -> 'MetricTransformationPipeline':
        """Add a greater than or equal filter"""
        return self.filter('ge', value)
    
    def less_than_or_equal(self, value: int) -> 'MetricTransformationPipeline':
        """Add a less than or equal filter"""
        return self.filter('le', value)
    
    def equal_to(self, value: int) -> 'MetricTransformationPipeline':
        """Add an equality filter"""
        return self.filter('eq', value)
        
    def aggregate(self, type: AggregationType) -> 'MetricTransformationPipeline':
        """
        Add an aggregation to the pipeline.
        
        Args:
            type: Aggregation type ('sum', 'avg', 'min', 'max')
            
        Returns:
            Self for method chaining
        """
        # Validate
        is_valid, error = validate_aggregation(type)
        if not is_valid:
            raise ValueError(f"Invalid aggregation: {error}")
        
        # Create the aggregation
        agg_obj = Aggregation(type)
        
        # Add to pipeline
        self._pipeline.aggregate(type=type)
        return self
    
    def sum(self) -> 'MetricTransformationPipeline':
        """Add a sum aggregation"""
        return self.aggregate('sum')
    
    def average(self) -> 'MetricTransformationPipeline':
        """Add an average aggregation"""
        return self.aggregate('avg')
    
    def minimum(self) -> 'MetricTransformationPipeline':
        """Add a minimum aggregation"""
        return self.aggregate('min')
    
    def maximum(self) -> 'MetricTransformationPipeline':
        """Add a maximum aggregation"""
        return self.aggregate('max')
    
    def group_by(self, time_grouping: TimeGroupingType, aggregation: AggregationType) -> 'MetricTransformationPipeline':
        """
        Group metrics by time and apply an aggregation.
        
        Args:
            time_grouping: Time grouping type ('hour', 'minute', 'day')
            aggregation: Aggregation type ('sum', 'avg', 'min', 'max')
            
        Returns:
            Self for method chaining
        """
        # Validate
        is_valid, error = validate_time_grouping(time_grouping)
        if not is_valid:
            raise ValueError(f"Invalid time grouping: {error}")
        
        is_valid, error = validate_aggregation(aggregation)
        if not is_valid:
            raise ValueError(f"Invalid aggregation: {error}")
        
        # Create the time grouping and aggregation
        time_grouping_obj = TimeGrouping(time_grouping)
        agg_obj = Aggregation(aggregation)
        
        # Add to pipeline
        self._pipeline.group_by_time(time_grouping_obj, agg_obj)
        return self
    
    def group_by_minute(self, aggregation: AggregationType = 'sum') -> 'MetricTransformationPipeline':
        """Group by minute with the given aggregation"""
        return self.group_by('minute', aggregation)
    
    def group_by_hour(self, aggregation: AggregationType = 'sum') -> 'MetricTransformationPipeline':
        """Group by hour with the given aggregation"""
        return self.group_by('hour', aggregation)
    
    def group_by_day(self, aggregation: AggregationType = 'sum') -> 'MetricTransformationPipeline':
        """Group by day with the given aggregation"""
        return self.group_by('day', aggregation)
    
    def execute(self) -> List[Metric]:
        """
        Execute the pipeline and return the transformed metrics.
        
        Returns:
            List of transformed Metric objects
        """
        return self._pipeline.execute()
    
    def execute_to_dicts(self) -> List[MetricDict]:
        """
        Execute the pipeline and return the results as dictionaries.
        
        Returns:
            List of dictionaries with value and timestamp
        """
        results = self.execute()
        return [{'value': metric.value, 'timestamp': metric.timestamp} for metric in results]


class LegacyTransformationBuilder:
    """
    Utility class for building legacy-style transformations.
    
    This class helps create the older style Transformation objects used
    by the original transform() function.
    """
    
    @staticmethod
    def build_from_dict(transform_data: TransformationSpec) -> Transformation:
        """
        Build a Transformation from a dictionary specification.
        
        Args:
            transform_data: Dictionary containing transformation data
            
        Returns:
            A Transformation object
        """
        transformation = Transformation()
        
        # Add filter if provided
        if 'filter' in transform_data:
            filter_data = transform_data['filter']
            if isinstance(filter_data, dict) and 'type' in filter_data and 'value' in filter_data:
                transformation.filter = Filter(filter_data['type'], int(filter_data['value']))
        
        # Add aggregation if provided
        if 'aggregation' in transform_data:
            transformation.aggregation = Aggregation(transform_data['aggregation'])
        
        # Add time grouping if provided
        if 'time_grouping' in transform_data:
            transformation.time_grouping = TimeGrouping(transform_data['time_grouping'])
        
        return transformation



def transform_metrics(
    metrics: List[Union[Metric, Dict[str, Any]]],
    transformations: List[TransformationSpec]
) -> List[Metric]:
    """
    Transform metrics using the legacy transform function.
    
    This is a convenience wrapper around the original transform() function
    that handles conversion between dictionaries and Metric objects.
    
    Args:
        metrics: List of Metric objects or dictionaries
        transformations: List of transformation specifications
        
    Returns:
        List of transformed Metric objects
    """
    # Convert dictionaries to Metric objects if needed
    metric_objs = []
    for metric in metrics:
        if isinstance(metric, dict):
            metric_objs.append(Metric(
                value=int(metric['value']),
                timestamp=int(metric.get('timestamp', 0))
            ))
        else:
            metric_objs.append(metric)
    
    # Convert transformation dictionaries to Transformation objects
    transformation_objs = []
    for transform_data in transformations:
        transformation_objs.append(LegacyTransformationBuilder.build_from_dict(transform_data))
    
    # Apply transformations
    return transform(metric_objs, transformation_objs)


def transform_metrics_to_dicts(
    metrics: List[Union[Metric, Dict[str, Any]]],
    transformations: List[TransformationSpec]
) -> List[MetricDict]:
    """
    Transform metrics and return results as dictionaries.
    
    Args:
        metrics: List of Metric objects or dictionaries
        transformations: List of transformation specifications
        
    Returns:
        List of dictionaries with value and timestamp
    """
    results = transform_metrics(metrics, transformations)
    return [{'value': metric.value, 'timestamp': metric.timestamp} for metric in results]


def create_pipeline(metrics: List[Union[Metric, Dict[str, Any]]]) -> MetricTransformationPipeline:
    """
    Create a new transformation pipeline with the given metrics.
    
    This is a convenience function for creating a MetricTransformationPipeline.
    
    Args:
        metrics: List of Metric objects or dictionaries
        
    Returns:
        A new MetricTransformationPipeline
    """
    return MetricTransformationPipeline(metrics)