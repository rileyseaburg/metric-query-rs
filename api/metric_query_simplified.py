"""
Simplified wrapper for metric_query_library that avoids circular imports.
This module will use the maturin-built package that we've already installed.
"""
import metric_query_library as mq

# Export the most commonly used functions and classes for convenience
Metric = mq.Metric
LabeledMetric = mq.LabeledMetric
create_pipeline = mq.create_pipeline
transform_metrics = mq.transform_metrics
transform_metrics_to_dicts = mq.transform_metrics_to_dicts
validate_metric = mq.validate_metric
validate_labeled_metric = mq.validate_labeled_metric
validate_transformations = mq.validate_transformations