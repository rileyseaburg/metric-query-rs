# Labeled Metrics Pipeline API

This document provides detailed documentation for the labeled metrics pipeline API, which is the recommended modern approach for working with labeled metrics.

## Overview

The labeled metrics pipeline API provides a fluent interface for transforming time-series metrics that have categorical labels. It's designed for data engineers who need to analyze metrics across different categories using a clean and intuitive syntax.

## Endpoint

```
POST /labeled-metrics/pipeline
```

## Request Format

```json
{
  "label_operations": [
    {
      "operation": "filter_by_label",
      "label": "CPU_USAGE"
    }
  ],
  "pipeline": [
    {
      "operation": "greater_than",
      "value": 50
    },
    {
      "operation": "group_by_hour",
      "aggregation": "avg"
    }
  ]
}
```

The request consists of two main sections:

1. **label_operations**: Operations applied to filter metrics by their label before transformation
2. **pipeline**: Operations applied to the filtered metrics, similar to the regular pipeline API

## Label Operations

| Operation | Parameters | Description |
|-----------|------------|-------------|
| `filter_by_label` | `label` (string) | Keep only metrics with the specified label |
| `filter_by_labels` | `labels` (array of strings) | Keep metrics with any of these labels |

## Pipeline Operations

### Filter Operations

| Operation | Parameters | Description |
|-----------|------------|-------------|
| `filter` | `type` (string), `value` (integer) | Generic filter operation |
| `greater_than` | `value` (integer) | Value > threshold |
| `less_than` | `value` (integer) | Value < threshold |
| `equal_to` | `value` (integer) | Value = threshold |

### Aggregation Operations

| Operation | Parameters | Description |
|-----------|------------|-------------|
| `aggregate` | `type` (string) | Generic aggregation |
| `sum` | none | Sum all values |
| `average` | none | Average of values |

### Time Grouping Operations

| Operation | Parameters | Description |
|-----------|------------|-------------|
| `group_by` | `time_grouping` (string), `aggregation` (string) | Generic time grouping |
| `group_by_minute` | `aggregation` (string, default: "sum") | Group by minute |
| `group_by_hour` | `aggregation` (string, default: "sum") | Group by hour |
| `group_by_day` | `aggregation` (string, default: "sum") | Group by day |

## Response Format

```json
[
  {
    "value": 75,
    "timestamp": 1678899600
  },
  {
    "value": 82,
    "timestamp": 1678903200
  }
]
```

The response contains the transformed metrics with value and timestamp. 
Note that the label information is lost after processing, as pipeline operations convert labeled metrics to regular metrics.

## Example Use Cases

### 1. Calculate Hourly Average CPU Usage

```json
{
  "label_operations": [
    {
      "operation": "filter_by_label",
      "label": "CPU_USAGE"
    }
  ],
  "pipeline": [
    {
      "operation": "group_by_hour",
      "aggregation": "avg"
    }
  ]
}
```

This example:
1. Filters metrics to keep only those labeled as "CPU_USAGE"
2. Groups the remaining metrics by hour
3. Calculates the average value for each hour

### 2. Find Memory Usage Spikes

```json
{
  "label_operations": [
    {
      "operation": "filter_by_label",
      "label": "MEMORY_USAGE"
    }
  ],
  "pipeline": [
    {
      "operation": "group_by_hour",
      "aggregation": "max"
    }
  ]
}
```

This example:
1. Filters metrics to keep only those labeled as "MEMORY_USAGE"
2. Groups the remaining metrics by hour
3. Finds the maximum value for each hour, identifying peak usage

### 3. Compare High CPU and Memory Usage

```json
{
  "label_operations": [
    {
      "operation": "filter_by_labels",
      "labels": ["CPU_USAGE", "MEMORY_USAGE"]
    }
  ],
  "pipeline": [
    {
      "operation": "greater_than", 
      "value": 80
    },
    {
      "operation": "group_by_day",
      "aggregation": "count"
    }
  ]
}
```

This example:
1. Filters metrics to keep those labeled either "CPU_USAGE" or "MEMORY_USAGE"
2. Keeps only metrics with values greater than 80 (percentage)
3. Groups by day and counts how many high usage events occur each day

### 4. Daily CPU Usage Pattern with Multi-Step Filtering

```json
{
  "label_operations": [
    {
      "operation": "filter_by_label",
      "label": "CPU_USAGE"
    }
  ],
  "pipeline": [
    {
      "operation": "greater_than", 
      "value": 20
    },
    {
      "operation": "less_than",
      "value": 90
    },
    {
      "operation": "group_by_hour",
      "aggregation": "avg"
    }
  ]
}
```

This example:
1. Filters metrics to keep only those labeled as "CPU_USAGE"
2. Keeps only metrics with values between 20 and 90
3. Groups by hour and calculates the average value for each hour

## Best Practices

### 1. Filter by Label First

Always filter by label first before applying other transformations. This reduces the dataset size early in the pipeline, improving performance.

```json
// GOOD
{
  "label_operations": [{"operation": "filter_by_label", "label": "CPU_USAGE"}],
  "pipeline": [{"operation": "group_by_hour", "aggregation": "avg"}]
}
```

### 2. Order Matters

Pipeline operations are applied sequentially in the order provided. Different orders can produce different results.

```json
// Finds hourly averages AFTER filtering out values < 50
{
  "pipeline": [
    {"operation": "greater_than", "value": 50},
    {"operation": "group_by_hour", "aggregation": "avg"}
  ]
}

// Finds hourly averages FIRST, then filters those averages
{
  "pipeline": [
    {"operation": "group_by_hour", "aggregation": "avg"},
    {"operation": "greater_than", "value": 50}
  ]
}
```

### 3. Consistent Labels

Ensure your label names are consistent. "CPU_USAGE" and "cpu_usage" will be treated as different labels.

### 4. Choose Appropriate Time Units

Select time units appropriate for your data volume and analysis needs:
- `minute`: High granularity, but produces many data points
- `hour`: Good balance for daily analysis
- `day`: Best for longer-term trends

### 5. Multiple Aggregations

You cannot chain multiple aggregations together. Only the last aggregation will be effective.

```json
// INCORRECT USAGE - only the average will be calculated
{
  "pipeline": [
    {"operation": "sum"},
    {"operation": "average"}
  ]
}
```

## Implementation Details

Behind the scenes, the API uses the following process:

1. Create a labeled processor from the input metrics
2. Apply label operations to filter the metrics
3. Convert labeled metrics to regular metrics (dropping label information)
4. Create a pipeline from these metrics
5. Apply each pipeline operation in sequence
6. Execute the pipeline and return the results as dictionaries

This process ensures that label filtering happens first, then regular pipeline operations are applied to the filtered metrics.