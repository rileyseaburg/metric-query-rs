"""
Metric Query Library

A Python package for transforming time series metric data with a fluent API.
This library wraps the Rust implementation for high performance while providing
a Pythonic interface.

Basic usage:
    ```python
    from metric_query_library import create_pipeline
    
    # Create a pipeline with metrics
    pipeline = create_pipeline(metrics)
    
    # Apply transformations and execute
    result = (
        pipeline
        .filter(type="gt", value=100)
        .group_by_hour()
        .sum()
        .execute_to_dicts()
    )
    ```

For labeled metrics:
    ```python
    from metric_query_library import create_labeled_processor
    
    # Create a processor for labeled metrics
    processor = create_labeled_processor(labeled_metrics)
    
    # Filter by label and transform
    result = (
        processor
        .filter_by_label("cpu_usage")
        .to_pipeline()
        .filter(type="gt", value=50)
        .group_by_day()
        .average()
        .execute_to_dicts()
    )
    ```
"""

# Import bindings from the Rust library
try:
    # Direct import from the compiled Rust module
    from metric_query_library import (
        Metric, LabeledMetric, Filter, Aggregation, TimeGrouping, Transformation,
        transform, create_pipeline as _create_raw_pipeline, get_registry,
        MetricPipeline, TransformationRegistry
    )
except ImportError as e:
    import sys
    print(f"Error importing from metric_query_library: {e}", file=sys.stderr)
    
    # Define placeholder classes for when the Rust module isn't available
    class Metric:
        def __init__(self, value=0, timestamp=0):
            self.value = value
            self.timestamp = timestamp
    
    class LabeledMetric:
        def __init__(self, label="", value=0, timestamp=0):
            self.label = label
            self.value = value
            self.timestamp = timestamp
    
    class Filter:
        def __init__(self, filter_type="", value=0):
            self.filter_type = filter_type
            self.value = value
    
    class Aggregation:
        def __init__(self, agg_type=""):
            self.agg_type = agg_type
    
    class TimeGrouping:
        def __init__(self, time_group_type=""):
            self.time_group_type = time_group_type
    
    class Transformation:
        def __init__(self):
            self.filter = None
            self.aggregation = None
            self.time_grouping = None
    
    class MetricPipeline:
        def __init__(self, metrics=None):
            self.metrics = metrics or []
            
        def filter(self, type="", value=0):
            return self
            
        def aggregate(self, type=""):
            return self
            
        def group_by_time(self, time_grouping="", aggregation=""):
            return self
            
        def execute(self):
            return self.metrics
    
    class TransformationRegistry:
        def __init__(self):
            pass
    
    def transform(metrics, transformations):
        return metrics
    
    def _create_raw_pipeline(metrics):
        return MetricPipeline(metrics)
    
    def get_registry():
        return TransformationRegistry()

# Import our Pythonic interfaces
from .type_defs import (
    FilterSpec, TransformationSpec, MetricDict, LabeledMetricDict,
    FilterType, AggregationType, TimeGroupingType, ApiErrorResponse, ApiSuccessResponse
)
from .validation import (
    validate_metric, validate_labeled_metric, validate_filter,
    validate_aggregation, validate_time_grouping, validate_transformation,
    validate_transformations
)
from .transformations import (
    MetricTransformationPipeline, LegacyTransformationBuilder,
    transform_metrics, transform_metrics_to_dicts, create_pipeline
)
from .label_ops import (
    LabeledMetricProcessor, create_labeled_processor
)

# Define version
__version__ = "1.0.0"

# For convenience, export commonly used functions and classes at the top level
__all__ = [
    # Core data types from Rust
    'Metric', 'LabeledMetric',
    
    # Type definitions
    'MetricDict', 'LabeledMetricDict', 'TransformationSpec',
    'FilterType', 'AggregationType', 'TimeGroupingType',
    
    # Validation functions
    'validate_metric', 'validate_labeled_metric', 'validate_transformation',
    
    # Main transformation interfaces
    'create_pipeline', 'transform_metrics', 'transform_metrics_to_dicts',
    'MetricTransformationPipeline',
    
    # Label operations
    'create_labeled_processor', 'LabeledMetricProcessor',
    
    # Version
    '__version__'
]
