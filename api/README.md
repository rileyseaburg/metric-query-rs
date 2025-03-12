# Metric Query API

A Flask API that interfaces with the metric-query-rs Rust library to provide a RESTful interface for metric transformations.

## Overview

This API allows teams to interact with a streaming data system without needing to understand its internals. It provides endpoints for:

- Adding metrics (value, timestamp)
- Adding labeled metrics (label, value, timestamp)
- Retrieving metrics
- Applying transformations to metrics (filters, aggregations, time groupings)

## Installation

1. Make sure you have the metric-query-rs library installed and available to Python.
2. Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

## Running the API

```bash
python app.py
```

The API will be available at http://localhost:5000

## API Endpoints

### Metrics

#### POST /metrics

Add a new metric to the stream.

**Request Body:**
```json
{
  "value": 123,
  "timestamp": 1646006400  // Optional, defaults to current time
}
```

**Response:**
```json
{
  "status": "success",
  "id": 0
}
```

#### GET /metrics

Get all metrics.

**Response:**
```json
[
  {
    "value": 123,
    "timestamp": 1646006400
  },
  {
    "value": 456,
    "timestamp": 1646010000
  }
]
```

### Labeled Metrics

#### POST /labeled-metrics

Add a new labeled metric to the stream.

**Request Body:**
```json
{
  "label": "cpu",
  "value": 123,
  "timestamp": 1646006400  // Optional, defaults to current time
}
```

**Response:**
```json
{
  "status": "success",
  "id": 0
}
```

#### GET /labeled-metrics

Get all labeled metrics.

**Response:**
```json
[
  {
    "label": "cpu",
    "value": 123,
    "timestamp": 1646006400
  },
  {
    "label": "memory",
    "value": 456,
    "timestamp": 1646010000
  }
]
```

### Transformations

#### POST /metrics/transform

Transform metrics according to specified transformations.

**Request Body:**
```json
{
  "transformations": [
    {
      "filter": {"type": "gt", "value": 100},
      "aggregation": "sum",
      "time_grouping": "hour"
    },
    {
      "filter": {"type": "lt", "value": 1000}
    }
  ]
}
```

**Response:**
```json
[
  {
    "value": 123,
    "timestamp": 1646006400
  }
]
```

#### POST /labeled-metrics/transform

Transform labeled metrics with additional support for label filtering.

**Request Body:**
```json
{
  "transformations": [
    {
      "filter": {"type": "gt", "value": 100},
      "aggregation": "sum",
      "time_grouping": "hour",
      "label_filter": "cpu"
    }
  ]
}
```

**Response:**
```json
[
  {
    "value": 123,
    "timestamp": 1646006400
  }
]
```

## Supported Transformations

### Filters

- `gt` - Greater Than
- `lt` - Less Than
- `gte` - Greater Than or Equal
- `lte` - Less Than or Equal
- `eq` - Equal

### Aggregations

- `sum` - Sum
- `avg` - Average
- `min` - Minimum
- `max` - Maximum

### Time Groupings

- `hour` - Group by hour
- `minute` - Group by minute
- `day` - Group by day

## Extension Points

The API includes placeholder endpoints for extending the functionality:

- `/transformations/filters` - For registering custom filters
- `/transformations/aggregations` - For registering custom aggregations

| Note that true extensibility would require modifying the underlying Rust library.
|
## Documentation

Detailed documentation is available in the [docs](docs) directory:

- [Documentation Index](docs/README.md) - Start here for an overview of available documentation
- [Labeled Metrics Endpoints](docs/labeled-metrics-endpoints.md) - Comprehensive documentation for all labeled metrics endpoints, including examples and best practices
- [Labeled Metrics Pipeline API](docs/labeled-metrics-pipeline.md) - Detailed guide for the modern fluent pipeline API for labeled metrics
