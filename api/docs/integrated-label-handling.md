# Integrated Label Handling

This document describes the integrated label handling feature in the Metric Query library, which allows for more efficient and intuitive filtering and transformation of labeled metrics.

## Overview

The Metric Query library now supports direct handling of labeled metrics through the core `MetricPipeline` interface. This means you can filter metrics by their labels and then apply additional transformations in a seamless, unified API.

### Key Benefits

- **Simplified API**: No separate processor needed for label operations
- **Consistent interface**: Use the same pipeline API for both labeled and unlabeled metrics
- **Improved performance**: Reduced overhead by eliminating conversion steps
- **Better type safety**: More explicit parameter types for label operations

## API Reference

### Label Filter Operations

The following operations are available for filtering metrics by label:

#### 1. `filter_by_label(filter_type, label)`

Filter metrics to only include those with an exact label match.

- **Parameters**:
  - `filter_type`: The string `"label_eq"` (literal equality)
  - `label`: String value to match against metric labels

- **Example**:
  ```python
  pipeline.filter_by_label('label_eq', 'cpu_usage')
  ```

#### 2. `filter_by_labels(filter_type, labels)`

Filter metrics to include those with labels matching any in the provided set.

- **Parameters**:
  - `filter_type`: The string `"label_in"` (set membership)
  - `labels`: List of string values to match against metric labels

- **Example**:
  ```python
  pipeline.filter_by_labels('label_in', ['cpu_usage', 'memory_usage'])
  ```

## Usage Patterns

### Basic Label Filtering

```python
from metric_query_library import create_pipeline

# Create a pipeline with labeled metrics
pipeline = create_pipeline(labeled_metrics)

# Filter to only CPU usage metrics
result = pipeline.filter_by_label('label_eq', 'cpu_usage').execute()
```

### Combining Label and Value Filters

```python
# Filter to CPU metrics with values over 80%
result = (
    pipeline
    .filter_by_label('label_eq', 'cpu_usage')
    .greater_than(80)
    .execute()
)
```

### Filtering by Multiple Labels

```python
# Get both CPU and memory metrics
result = (
    pipeline
    .filter_by_labels('label_in', ['cpu_usage', 'memory_usage'])
    .execute()
)
```

### Complete Analysis Example

```python
# Find average hourly CPU usage over 50%
result = (
    pipeline
    .filter_by_label('label_eq', 'cpu_usage')
    .greater_than(50)
    .group_by_hour('avg')
    .execute_to_dicts()
)
```

## REST API Changes

The labeled metrics API endpoints have been updated to use the integrated label handling:

### POST /labeled-metrics/transform

This endpoint now accepts a unified transformation structure that includes label filter operations directly:

```json
{
  "transformations": [
    {
      "label_filter": "cpu_usage"
    },
    {
      "filter": {
        "type": "gt", 
        "value": 50
      }
    },
    {
      "aggregation": "avg",
      "time_grouping": "hour"
    }
  ]
}
```

For filtering by multiple labels:

```json
{
  "transformations": [
    {
      "label_filter": ["cpu_usage", "memory_usage"]
    },
    ...
  ]
}
```

### POST /labeled-metrics/pipeline

This endpoint now accepts operations for label filtering directly in the pipeline:

```json
{
  "pipeline": [
    {"operation": "filter_by_label", "label": "cpu_usage"},
    {"operation": "greater_than", "value": 50},
    {"operation": "group_by_hour", "aggregation": "avg"}
  ]
}
```

For filtering by multiple labels:

```json
{
  "pipeline": [
    {"operation": "filter_by_labels", "labels": ["cpu_usage", "memory_usage"]},
    ...
  ]
}
```

## Implementation Details

The integrated label handling is implemented by:

1. Adding label filter capabilities directly to the `MetricPipeline` class
2. Modifying the Rust pipeline to handle label filtering natively
3. Supporting type-safe parameters through the `label_eq` and `label_in` type strings
4. Optimizing the filtering process to handle labels efficiently

This removes the need for the separate processor step previously required for label operations.