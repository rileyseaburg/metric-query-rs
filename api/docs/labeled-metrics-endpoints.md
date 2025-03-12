# Labeled Metrics Endpoints Documentation

This document provides details on the labeled metrics endpoints available in the Metric Query API. Labeled metrics extend basic metrics with a categorical label, enabling more powerful filtering and grouping capabilities.

## Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/labeled-metrics` | Retrieve all stored labeled metrics |
| POST | `/labeled-metrics` | Add a new labeled metric |
| POST | `/labeled-metrics/transform` | Transform labeled metrics with additional support for label filtering |
| POST | `/labeled-metrics/pipeline` | Transform labeled metrics using the fluent pipeline API |

---

## GET /labeled-metrics

Retrieve all labeled metrics stored in the system.

### Response

Returns an array of labeled metric objects:

```json
[
  {
    "label": "CPU_USAGE",
    "value": 75,
    "timestamp": 1678901234
  },
  {
    "label": "MEMORY_USAGE",
    "value": 512,
    "timestamp": 1678901235
  }
]
```

---

## POST /labeled-metrics

Add a new labeled metric to the stream.

### Request Body

```json
{
  "label": "CPU_USAGE",
  "value": 75,
  "timestamp": 1678901234
}
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| label | string | Yes | Category label from a known set of values (e.g., CPU_USAGE, MEMORY_USAGE) |
| value | integer | Yes | The metric value (any positive or negative integer) |
| timestamp | integer | No | Unix timestamp in seconds. If not provided, current time is used |

### Response

```json
{
  "status": "success",
  "id": 0
}
```

---

## POST /labeled-metrics/transform

Transform labeled metrics with additional support for label filtering. This endpoint extends regular metric transformations with the ability to filter by label.

### Constraints

- Labels are considered to be from a known set of values (enum-like)
- Filters can be applied to labels IN ADDITION TO values and timestamps
- Like basic metrics, aggregations can ONLY be applied to values
- Like basic metrics, time groupings can ONLY be applied to timestamps
- Transformations are applied sequentially in the order provided
- The label_filter parameter is unique to labeled metrics

### Request Body

```json
{
  "transformations": [
    {
      "label_filter": "CPU_USAGE"
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

| Transformation | Description |
|----------------|-------------|
| label_filter | String to filter metrics by label (only applies to labeled metrics) |
| filter | Filter condition with type (gt, lt, ge, le, eq) and value |
| aggregation | Aggregation function (sum, avg, min, max) |
| time_grouping | Time unit to group metrics by (minute, hour, day) |

### Response

```json
[
  {
    "value": 350,
    "timestamp": 1678901200
  },
  {
    "value": 425,
    "timestamp": 1678904800
  }
]
```

### Example Use Cases

1. Calculate hourly average CPU usage:
```json
{
  "transformations": [
    {
      "label_filter": "CPU_USAGE"
    },
    {
      "aggregation": "avg",
      "time_grouping": "hour"
    }
  ]
}
```

2. Find peak memory usage per day:
```json
{
  "transformations": [
    {
      "label_filter": "MEMORY_USAGE"
    },
    {
      "aggregation": "max",
      "time_grouping": "day"
    }
  ]
}
```

3. Filter high CPU usage events and group by hour:
```json
{
  "transformations": [
    {
      "label_filter": "CPU_USAGE"
    },
    {
      "filter": {
        "type": "gt",
        "value": 80
      }
    },
    {
      "aggregation": "avg",
      "time_grouping": "hour"
    }
  ]
}
```

---

## POST /labeled-metrics/pipeline

Transform labeled metrics using the fluent pipeline API. This endpoint provides a more intuitive interface for building transformation pipelines with labeled metrics.

### Request Body

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

#### Label Operations

| Operation | Parameters | Description |
|-----------|------------|-------------|
| filter_by_label | label (string) | Keep metrics with a specific label |
| filter_by_labels | labels (array of strings) | Keep metrics with any of these labels |

#### Pipeline Operations

| Operation | Parameters | Description |
|-----------|------------|-------------|
| filter | type (string), value (integer) | Generic filter operation |
| greater_than | value (integer) | Filter metrics where value > threshold |
| less_than | value (integer) | Filter metrics where value < threshold |
| equal_to | value (integer) | Filter metrics where value = threshold |
| aggregate | type (string) | Generic aggregation operation |
| sum | (none) | Sum all values |
| average | (none) | Average of values |
| group_by | time_grouping (string), aggregation (string) | Generic time grouping operation |
| group_by_minute | aggregation (string, default: sum) | Group by minute |
| group_by_hour | aggregation (string, default: sum) | Group by hour |
| group_by_day | aggregation (string, default: sum) | Group by day |

### Response

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

### Example Use Cases

1. Calculate hourly average CPU usage:
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

2. Find memory usage spikes:
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

3. Analyzing high CPU and memory usage events:
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

---

## Working with Labels - Best Practices

1. **Filter First**: Always filter by label first to reduce the dataset size before applying transformations
2. **Consistent Labels**: Ensure your label names are consistent (e.g., "CPU_USAGE" vs "cpu_usage")
3. **Related Labels**: When using multiple labels, make sure they're logically related for meaningful analysis
4. **Order Matters**: In both transform and pipeline endpoints, operations are applied sequentially in the order provided
5. **Multiple Aggregations**: You can't chain multiple aggregations together (e.g., sum, then avg)
6. **Time Unit Selection**: Choose appropriate time units - minute grouping on months of data will return many data points