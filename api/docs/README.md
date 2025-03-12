# Metric Query API Documentation

Welcome to the Metric Query API documentation. This directory contains detailed documentation for various aspects of the API.

## Available Documentation

| Document | Description |
|----------|-------------|
| [Integrated Label Handling](integrated-label-handling.md) | Documentation for the new integrated label handling feature (NEW) |
| [Labeled Metrics Endpoints](labeled-metrics-endpoints.md) | Comprehensive documentation for all labeled metrics endpoints, including examples and best practices |
| [Labeled Metrics Pipeline API](labeled-metrics-pipeline.md) | Detailed guide for the modern fluent pipeline API for labeled metrics |

## Overview

The Metric Query API is designed to help teams work with streaming time-series metric data. It provides a powerful interface for transforming and analyzing metrics without requiring knowledge of the underlying streaming technology.
### Core Features

- **Basic Metrics**: Operations with time-series data points (value, timestamp)
- **Labeled Metrics**: Extended metrics with categorical labels (label, value, timestamp)
- **Transformations**: Filter, aggregate, and group metrics data
- **Pipeline API**: Fluent interface for building transformation pipelines
- **Integrated Label Handling**: Direct filtering of labeled metrics through the core pipeline API

### Latest Features

#### Integrated Label Handling

The library now features integrated label handling, which enables direct filtering of labeled metrics through the core pipeline API. This simplifies the code and improves performance by removing the need for a separate processor step.

For detailed information, see [Integrated Label Handling](integrated-label-handling.md).
- **Pipeline API**: Fluent interface for building transformation pipelines

### API Design Principles

1. **Bounded Stream Processing**: Works with bounded portions of larger unbounded streams
2. **Order Independence**: Processing doesn't depend on the ordering of input metrics
3. **Sequential Transformations**: Transformations are applied in the order provided
4. **Strong Type Safety**: Comprehensive validation prevents runtime errors
5. **Extensibility**: Plugin architecture for custom filters, aggregations, and groupings

## Getting Started

The best way to get started with the API is to:
1. Review the main [API README](../README.md) for installation and basic usage
2. Check out the new [Integrated Label Handling](integrated-label-handling.md) documentation
3. Explore the [Labeled Metrics Endpoints](labeled-metrics-endpoints.md) documentation for endpoint details
4. Learn about the modern [Pipeline API](labeled-metrics-pipeline.md) for building fluent transformations
3. Learn about the modern [Pipeline API](labeled-metrics-pipeline.md) for building fluent transformations

## Common Use Cases

- **Time Series Analysis**: Filter, group, and aggregate metrics to identify trends
- **Category Comparison**: Compare metrics across different categories (CPU, memory, etc.)
- **Threshold Detection**: Identify metrics that exceed specified thresholds
- **Data Compression**: Reduce granularity for storage or visualization (hourly/daily averages)