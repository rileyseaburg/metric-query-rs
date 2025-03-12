"""
Label operations for Metric Query API

This module provides utilities for working with labeled metrics,
including filtering and grouping operations.
"""

from typing import List, Dict, Any, Optional, Union, Callable
import metric_query_library as mq
from .type_defs import (
    FilterSpec, TransformationSpec, MetricDict, LabeledMetricDict,
)
from .transformations import MetricTransformationPipeline

class LabeledMetricProcessor:
    """
    Processor for operations on labeled metrics.
    
    This class provides utilities for filtering and preprocessing
    labeled metrics before sending them to the transformation pipeline.
    """
    
    def __init__(self, metrics: List[Union[mq.LabeledMetric, Dict[str, Any]]]):
        """
        Initialize with a list of labeled metrics.
        
        Args:
            metrics: List of LabeledMetric objects or dictionaries
        """
        # Convert dictionaries to LabeledMetric objects if needed
        self._metrics = []
        for metric in metrics:
            if isinstance(metric, dict):
                self._metrics.append(mq.LabeledMetric(
                    label=str(metric['label']),
                    value=int(metric['value']),
                    timestamp=int(metric.get('timestamp', 0))
                ))
            else:
                self._metrics.append(metric)
    
    def filter_by_label(self, label: str) -> 'LabeledMetricProcessor':
        """
        Filter metrics by exact label match.
        
        Args:
            label: Label to match
            
        Returns:
            Self for method chaining
        """
        self._metrics = [m for m in self._metrics if m.label == label]
        return self
    
    def filter_by_labels(self, labels: List[str]) -> 'LabeledMetricProcessor':
        """
        Filter metrics by multiple labels.
        
        Args:
            labels: List of labels to match
            
        Returns:
            Self for method chaining
        """
        label_set = set(labels)
        self._metrics = [m for m in self._metrics if m.label in label_set]
        return self
    
    def to_unlabeled(self) -> List[mq.Metric]:
        """
        Convert labeled metrics to regular metrics for processing.
        
        Returns:
            List of regular Metric objects
        """
        return [mq.Metric(value=m.value, timestamp=m.timestamp) for m in self._metrics]
    
    def to_pipeline(self) -> MetricTransformationPipeline:
        """
        Create a transformation pipeline from these metrics.
        
        This converts labeled metrics to regular metrics and creates a pipeline.
        
        Returns:
            A new MetricTransformationPipeline
        """
        return MetricTransformationPipeline(self.to_unlabeled())
    
    def get_metrics(self) -> List[mq.LabeledMetric]:
        """
        Get the current set of labeled metrics.
        
        Returns:
            List of LabeledMetric objects
        """
        return self._metrics
    
    def to_dicts(self) -> List[LabeledMetricDict]:
        """
        Convert labeled metrics to dictionaries.
        
        Returns:
            List of dictionaries with label, value, and timestamp
        """
        return [
            {'label': m.label, 'value': m.value, 'timestamp': m.timestamp}
            for m in self._metrics
        ]
    
    @staticmethod
    def group_by_label(
        metrics: List[Union[mq.LabeledMetric, Dict[str, Any]]]
    ) -> Dict[str, List[mq.Metric]]:
        """
        Group labeled metrics by their labels.
        
        Args:
            metrics: List of LabeledMetric objects or dictionaries
            
        Returns:
            Dictionary mapping labels to lists of regular Metric objects
        """
        # Convert dictionaries to LabeledMetric objects if needed
        labeled_metrics = []
        for metric in metrics:
            if isinstance(metric, dict):
                labeled_metrics.append(mq.LabeledMetric(
                    label=str(metric['label']),
                    value=int(metric['value']),
                    timestamp=int(metric.get('timestamp', 0))
                ))
            else:
                labeled_metrics.append(metric)
        
        # Group by label
        result = {}
        for metric in labeled_metrics:
            if metric.label not in result:
                result[metric.label] = []
            result[metric.label].append(mq.Metric(value=metric.value, timestamp=metric.timestamp))
        
        return result
    
    @staticmethod
    def transform_by_label(
        metrics: List[Union[mq.LabeledMetric, Dict[str, Any]]],
        transformations: List[TransformationSpec]
    ) -> Dict[str, List[mq.Metric]]:
        """
        Apply transformations to labeled metrics, grouped by label.
        
        This groups metrics by label, then applies the transformations
        to each group separately.
        
        Args:
            metrics: List of LabeledMetric objects or dictionaries
            transformations: List of transformation specifications
            
        Returns:
            Dictionary mapping labels to lists of transformed Metric objects
        """
        from .transformations import transform_metrics
        
        # Group by label
        grouped = LabeledMetricProcessor.group_by_label(metrics)
        
        # Apply transformations to each group
        result = {}
        for label, group_metrics in grouped.items():
            result[label] = transform_metrics(group_metrics, transformations)
        
        return result

def create_labeled_processor(
    metrics: List[Union[mq.LabeledMetric, Dict[str, Any]]]
) -> LabeledMetricProcessor:
    """
    Create a new labeled metric processor.
    
    Args:
        metrics: List of LabeledMetric objects or dictionaries
        
    Returns:
        A new LabeledMetricProcessor
    """
    return LabeledMetricProcessor(metrics)