# Integrated Label Handling

This document describes the integrated label handling approach implemented in the Metric Query Library. This enhancement allows for more flexible and powerful label-based transformations within the unified metric transformation pipeline.

## Overview

Previously, the Metric Query Library handled labeled metrics through a separate pre-processing step using the `LabeledMetricProcessor` class. This required converting labeled metrics to unlabeled metrics before they could be processed by the core Rust transformation engine, limiting the flexibility of label-based operations.

The new integrated approach allows label information to flow directly through the Rust pipeline, enabling more complex transformations that can make decisions based on labels within a single unified pipeline.

## Key Improvements

- **Unified Metric Model**: The `Metric` struct in Rust now includes an optional `label` field, eliminating the need for separate `LabeledMetric` handling.
- **Label-Aware Transformations**: The transformation pipeline now preserves label information throughout the process.
- **Direct Label Filtering**: Label filtering can now be done directly within the transformation pipeline rather than as a preprocessing step.
- **Preserve Labels in Results**: Output metrics maintain their label information, providing richer context in the results.

## Using Label-Based Filtering

The enhanced API provides two main methods for filtering by label:

### 1. Filter by Exact Label Match

```python
# Filter metrics with label "cpu_usage"
pipeline = MetricTransformationPipeline(metrics)
result = (
    pipeline
    .filter_by_label("cpu_usage")
    .aggregate("avg")
    .execute()
)
```

### 2. Filter by Multiple Labels

```python
# Filter metrics with labels in the set ["cpu_usage", "memory_usage"]
pipeline = MetricTransformationPipeline(metrics)
result = (
    pipeline
    .filter_by_labels(["cpu_usage", "memory_usage"])
    .group_by_hour("sum")
    .execute()
)
```

## How It Works

1. When metrics are added to the pipeline, label information is preserved within the `Metric` struct.
2. Label filters (`label_eq` and `label_in`) are implemented as regular filter plugins in the Rust core.
3. The `FilterTransformation` applies these label filters in the same way as value filters.
4. Aggregation and time grouping operations maintain label information where appropriate.

## Integration with Existing Code

This enhancement is fully backward compatible:
- Existing code using unlabeled metrics will continue to work without changes.
- The `LabeledMetricProcessor` is maintained for backward compatibility but is no longer necessary for most use cases.
- All existing transformations work with both labeled and unlabeled metrics.

## Performance Considerations

The integrated label handling approach offers several performance benefits:
- Eliminates the need to convert between `LabeledMetric` and `Metric` objects.
- Avoids creating multiple separate pipelines for different labels.
- Reduces memory usage by operating on a single pipeline instead of multiple pipelines.

## Example: Complex Label-Aware Pipeline

```python
# Create a pipeline that filters different labels with different thresholds
pipeline = MetricTransformationPipeline(metrics)

# For CPU metrics, filter values > 80
cpu_pipeline = pipeline.clone().filter_by_label("cpu_usage").greater_than(80)

# For memory metrics, filter values > 90
mem_pipeline = pipeline.clone().filter_by_label("memory_usage").greater_than(90)

# Combine the results and aggregate
combined_metrics = cpu_pipeline.execute() + mem_pipeline.execute()
final_pipeline = MetricTransformationPipeline(combined_metrics).average()
result = final_pipeline.execute()
```

With future enhancements, we could potentially support this pattern with a single pipeline:

```python
# Hypothetical future API for label-specific conditions
pipeline = MetricTransformationPipeline(metrics)
result = (
    pipeline
    .when_label("cpu_usage").greater_than(80)
    .when_label("memory_usage").greater_than(90)
    .average()
    .execute()
)