orMetric Query API

A powerful API for transforming, analyzing, and querying time-series metric data in streaming environments.

## Project Structure

The API has been modularized for better organization, maintainability, and scalability:

```
api/
├── app.py                   # Main application entry point
├── config/                  # Configuration settings
│   ├── __init__.py
│   └── swagger.py           # Swagger API documentation configuration
├── models/                  # Data models
│   ├── __init__.py
│   └── store.py             # In-memory storage for metrics
├── routes/                  # API endpoints
│   ├── __init__.py
│   ├── docs.py              # Documentation endpoints
│   ├── extensions.py        # Custom extension endpoints
│   ├── labeled_metrics.py   # Labeled metrics endpoints
│   ├── metrics.py           # Basic metrics endpoints
│   └── tests.py             # Test endpoints
├── utils/                   # Utility functions
│   ├── __init__.py
│   └── utils.py             # Common utilities
└── metric_query_library/    # Core library for metrics processing
    ├── __init__.py
    ├── label_ops.py
    ├── transformations.py
    ├── type_defs.py
    └── validation.py
```

## Features

- **Basic Metrics**: Endpoints for adding and retrieving basic metrics (value, timestamp)
- **Labeled Metrics**: Support for categorized metrics with labels
- **Transformations**:
  - Filtering (value thresholds)
  - Aggregation (sum, avg, min, max)
  - Time Grouping (minute, hour, day)
- **Fluent Pipeline API**: Intuitive method chaining for transformations
- **Plugin Architecture**: Extensible with custom filters, aggregations, and time groupings
- **Comprehensive Documentation**: Interactive Swagger UI with examples and usage patterns

## API Endpoints

### Documentation
- `GET /`: Complete API documentation and information

### Basic Metrics
- `GET /metrics`: Retrieve all basic metrics
- `POST /metrics`: Add a new basic metric
- `POST /metrics/transform`: Apply transformations to basic metrics
- `POST /metrics/pipeline`: Use fluent pipeline API with basic metrics

### Labeled Metrics
- `GET /labeled-metrics`: Retrieve all labeled metrics
- `POST /labeled-metrics`: Add a new labeled metric
- `POST /labeled-metrics/transform`: Apply transformations to labeled metrics
- `POST /labeled-metrics/pipeline`: Use fluent pipeline API with labeled metrics

### Extensions
- `POST /transformations/filters`: Register a custom filter
- `POST /transformations/aggregations`: Register a custom aggregation

### Tests
- `POST /test`: Run predefined test cases

## Running the API

```bash
python app.py
```

The API will be available at `http://localhost:5000`. Swagger documentation is accessible at `http://localhost:5000/apidocs`.

## Development

The modular structure makes it easy to extend the API:

1. To add new endpoints, create a new file in the `routes/` directory and register the blueprint in `app.py`
2. To add new models, create a new file in the `models/` directory
3. To add new utility functions, extend the `utils/utils.py` file
4. To add new configuration options, extend the `config/` directory

## Design Principles

- **Separation of Concerns**: Each module has a clear, specific responsibility
- **Modularity**: Components are easy to extend, replace, or update independently
- **RESTful Design**: Endpoints follow REST conventions
- **Documentation**: Comprehensive inline documentation for all endpoints
- **Type Safety**: Strong typing with validation for all inputs and outputs
