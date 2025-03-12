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

import sys
import logging

# Configure logging
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
# foo 
# Try to use maturin_import_hook if available
try:
    import maturin_import_hook
    logger.info("Using maturin_import_hook for automatic rebuilding")
    maturin_import_hook.install()
except ImportError:
    logger.info("maturin_import_hook not found. Consider installing it for development.")

# Define placeholder classes for when the Rust module isn't available
class Metric:
    def __init__(self, value=0, timestamp=0, label=None):
        self.value = value
        self.timestamp = timestamp
        self.label = label

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
        self.operations = []
        
    def filter(self, filter_obj=None, **kwargs):
        """Store filter operation for later execution"""
        if filter_obj:
            self.operations.append(('filter', filter_obj))
        else:
            self.operations.append(('filter', kwargs))
        return self
        
    def aggregate(self, type=""):
        """Store aggregation operation for later execution"""
        self.operations.append(('aggregate', type))
        return self
        
    def group_by_time(self, time_grouping, aggregation):
        """Store group_by operation for later execution"""
        self.operations.append(('group_by', (time_grouping, aggregation)))
        return self
        
    def filter_by_label(self, filter_type="", label=""):
        """Store label filter operation for later execution"""
        self.operations.append(('filter_by_label', (filter_type, label)))
        return self
        
    def filter_by_labels(self, filter_type="", labels=None):
        """Store labels filter operation for later execution"""
        self.operations.append(('filter_by_labels', (filter_type, labels or [])))
        return self
        
    def execute(self):
        """
        Execute the pipeline operations in sequence.
        This is a simplified implementation for when Rust bindings are not available.
        """
        import logging
        logging.warning("Using Python fallback implementation for MetricPipeline.execute()")
        return self.metrics

class TransformationRegistry:
    def __init__(self):
        pass
    
    def refresh(self, py=None):
        pass

def transform(metrics, transformations):
    """
    Transform metrics using the specified transformations.
    This is a simplified implementation for when Rust bindings are not available.
    """
    import logging
    logging.warning("Using Python fallback implementation for transform()")
    return metrics

def _create_raw_pipeline(metrics):
    """Create a new pipeline with the given metrics"""
    import logging
    logging.warning("Using Python fallback implementation for _create_raw_pipeline()")
    return MetricPipeline(metrics)

def get_registry():
    return TransformationRegistry()

# Try to import the Rust bindings and replace the placeholder classes
try:
    # Import the Rust module
    import importlib.util
    spec = importlib.util.find_spec("metric_query_library")
    if spec and spec.origin and "site-packages" in spec.origin:
        logger.info(f"Found metric_query_library at {spec.origin}")
        # This is the installed package, not our module
        # Import the Rust bindings
        import metric_query_library._metric_query_library as rust_lib
        logger.info("Successfully imported Rust bindings")
        
        # Replace the placeholder classes with the real ones
        Metric = rust_lib.Metric
        LabeledMetric = rust_lib.LabeledMetric
        Filter = rust_lib.Filter
        Aggregation = rust_lib.Aggregation
        TimeGrouping = rust_lib.TimeGrouping
        Transformation = rust_lib.Transformation
        MetricPipeline = rust_lib.MetricPipeline
        TransformationRegistry = rust_lib.TransformationRegistry
        transform = rust_lib.transform
        _create_raw_pipeline = rust_lib.create_pipeline
        get_registry = rust_lib.get_registry
except ImportError as e:
    logger.error(f"Error importing Rust bindings: {e}")
    # Continue with the placeholder classes

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