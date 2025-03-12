from flask import Flask, request, jsonify
from flasgger import Swagger
from flask_cors import CORS
from datetime import datetime
import json
from typing import List, Dict, Any, Optional, Union

# Import from our improved library
import metric_query_library as mq
from metric_query_library.type_defs import (
    FilterSpec, TransformationSpec, MetricDict, LabeledMetricDict,
    ApiErrorResponse, ApiSuccessResponse
)
from metric_query_library.validation import (
    validate_metric, validate_labeled_metric, validate_transformations
)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configure Swagger with detailed OpenAPI specification
swagger = Swagger(app, template={
    "swagger": "2.0",
    "info": {
        "title": "Metric Query API",
        "description": """
        # Metric Query Interface
        
        ## Overview
        This API provides a powerful interface for transforming streaming metric data. It was designed for teams
        working with time-series metrics who need flexible transformation capabilities without concerning
        themselves with the underlying streaming technology.
        
        ## Core Concepts
        - **Metrics**: Time-series data points with a value and timestamp
        - **Labeled Metrics**: Extended metrics with a categorical label
        - **Transformations**: Operations to filter, aggregate, and group metrics
        - **Pipeline API**: Fluent interface for chaining transformations
        
        ## Design Constraints
        - Metrics are delivered as a bounded stream (part of a larger unbounded stream)
        - Metrics aren't guaranteed to be in order and can't be pre-sorted
        - Transformations are applied sequentially in the order provided
        """,
        "version": "1.0.0",
        "contact": {
            "name": "API Support",
            "url": "http://www.example.com/support"
        },
        "license": {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT"
        }
    },
    "tags": [
        {
            "name": "Metrics",
            "description": "Operations with basic metrics (value, timestamp)"
        },
        {
            "name": "Labeled Metrics",
            "description": "Operations with labeled metrics (label, value, timestamp)"
        },
        {
            "name": "Transformations",
            "description": "Filter, aggregate, and group metrics data"
        },
        {
            "name": "Pipeline",
            "description": "Fluent interface for building transformation pipelines"
        },
        {
            "name": "Tests",
            "description": "Test endpoints for demonstrating functionality"
        },
        {
            "name": "Extensions",
            "description": "Extension points for custom functionality"
        },
        {
            "name": "Documentation",
            "description": "API documentation and guidelines"
        }
    ],
    "definitions": {
        "Metric": {
            "type": "object",
            "description": "A single data point in a metric stream",
            "required": ["value", "timestamp"],
            "properties": {
                "value": {
                    "type": "integer",
                    "description": "The metric value (any positive or negative integer)"
                },
                "timestamp": {
                    "type": "integer",
                    "description": "Unix timestamp in seconds (between the Linux epoch and now, no future events)"
                }
            }
        },
        "LabeledMetric": {
            "type": "object",
            "description": "A single data point in a labeled metric stream",
            "required": ["label", "value", "timestamp"],
            "properties": {
                "label": {
                    "type": "string",
                    "description": "Category label from a known set of values (e.g., CPU_USAGE, MEMORY_USAGE)"
                },
                "value": {
                    "type": "integer",
                    "description": "The metric value (any positive or negative integer)"
                },
                "timestamp": {
                    "type": "integer",
                    "description": "Unix timestamp in seconds (between the Linux epoch and now)"
                }
            }
        },
        "FilterOperation": {
            "type": "object",
            "description": "Filter operation specification",
            "required": ["type", "value"],
            "properties": {
                "type": {
                    "type": "string",
                    "description": "Filter operator type",
                    "enum": ["gt", "lt", "ge", "le", "eq"],
                    "example": "gt"
                },
                "value": {
                    "type": "integer",
                    "description": "Value to compare against",
                    "example": 100
                }
            }
        },
        "AggregationOperation": {
            "type": "string",
            "description": "Aggregation function type",
            "enum": ["sum", "avg", "min", "max"],
            "example": "sum"
        },
        "TimeGroupingOperation": {
            "type": "string",
            "description": "Time unit to group metrics by",
            "enum": ["minute", "hour", "day"],
            "example": "hour"
        },
        "Transformation": {
            "type": "object",
            "description": "A single transformation to apply to metrics",
            "properties": {
                "filter": {
                    "$ref": "#/definitions/FilterOperation"
                },
                "aggregation": {
                    "$ref": "#/definitions/AggregationOperation"
                },
                "time_grouping": {
                    "$ref": "#/definitions/TimeGroupingOperation"
                },
                "label_filter": {
                    "type": "string",
                    "description": "Label to filter metrics by (only for labeled metrics)",
                    "example": "CPU_USAGE"
                }
            }
        },
        "PipelineOperation": {
            "type": "object",
            "description": "An operation in a fluent transformation pipeline",
            "required": ["operation"],
            "properties": {
                "operation": {
                    "type": "string",
                    "description": "Pipeline operation name",
                    "enum": [
                        "filter", "greater_than", "less_than", "equal_to",
                        "aggregate", "sum", "average", "minimum", "maximum",
                        "group_by", "group_by_minute", "group_by_hour", "group_by_day"
                    ]
                },
                "type": {
                    "type": "string",
                    "description": "Type parameter for filter or aggregate operations"
                },
                "value": {
                    "type": "integer",
                    "description": "Value parameter for filter operations"
                },
                "time_grouping": {
                    "type": "string",
                    "description": "Time unit for group_by operation"
                },
                "aggregation": {
                    "type": "string",
                    "description": "Aggregation function for group_by operation"
                }
            }
        }
    },
    "securityDefinitions": {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API key for authentication (future implementation)"
        }
    },
    "externalDocs": {
        "description": "Metric Query Interface Design Documentation",
        "url": "https://github.com/example/metric-query-rs/docs"
    }
})

# In-memory storage for metrics
metrics_store: List[mq.Metric] = []
labeled_metrics_store: List[mq.LabeledMetric] = []

# Add comprehensive API description and constraints to the app
@app.route('/', methods=['GET'])
def api_info():
    """
    Metric Query Interface Documentation
    ---
    tags:
      - Documentation
    description: |
      Complete documentation of the Metric Query Interface including design principles, constraints,
      data models, transformations, extension points, and usage patterns.
      
      This comprehensive reference guide provides all the information needed to understand and
      effectively use the Metric Query Interface.
    produces:
      - application/json
    responses:
      200:
        description: Comprehensive API information and constraints
        schema:
          type: object
          properties:
            name:
              type: string
              example: "Metric Query API"
            version:
              type: string
              example: "1.0.0"
            description:
              type: string
            design_principles:
              type: object
            architecture:
              type: object
            data_models:
              type: object
            constraints:
              type: object
            operations:
              type: object
            transformations:
              type: object
            endpoints:
              type: object
            extension_mechanisms:
              type: object
            fluent_api:
              type: object
            usage_patterns:
              type: object
            examples:
              type: object
            reference_implementation:
              type: object
    """
    return jsonify({
        "name": "Metric Query API",
        "version": "1.0.0",
        "description": "Comprehensive API for querying, transforming, and analyzing time series metric data in streaming environments",
        
        "design_principles": {
            "language_agnostic": "Core implementation in Rust with Python bindings, allowing for multiple language interfaces",
            "performance_focused": "Designed for high-throughput streaming data processing with minimal overhead",
            "extensible": "Plugin architecture for custom transformations, filters, and aggregations",
            "fluent_interface": "Intuitive chaining of operations for better readability and maintainability",
            "stateless_transformations": "Each transformation operation maintains no state between invocations for reliability",
            "type_safety": "Strong type checking and validation to prevent runtime errors",
            "bounded_stream_processing": "Designed to work with bounded portions of larger unbounded streams",
            "order_independence": "Processing does not depend on the ordering of input metrics",
            "composability": "Small, focused operations that can be combined in powerful ways",
            "separation_of_concerns": "Clear distinction between different types of operations (filtering, aggregation, time grouping)"
        },
        
        "architecture": {
            "core_engine": {
                "description": "Rust-based transformation engine for high performance",
                "components": ["Filter Engine", "Aggregation Engine", "Time Grouping Engine", "Plugin Registry"]
            },
            "bindings": {
                "description": "Language bindings to connect to the core engine",
                "supported": ["Python", "Future: JavaScript, Java"]
            },
            "api_layer": {
                "description": "RESTful Flask API with Swagger documentation",
                "components": ["HTTP Endpoints", "Data Validation", "Error Handling", "Documentation"]
            },
            "plugin_system": {
                "description": "Trait-based plugin architecture for extensions",
                "extension_points": ["Custom Filters", "Custom Aggregations", "Custom Time Groupings"]
            },
            "type_system": {
                "description": "Strong typing with validation for all inputs and outputs",
                "components": ["Request Schema Validation", "Response Schema Validation", "Error Type System"]
            },
            "execution_model": {
                "description": "Pipeline-based sequential processing",
                "flow": "Input Metrics → Filters → Aggregations → Time Groupings → Output Metrics"
            }
        },
        
        "data_models": {
            "basic_metric": {
                "description": "Basic time-series metric data point",
                "structure": {
                    "value": "Integer value representing the metric measurement",
                    "timestamp": "Unix timestamp (seconds) when the measurement was taken"
                },
                "constraints": {
                    "value": "Any positive or negative integer (no floating point)",
                    "timestamp": "Any valid unix timestamp between Linux epoch and current time (no future events)"
                },
                "validation_rules": {
                    "value": "Must be a valid integer",
                    "timestamp": "Must be a positive integer not exceeding current time"
                },
                "canonical_json": {
                    "value": 42,
                    "timestamp": 1678901234
                },
                "internal_representation": "Rust struct Metric { value: i64, timestamp: u64 }"
            },
            "labeled_metric": {
                "description": "Extended metric with categorical label",
                "structure": {
                    "label": "String identifier categorizing the metric type",
                    "value": "Integer value representing the metric measurement",
                    "timestamp": "Unix timestamp when the measurement was taken"
                },
                "constraints": {
                    "label": "String from a known set of categories (enum-like)",
                    "value": "Any positive or negative integer",
                    "timestamp": "Any valid unix timestamp between Linux epoch and current time"
                },
                "validation_rules": {
                    "label": "Must be a non-empty string",
                    "value": "Must be a valid integer",
                    "timestamp": "Must be a positive integer not exceeding current time"
                },
                "canonical_json": {
                    "label": "CPU_USAGE",
                    "value": 75,
                    "timestamp": 1678901234
                },
                "internal_representation": "Rust struct LabeledMetric { label: String, value: i64, timestamp: u64 }"
            },
            "filter_specification": {
                "description": "Specification for a filter operation",
                "structure": {
                    "type": "Filter operator type (gt, lt, ge, le, eq)",
                    "value": "Value to compare against"
                },
                "canonical_json": {
                    "filter": {
                        "type": "gt",
                        "value": 100
                    }
                },
                "internal_representation": "Rust struct Filter { type: FilterType, value: i64 }"
            },
            "aggregation_specification": {
                "description": "Specification for an aggregation operation",
                "structure": {
                    "type": "Aggregation function (sum, avg, min, max)"
                },
                "canonical_json": {
                    "aggregation": "sum"
                },
                "internal_representation": "Rust struct Aggregation { type: AggregationType }"
            },
            "time_grouping_specification": {
                "description": "Specification for a time grouping operation",
                "structure": {
                    "unit": "Time unit for grouping (minute, hour, day)"
                },
                "canonical_json": {
                    "time_grouping": "hour"
                },
                "internal_representation": "Rust struct TimeGrouping { unit: TimeUnit }"
            },
            "transformation": {
                "description": "Complete specification for a metric transformation",
                "components": {
                    "filter": "Optional criteria for including/excluding metrics",
                    "aggregation": "Optional function for combining multiple metric values",
                    "time_grouping": "Optional time window for organizing metrics"
                },
                "canonical_json": {
                    "filter": {
                        "type": "gt",
                        "value": 100
                    },
                    "aggregation": "sum",
                    "time_grouping": "hour"
                },
                "internal_representation": "Rust struct Transformation { filter: Option<Filter>, aggregation: Option<Aggregation>, time_grouping: Option<TimeGrouping> }"
            },
            "pipeline_operation": {
                "description": "Operation in a fluent transformation pipeline",
                "structure": {
                    "operation": "Operation name (e.g., filter, greater_than, group_by_hour)",
                    "parameters": "Operation-specific parameters"
                },
                "canonical_json": {
                    "operation": "greater_than",
                    "value": 100
                },
                "internal_representation": "Rust trait PipelineOperation { fn apply(&self, metrics: &[Metric]) -> Vec<Metric>; }"
            }
        },
        
        "constraints": {
            "metrics": {
                "description": "Bounded stream of Metric objects",
                "properties": {
                    "order": "Metrics aren't guaranteed to be in any particular order",
                    "sorting": "Can't pre-sort the list as it's part of a larger stream of data",
                    "value_range": "Any positive or negative integer (no floating point)",
                    "timestamp_range": "Any timestamp between the Linux epoch and now (no future events)",
                    "uniqueness": "No guarantee of uniqueness; duplicate timestamps may exist",
                    "completeness": "No guarantee of complete data; gaps in time series may exist",
                    "size_limitations": "System is designed to handle large volumes of metrics efficiently",
                    "persistence": "Metrics are stored in memory by default; external persistence is an implementation detail"
                }
            },
            "operations": {
                "filters": {
                    "description": "Can be applied to value and timestamp (and label for LabeledMetrics)",
                    "types": ["gt", "lt", "ge", "le", "eq"],
                    "composition": "Multiple filters can be chained in sequence",
                    "limitations": "Filters operate on individual metrics; they cannot compare multiple metrics",
                    "performance": "O(n) where n is the number of metrics in the stream"
                },
                "aggregations": {
                    "description": "Can ONLY be applied to value, not timestamp or labels",
                    "types": ["sum", "avg", "min", "max"],
                    "input_requirements": "Requires at least one metric to produce a result",
                    "output": "Produces a single metric with aggregated value",
                    "limitations": "Loss of individual metric data after aggregation",
                    "performance": "O(n) where n is the number of metrics being aggregated"
                },
                "timeGroupings": {
                    "description": "Can ONLY be applied to timestamp, not value or labels",
                    "types": ["minute", "hour", "day"],
                    "behavior": "Rounds timestamps down to the nearest time unit boundary",
                    "output": "Creates buckets of metrics grouped by time periods",
                    "limitations": "Cannot use custom time periods without extending the system",
                    "performance": "O(n) for grouping, O(m*g) for aggregation within groups (where m is metrics, g is groups)"
                }
            },
            "transformations": {
                "chaining": "Transformations are applied sequentially in the order provided",
                "extension": "Custom filters and aggregations require extending the Rust library",
                "compatibility": "Not all transformations can be combined (e.g., multiple aggregations)",
                "complexity": "Performance degrades with increasing number of chained transformations",
                "order_dependency": "The order of transformations matters and can produce different results",
                "determinism": "Given the same inputs and transformations, outputs will always be identical",
                "side_effects": "Transformations do not modify the original metrics collection",
                "parallelism": "Designed for potential parallel execution of independent transformations (future feature)"
            },
            "labeledMetrics": {
                "description": "Extended metrics with a label field",
                "labelTypes": "Labels are considered to be from a known set of values (enum-like)",
                "operations": "Filters can be applied to labels in addition to values and timestamps",
                "uniqueness": "No guarantee that label+timestamp combinations are unique",
                "grouping": "Can be grouped by label before other transformations",
                "conversion": "Can be converted to basic metrics by dropping the label information",
                "performance": "Slightly higher memory footprint than basic metrics"
            }
        },
        
        "operations": {
            "filters": {
                "gt": {
                    "description": "Greater than: value > threshold",
                    "signature": "filter(type='gt', value=threshold)",
                    "fluent_api": "greater_than(threshold)",
                    "example": "pipeline.greater_than(100)",
                    "application": "Filters metrics where value > 100"
                },
                "lt": {
                    "description": "Less than: value < threshold",
                    "signature": "filter(type='lt', value=threshold)",
                    "fluent_api": "less_than(threshold)",
                    "example": "pipeline.less_than(100)",
                    "application": "Filters metrics where value < 100"
                },
                "ge": {
                    "description": "Greater than or equal: value >= threshold",
                    "signature": "filter(type='ge', value=threshold)",
                    "fluent_api": "greater_than_or_equal(threshold)",
                    "example": "pipeline.greater_than_or_equal(100)",
                    "application": "Filters metrics where value >= 100"
                },
                "le": {
                    "description": "Less than or equal: value <= threshold",
                    "signature": "filter(type='le', value=threshold)",
                    "fluent_api": "less_than_or_equal(threshold)",
                    "example": "pipeline.less_than_or_equal(100)",
                    "application": "Filters metrics where value <= 100"
                },
                "eq": {
                    "description": "Equal to: value == threshold",
                    "signature": "filter(type='eq', value=threshold)",
                    "fluent_api": "equal_to(threshold)",
                    "example": "pipeline.equal_to(100)",
                    "application": "Filters metrics where value == 100"
                },
                "label_filter": {
                    "description": "Filter by exact label match (labeled metrics only)",
                    "signature": "filter_by_label(label)",
                    "fluent_api": "filter_by_label(label)",
                    "example": "processor.filter_by_label('CPU_USAGE')",
                    "application": "Filters labeled metrics where label == 'CPU_USAGE'"
                }
            },
            "aggregations": {
                "sum": {
                    "description": "Sum of all values",
                    "signature": "aggregate(type='sum')",
                    "fluent_api": "sum()",
                    "example": "pipeline.sum()",
                    "application": "Aggregates all metric values into a single sum"
                },
                "avg": {
                    "description": "Average (mean) of all values",
                    "signature": "aggregate(type='avg')",
                    "fluent_api": "average()",
                    "example": "pipeline.average()",
                    "application": "Aggregates all metric values into a single average"
                },
                "min": {
                    "description": "Minimum value",
                    "signature": "aggregate(type='min')",
                    "fluent_api": "minimum()",
                    "example": "pipeline.minimum()",
                    "application": "Finds the minimum value among all metrics"
                },
                "max": {
                    "description": "Maximum value",
                    "signature": "aggregate(type='max')",
                    "fluent_api": "maximum()",
                    "example": "pipeline.maximum()",
                    "application": "Finds the maximum value among all metrics"
                }
            },
            "timeGroupings": {
                "minute": {
                    "description": "Group by minute (floor timestamp to nearest minute)",
                    "signature": "group_by(time_grouping='minute', aggregation=agg_type)",
                    "fluent_api": "group_by_minute(aggregation=agg_type)",
                    "example": "pipeline.group_by_minute('sum')",
                    "application": "Groups metrics into minute buckets and applies sum aggregation"
                },
                "hour": {
                    "description": "Group by hour (floor timestamp to nearest hour)",
                    "signature": "group_by(time_grouping='hour', aggregation=agg_type)",
                    "fluent_api": "group_by_hour(aggregation=agg_type)",
                    "example": "pipeline.group_by_hour('avg')",
                    "application": "Groups metrics into hour buckets and applies average aggregation"
                },
                "day": {
                    "description": "Group by day (floor timestamp to nearest day)",
                    "signature": "group_by(time_grouping='day', aggregation=agg_type)",
                    "fluent_api": "group_by_day(aggregation=agg_type)",
                    "example": "pipeline.group_by_day('max')",
                    "application": "Groups metrics into day buckets and applies maximum aggregation"
                }
            },
            "labelGroupings": {
                "description": "Group metrics by their label (labeled metrics only)",
                "behavior": "Creates separate groups for each unique label value",
                "fluent_api": "processor.to_pipeline()",
                "application": "Groups labeled metrics by label type before applying transformations"
            }
        },
        
        "transformations": {
            "types": {
                "filtering": {
                    "description": "Include/exclude metrics based on criteria",
                    "use_cases": ["Remove outliers", "Focus on specific value ranges", "Time-based filtering"]
                },
                "aggregation": {
                    "description": "Combine multiple metrics into a single result",
                    "use_cases": ["Calculate totals", "Find averages", "Identify extremes"]
                },
                "grouping": {
                    "description": "Organize metrics into buckets for further processing",
                    "use_cases": ["Time-based analysis", "Category-based analysis"]
                }
            },
            "usage_patterns": {
                "basic": {
                    "description": "Apply a single transformation to a metric stream",
                    "example": "pipeline.greater_than(100).execute()"
                },
                "chained": {
                    "description": "Apply multiple transformations in sequence",
                    "example": "pipeline.greater_than(100).group_by_hour('sum').execute()"
                },
                "grouped": {
                    "description": "Apply transformations after grouping metrics",
                    "example": "processor.filter_by_label('CPU_USAGE').to_pipeline().group_by_hour('avg').execute()"
                },
                "conditional": {
                    "description": "Apply transformations based on metric properties",
                    "implementation": "Custom logic in client code that chooses different transformations"
                }
            },
            "implementation": {
                "legacy": {
                    "description": "Original transformation function with explicit transformation objects",
                    "example": "transform(metrics, [{'filter': {'type': 'gt', 'value': 100}}])"
                },
                "fluent": {
                    "description": "Modern pipeline API with method chaining",
                    "example": "pipeline.greater_than(100).group_by_hour('sum').execute()"
                },
                "extension": {
                    "description": "Custom transformations via plugin system",
                    "example": "Implement FilterPlugin trait and register with registry"
                }
            }
        },
        
        "endpoints": {
            "metrics": {
                "GET /metrics": {
                    "description": "Retrieve all stored metrics",
                    "response": "Array of metric objects",
                    "usage": "GET /metrics"
                },
                "POST /metrics": {
                    "description": "Add a new metric",
                    "payload": {"value": 42, "timestamp": 1678901234},
                    "response": {"status": "success", "id": 0},
                    "usage": "POST /metrics {\"value\": 42, \"timestamp\": 1678901234}"
                }
            },
            "labeledMetrics": {
                "GET /labeled-metrics": {
                    "description": "Retrieve all stored labeled metrics",
                    "response": "Array of labeled metric objects",
                    "usage": "GET /labeled-metrics"
                },
                "POST /labeled-metrics": {
                    "description": "Add a new labeled metric",
                    "payload": {"label": "CPU_USAGE", "value": 75, "timestamp": 1678901234},
                    "response": {"status": "success", "id": 0},
                    "usage": "POST /labeled-metrics {\"label\": \"CPU_USAGE\", \"value\": 75, \"timestamp\": 1678901234}"
                }
            },
            "transformations": {
                "POST /metrics/transform": {
                    "description": "Apply transformations to basic metrics",
                    "payload": {"transformations": [{"filter": {"type": "gt", "value": 100}}, {"aggregation": "sum", "time_grouping": "hour"}]},
                    "response": "Array of transformed metrics",
                    "usage": "POST /metrics/transform {\"transformations\": [{\"filter\": {\"type\": \"gt\", \"value\": 100}}, {\"aggregation\": \"sum\", \"time_grouping\": \"hour\"}]}"
                },
                "POST /labeled-metrics/transform": {
                    "description": "Apply transformations to labeled metrics",
                    "payload": {"transformations": [{"label_filter": "CPU_USAGE"}, {"filter": {"type": "gt", "value": 50}}, {"aggregation": "avg", "time_grouping": "hour"}]},
                    "response": "Array of transformed metrics",
                    "usage": "POST /labeled-metrics/transform {\"transformations\": [{\"label_filter\": \"CPU_USAGE\"}, {\"filter\": {\"type\": \"gt\", \"value\": 50}}, {\"aggregation\": \"avg\", \"time_grouping\": \"hour\"}]}"
                }
            },
            "pipelines": {
                "POST /metrics/pipeline": {
                    "description": "Apply pipeline transformations to basic metrics",
                    "payload": {"pipeline": [{"operation": "greater_than", "value": 100}, {"operation": "group_by_hour", "aggregation": "sum"}]},
                    "response": "Array of transformed metrics",
                    "usage": "POST /metrics/pipeline {\"pipeline\": [{\"operation\": \"greater_than\", \"value\": 100}, {\"operation\": \"group_by_hour\", \"aggregation\": \"sum\"}]}"
                },
                "POST /labeled-metrics/pipeline": {
                    "description": "Apply pipeline transformations to labeled metrics",
                    "payload": {"label_operations": [{"operation": "filter_by_label", "label": "CPU_USAGE"}], "pipeline": [{"operation": "greater_than", "value": 50}, {"operation": "group_by_hour", "aggregation": "avg"}]},
                    "response": "Array of transformed metrics",
                    "usage": "POST /labeled-metrics/pipeline {\"label_operations\": [{\"operation\": \"filter_by_label\", \"label\": \"CPU_USAGE\"}], \"pipeline\": [{\"operation\": \"greater_than\", \"value\": 50}, {\"operation\": \"group_by_hour\", \"aggregation\": \"avg\"}]}"
                }
            },
            "extensions": {
                "POST /transformations/filters": {
                    "description": "Register a custom filter",
                    "payload": {"name": "in_range", "description": "Filter values within range", "parameters": {"min": 100, "max": 500}, "implementation": "..."},
                    "response": {"status": "success", "message": "Custom filter registered"},
                    "usage": "POST /transformations/filters {\"name\": \"in_range\", \"description\": \"Filter values within range\", \"parameters\": {\"min\": 100, \"max\": 500}, \"implementation\": \"...\"}"
                },
                "POST /transformations/aggregations": {
                    "description": "Register a custom aggregation",
                    "payload": {"name": "variance", "description": "Calculate variance", "parameters": {}, "implementation": "..."},
                    "response": {"status": "success", "message": "Custom aggregation registered"},
                    "usage": "POST /transformations/aggregations {\"name\": \"variance\", \"description\": \"Calculate variance\", \"parameters\": {}, \"implementation\": \"...\"}"
                }
            },
            "test": {
                "POST /test": {
                    "description": "Run predefined test cases with sample data",
                    "payload": {"test_type": "time_grouping", "parameters": {"time_grouping": "hour", "aggregation_type": "avg"}},
                    "response": "Test results with metrics and description",
                    "usage": "POST /test {\"test_type\": \"time_grouping\", \"parameters\": {\"time_grouping\": \"hour\", \"aggregation_type\": \"avg\"}}"
                }
            }
        },
        
        "extension_mechanisms": {
            "custom_filters": {
                "description": "Extend filtering capabilities with custom implementations",
                "interface": "Implement the FilterPlugin trait in Rust",
                "registration": "Use the extension API to register new filters",
                "example": "Range filter: check if value is within a specified range",
                "implementation_details": {
                    "trait_definition": "trait FilterPlugin { fn filter(&self, metric: &Metric) -> bool; }",
                    "registration": "registry.register_filter(\"in_range\", Box::new(InRangeFilter { min: 100, max: 500 }))",
                    "usage": "transform(..., [{ \"filter\": { \"type\": \"in_range\", \"min\": 100, \"max\": 500 } }])"
                }
            },
            "custom_aggregations": {
                "description": "Extend aggregation capabilities with custom implementations",
                "interface": "Implement the AggregationPlugin trait in Rust",
                "registration": "Use the extension API to register new aggregations",
                "example": "Percentile calculation: compute specific percentiles of values",
                "implementation_details": {
                    "trait_definition": "trait AggregationPlugin { fn aggregate(&self, metrics: &[Metric]) -> Option<Metric>; }",
                    "registration": "registry.register_aggregation(\"percentile_95\", Box::new(PercentileAggregation { percentile: 95 }))",
                    "usage": "transform(..., [{ \"aggregation\": \"percentile_95\" }])"
                }
            },
            "custom_time_groupings": {
                "description": "Extend time grouping capabilities",
                "interface": "Implement the TimeGroupingPlugin trait in Rust",
                "example": "Custom calendar periods (week, month, quarter)",
                "implementation_details": {
                    "trait_definition": "trait TimeGroupingPlugin { fn group_timestamp(&self, timestamp: u64) -> u64; }",
                    "registration": "registry.register_time_grouping(\"week\", Box::new(WeekGrouping {}))",
                    "usage": "transform(..., [{ \"time_grouping\": \"week\", \"aggregation\": \"sum\" }])"
                }
            }
        },
        
        "fluent_api": {
            "description": "Modern pipeline-based API for chaining transformations",
            "pipeline_creation": {
                "description": "Create a pipeline from a collection of metrics",
                "example": "pipeline = create_pipeline(metrics)"
            },
            "method_chaining": {
                "description": "Chain methods to build a sequence of transformations",
                "example": "pipeline.greater_than(100).group_by_hour('sum')"
            },
            "execution": {
                "description": "Call execute() to apply all transformations and get results",
                "example": "result = pipeline.execute()"
            },
            "operators": {
                "filter": {
                    "description": "Generic filter operation",
                    "signature": "filter(type: str, value: int) -> Pipeline",
                    "example": "pipeline.filter(type='gt', value=100)"
                },
                "shorthand_filters": {
                    "greater_than": {
                        "signature": "greater_than(value: int) -> Pipeline",
                        "example": "pipeline.greater_than(100)"
                    },
                    "less_than": {
                        "signature": "less_than(value: int) -> Pipeline",
                        "example": "pipeline.less_than(100)"
                    },
                    "equal_to": {
                        "signature": "equal_to(value: int) -> Pipeline",
                        "example": "pipeline.equal_to(100)"
                    }
                },
                "aggregations": {
                    "aggregate": {
                        "signature": "aggregate(type: str) -> Pipeline",
                        "example": "pipeline.aggregate(type='sum')"
                    },
                    "shorthand": {
                        "sum": {
                            "signature": "sum() -> Pipeline",
                            "example": "pipeline.sum()"
                        },
                        "average": {
                            "signature": "average() -> Pipeline",
                            "example": "pipeline.average()"
                        },
                        "minimum": {
                            "signature": "minimum() -> Pipeline",
                            "example": "pipeline.minimum()"
                        },
                        "maximum": {
                            "signature": "maximum() -> Pipeline",
                            "example": "pipeline.maximum()"
                        }
                    }
                },
                "grouping": {
                    "group_by": {
                        "signature": "group_by(time_grouping: str, aggregation: str) -> Pipeline",
                        "example": "pipeline.group_by(time_grouping='hour', aggregation='sum')"
                    },
                    "shorthand": {
                        "minute": {
                            "signature": "group_by_minute(aggregation: str = 'sum') -> Pipeline",
                            "example": "pipeline.group_by_minute()"
                        },
                        "hour": {
                            "signature": "group_by_hour(aggregation: str = 'sum') -> Pipeline",
                            "example": "pipeline.group_by_hour()"
                        },
                        "day": {
                            "signature": "group_by_day(aggregation: str = 'sum') -> Pipeline",
                            "example": "pipeline.group_by_day()"
                        }
                    }
                }
            },
            "example_pipeline": "pipeline.filter(gt=100).group_by_hour().sum().execute()",
            "endpoints": {
                "pipeline": "/metrics/pipeline",
                "labeled_pipeline": "/labeled-metrics/pipeline"
            }
        },
        
        "usage_patterns": {
            "basic_metrics_analysis": {
                "description": "Analyze basic metric trends",
                "pattern": "Filter → Group by time → Aggregate",
                "example": "pipeline.greater_than(100).group_by_hour('avg').execute()",
                "use_case": "Analyze hourly average of significant metrics"
            },
            "outlier_detection": {
                "description": "Identify metrics outside normal range",
                "pattern": "Filter for extreme values",
                "example": "pipeline.greater_than(threshold).execute()",
                "use_case": "Find anomalies in system metrics"
            },
            "time_series_compression": {
                "description": "Reduce granularity for storage or visualization",
                "pattern": "Group by time → Aggregate",
                "example": "pipeline.group_by_day('avg').execute()",
                "use_case": "Generate daily summaries from minute-level data"
            },
            "category_analysis": {
                "description": "Compare different categories of metrics",
                "pattern": "Filter by label → Transform → Compare results",
                "example": "processor.filter_by_label('CPU_USAGE').to_pipeline().group_by_hour('avg').execute()",
                "use_case": "Compare CPU usage vs. memory usage patterns"
            },
            "advanced_compositions": {
                "description": "Complex multi-step transformations",
                "example": "First filter out noise, then group by time, then find maximum values",
                "pattern": "Filter → Group → Aggregate → Filter again",
                "use_case": "Find peak hourly values above a threshold"
            }
        },
        
        "examples": {
            "basic_filtering": {
                "description": "Filter metrics with values greater than 500",
                "endpoint": "POST /test with {test_type: 'basic_filtering', parameters: {filter_value: 500}}",
                "fluent_equivalent": "pipeline.greater_than(500).execute()",
                "legacy_equivalent": "transform_metrics(metrics, [{filter: {type: 'gt', value: 500}}])",
                "result_example": [
                    {"value": 600, "timestamp": 1678901234},
                    {"value": 550, "timestamp": 1678901235}
                ]
            },
            "time_grouping": {
                "description": "Group metrics by hour and calculate the average",
                "endpoint": "POST /test with {test_type: 'time_grouping', parameters: {time_grouping: 'hour', aggregation_type: 'avg'}}",
                "fluent_equivalent": "pipeline.group_by_hour('avg').execute()",
                "legacy_equivalent": "transform_metrics(metrics, [{time_grouping: 'hour', aggregation: 'avg'}])",
                "result_example": [
                    {"value": 425, "timestamp": 1678899600},
                    {"value": 312, "timestamp": 1678903200}
                ]
            },
            "chained_transformations": {
                "description": "Filter metrics > 100, group by day and sum",
                "endpoint": "POST /test with {test_type: 'chained_transformations', parameters: {filter_value: 100, time_grouping: 'day', aggregation_type: 'sum'}}",
                "fluent_equivalent": "pipeline.greater_than(100).group_by_day('sum').execute()",
                "legacy_equivalent": "transform_metrics(metrics, [{filter: {type: 'gt', value: 100}}, {time_grouping: 'day', aggregation: 'sum'}])",
                "result_example": [
                    {"value": 2500, "timestamp": 1678838400},
                    {"value": 3200, "timestamp": 1678924800}
                ]
            },
            "labeled_metrics": {
                "description": "Filter CPU usage metrics > 50 and calculate hourly average",
                "endpoint": "POST /labeled-metrics/pipeline",
                "payload": {
                    "label_operations": [{"operation": "filter_by_label", "label": "CPU_USAGE"}],
                    "pipeline": [
                        {"operation": "greater_than", "value": 50},
                        {"operation": "group_by_hour", "aggregation": "avg"}
                    ]
                },
                "result_example": [
                    {"value": 75, "timestamp": 1678899600},
                    {"value": 82, "timestamp": 1678903200}
                ]
            }
        },
        
        "reference_implementation": {
            "github_repository": "https://github.com/example/metric-query-rs",
            "core_components": {
                "metric_models": "src/models/",
                "transformations": "src/transformations.rs",
                "plugins": "src/plugins.rs",
                "errors": "src/errors.rs",
                "api": "api/app.py",
                "python_bindings": "api/metric_query_library/"
            },
            "language_stack": {
                "core_engine": "Rust",
                "bindings": "Python (via PyO3)",
                "api_layer": "Flask, Flasgger",
                "ui": "React, TypeScript"
            },
            "installation": {
                "requirements": "Rust (1.60+), Python (3.8+), Node.js (14+)",
                "setup": "cargo build && pip install -e . && cd ui && npm install",
                "running": "python api/app.py"
            },
            "documentation": {
                "api_docs": "/",
                "swagger": "/apidocs",
                "code_comments": "Extensively documented source code"
            }
        }
    })

@app.route('/metrics', methods=['POST'])
def add_metric():
    """
    Add a new metric to the stream
    ---
    tags:
      - Metrics
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            value:
              type: integer
              example: 42
            timestamp:
              type: integer
              example: 1678901234
    responses:
      201:
        description: Successfully created metric
        examples:
          application/json:
            status: success
            id: 0
      400:
        description: Invalid input
    """
    data = request.json
    
    # Validate input
    is_valid, error = validate_metric(data)
    if not is_valid:
        return jsonify({"error": error}), 400
    
    # Create a new metric
    metric = mq.Metric(
        value=int(data['value']),
        timestamp=int(data.get('timestamp', datetime.now().timestamp()))
    )
    
    metrics_store.append(metric)
    return jsonify({"status": "success", "id": len(metrics_store) - 1}), 201

@app.route('/labeled-metrics', methods=['POST'])
def add_labeled_metric():
    """
    Add a new labeled metric to the stream
    ---
    tags:
      - Labeled Metrics
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            label:
              type: string
              example: cpu_usage
            value:
              type: integer
              example: 75
            timestamp:
              type: integer
              example: 1678901234
    responses:
      201:
        description: Successfully created labeled metric
        examples:
          application/json:
            status: success
            id: 0
      400:
        description: Invalid input
    """
    data = request.json
    
    # Validate input
    is_valid, error = validate_labeled_metric(data)
    if not is_valid:
        return jsonify({"error": error}), 400
    
    # Create a new labeled metric
    metric = mq.LabeledMetric(
        label=data['label'],
        value=int(data['value']),
        timestamp=int(data.get('timestamp', datetime.now().timestamp()))
    )
    
    labeled_metrics_store.append(metric)
    return jsonify({"status": "success", "id": len(labeled_metrics_store) - 1}), 201

@app.route('/metrics', methods=['GET'])
def get_metrics():
    """
    Get all metrics
    ---
    tags:
      - Metrics
    responses:
      200:
        description: A list of all metrics
        schema:
          type: array
          items:
            type: object
            properties:
              value:
                type: integer
                description: The metric value
              timestamp:
                type: integer
                description: Unix timestamp in seconds
    """
    # Use to_dicts helper from our improved library
    result = [{'value': m.value, 'timestamp': m.timestamp} for m in metrics_store]
    return jsonify(result)

@app.route('/labeled-metrics', methods=['GET'])
def get_labeled_metrics():
    """
    Get all labeled metrics
    ---
    tags:
      - Labeled Metrics
    responses:
      200:
        description: A list of all labeled metrics
        schema:
          type: array
          items:
            type: object
            properties:
              label:
                type: string
                description: The metric label (category)
              value:
                type: integer
                description: The metric value
              timestamp:
                type: integer
                description: Unix timestamp in seconds
    """
    # Use to_dicts helper from our improved library
    result = [{'label': m.label, 'value': m.value, 'timestamp': m.timestamp} for m in labeled_metrics_store]
    return jsonify(result)

@app.route('/metrics/transform', methods=['POST'])
def transform_metrics():
    """
    Transform metrics according to specified transformations
    ---
    tags:
      - Transformations
    description: |
      Apply filters, aggregations, and time groupings to a stream of metrics.
      
      **Constraints:**
      - Filters can be applied to metric values or timestamps
      - Aggregations can ONLY be applied to metric values
      - Time groupings can ONLY be applied to timestamps
      - Transformations are applied sequentially in the order provided
      - Input metrics are not guaranteed to be ordered
      - Metrics cannot be pre-sorted as they are part of a larger stream
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - transformations
          properties:
            transformations:
              type: array
              description: A list of transformations to apply sequentially
              items:
                type: object
                properties:
                  filter:
                    type: object
                    description: Filter condition to apply on metrics
                    properties:
                      type:
                        type: string
                        enum: [gt, lt, ge, le, eq]
                        description: Filter operator (greater than, less than, etc.)
                        example: gt
                      value:
                        type: integer
                        description: Value to compare against (can be applied to metric value or timestamp)
                        example: 100
                  aggregation:
                    type: string
                    enum: [sum, avg, min, max]
                    description: Aggregation function to apply on metric values
                    example: sum
                  time_grouping:
                    type: string
                    enum: [hour, minute, day]
                    description: Time unit to group metrics by
                    example: hour
    responses:
      200:
        description: Transformed metrics
        schema:
          type: array
          items:
            type: object
            properties:
              value:
                type: integer
                description: Transformed metric value
              timestamp:
                type: integer
                description: Timestamp (possibly adjusted by time grouping)
        examples:
          application/json:
            - value: 150
              timestamp: 1678901200
      400:
        description: Invalid request
        schema:
          type: object
          properties:
            error:
              type: string
              description: Error message
    """
    data = request.json
    
    # Validate transformations
    is_valid, error = validate_transformations(data)
    if not is_valid:
        return jsonify({"error": error}), 400
    
    # Use our improved transformation function
    result = mq.transform_metrics_to_dicts(metrics_store, data['transformations'])
    return jsonify(result)

@app.route('/labeled-metrics/transform', methods=['POST'])
def transform_labeled_metrics():
    """
    Transform labeled metrics with additional support for label filtering
    ---
    tags:
      - Transformations
    description: |
      Apply filters, aggregations, and time groupings to a stream of labeled metrics.
      
      **Labeled Metrics Constraints:**
      - Labels are considered to be from a known set of values (enum-like)
      - Filters can be applied to labels IN ADDITION TO values and timestamps
      - Like basic metrics, aggregations can ONLY be applied to values
      - Like basic metrics, time groupings can ONLY be applied to timestamps
      - Transformations are applied sequentially in the order provided
      - The label_filter parameter is unique to labeled metrics
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - transformations
          properties:
            transformations:
              type: array
              description: A list of transformations to apply sequentially
              items:
                type: object
                properties:
                  filter:
                    type: object
                    description: Filter condition to apply on metrics
                    properties:
                      type:
                        type: string
                        enum: [gt, lt, ge, le, eq]
                        description: Filter operator (greater than, less than, etc.)
                        example: gt
                      value:
                        type: integer
                        description: Value to compare against (can be applied to metric value or timestamp)
                        example: 100
                  aggregation:
                    type: string
                    enum: [sum, avg, min, max]
                    description: Aggregation function to apply on metric values
                    example: sum
                  time_grouping:
                    type: string
                    enum: [hour, minute, day]
                    description: Time unit to group metrics by
                    example: hour
                  label_filter:
                    type: string
                    description: Label to filter metrics by (only applies to labeled metrics)
                    example: cpu_usage
    responses:
      200:
        description: Transformed metrics
        schema:
          type: array
          items:
            type: object
            properties:
              value:
                type: integer
                description: Transformed metric value
              timestamp:
                type: integer
                description: Timestamp (possibly adjusted by time grouping)
        examples:
          application/json:
            - value: 350
              timestamp: 1678901200
      400:
        description: Invalid request
        schema:
          type: object
          properties:
            error:
              type: string
              description: Error message
    """
    data = request.json
    
    # Validate transformations
    is_valid, error = validate_transformations(data)
    if not is_valid:
        return jsonify({"error": error}), 400
    
    # Extract label filters
    label_filters = []
    for transform_data in data['transformations']:
        if 'label_filter' in transform_data:
            label_filters.append(transform_data['label_filter'])
    
    # Use our improved label operations
    processor = mq.create_labeled_processor(labeled_metrics_store)
    
    # Apply label filtering if specified
    if label_filters:
        processor.filter_by_labels(label_filters)
    
    # Convert to unlabeled metrics and apply transformations
    transformations = [
        {k: v for k, v in t.items() if k != 'label_filter'}
        for t in data['transformations']
    ]
    
    # Convert to pipeline and execute
    pipeline = processor.to_pipeline()
    for transform_data in transformations:
        # Apply filter if present
        if 'filter' in transform_data:
            filter_data = transform_data['filter']
            pipeline.filter(type=filter_data['type'], value=filter_data['value'])
        
        # Check if we have both aggregation and time grouping
        if 'aggregation' in transform_data and 'time_grouping' in transform_data:
            pipeline.group_by(
                time_grouping=transform_data['time_grouping'],
                aggregation=transform_data['aggregation']
            )
        elif 'aggregation' in transform_data:
            pipeline.aggregate(type=transform_data['aggregation'])
    
    result = pipeline.execute_to_dicts()
    return jsonify(result)

@app.route('/metrics/pipeline', methods=['POST'])
def pipeline_transform():
    """
    Transform metrics using fluent pipeline API
    ---
    tags:
      - Transformations
    description: |
      Apply transformations to metrics using a fluent pipeline API.
      This endpoint demonstrates the new fluent interface for chaining transformations.
      
      Example request body:
      ```json
      {
        "pipeline": [
          {"operation": "filter", "type": "gt", "value": 100},
          {"operation": "group_by_hour"},
          {"operation": "aggregate", "type": "sum"}
        ]
      }
      ```
      
      Available operations:
      - filter: Apply a filter (requires type and value)
      - greater_than: Shorthand for filter with type="gt" (requires value)
      - less_than: Shorthand for filter with type="lt" (requires value)
      - equal_to: Shorthand for filter with type="eq" (requires value)
      - aggregate: Apply aggregation (requires type)
      - sum: Shorthand for aggregate with type="sum"
      - average: Shorthand for aggregate with type="avg" 
      - group_by: Group by time and apply aggregation (requires time_grouping and aggregation)
      - group_by_minute: Shorthand for group_by with time_grouping="minute" (optional aggregation, default sum)
      - group_by_hour: Shorthand for group_by with time_grouping="hour" (optional aggregation, default sum)
      - group_by_day: Shorthand for group_by with time_grouping="day" (optional aggregation, default sum)
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - pipeline
          properties:
            pipeline:
              type: array
              description: A list of pipeline operations to apply sequentially
              items:
                type: object
                required:
                  - operation
                properties:
                  operation:
                    type: string
                    description: Operation to apply
                    enum: [filter, greater_than, less_than, equal_to, 
                           aggregate, sum, average, 
                           group_by, group_by_minute, group_by_hour, group_by_day]
                  type:
                    type: string
                    description: Type for filter or aggregation operations
                  value:
                    type: integer
                    description: Value for filter operations
                  time_grouping:
                    type: string
                    description: Time grouping for group_by operation
                  aggregation:
                    type: string
                    description: Aggregation for group_by operation
    responses:
      200:
        description: Transformed metrics
        schema:
          type: array
          items:
            type: object
            properties:
              value:
                type: integer
                description: Transformed metric value
              timestamp:
                type: integer
                description: Timestamp (possibly adjusted by time grouping)
      400:
        description: Invalid request
        schema:
          type: object
          properties:
            error:
              type: string
              description: Error message
    """
    data = request.json
    
    if not data or 'pipeline' not in data:
        return jsonify({"error": "Missing required field: pipeline"}), 400
    
    pipeline_steps = data['pipeline']
    if not isinstance(pipeline_steps, list) or not pipeline_steps:
        return jsonify({"error": "Pipeline must be a non-empty array"}), 400
    
    # Create a pipeline with the metrics
    try:
        pipeline = mq.create_pipeline(metrics_store)
        
        # Apply each operation in sequence
        for i, step in enumerate(pipeline_steps):
            if 'operation' not in step:
                return jsonify({"error": f"Missing operation in pipeline step {i}"}), 400
            
            operation = step['operation']
            
            try:
                if operation == 'filter':
                    if 'type' not in step or 'value' not in step:
                        return jsonify({"error": f"Filter operation requires type and value (step {i})"}), 400
                    pipeline.filter(type=step['type'], value=int(step['value']))
                
                elif operation == 'greater_than':
                    if 'value' not in step:
                        return jsonify({"error": f"greater_than operation requires value (step {i})"}), 400
                    pipeline.greater_than(value=int(step['value']))
                
                elif operation == 'less_than':
                    if 'value' not in step:
                        return jsonify({"error": f"less_than operation requires value (step {i})"}), 400
                    pipeline.less_than(value=int(step['value']))
                
                elif operation == 'equal_to':
                    if 'value' not in step:
                        return jsonify({"error": f"equal_to operation requires value (step {i})"}), 400
                    pipeline.equal_to(value=int(step['value']))
                
                elif operation == 'aggregate':
                    if 'type' not in step:
                        return jsonify({"error": f"aggregate operation requires type (step {i})"}), 400
                    pipeline.aggregate(type=step['type'])
                
                elif operation == 'sum':
                    pipeline.sum()
                
                elif operation == 'average':
                    pipeline.average()
                
                elif operation == 'group_by':
                    if 'time_grouping' not in step or 'aggregation' not in step:
                        return jsonify({"error": f"group_by operation requires time_grouping and aggregation (step {i})"}), 400
                    pipeline.group_by(
                        time_grouping=step['time_grouping'],
                        aggregation=step['aggregation']
                    )
                
                elif operation == 'group_by_minute':
                    agg = step.get('aggregation', 'sum')
                    pipeline.group_by_minute(aggregation=agg)
                
                elif operation == 'group_by_hour':
                    agg = step.get('aggregation', 'sum')
                    pipeline.group_by_hour(aggregation=agg)
                
                elif operation == 'group_by_day':
                    agg = step.get('aggregation', 'sum')
                    pipeline.group_by_day(aggregation=agg)
                
                else:
                    return jsonify({"error": f"Unknown operation: {operation} (step {i})"}), 400
            
            except ValueError as e:
                return jsonify({"error": f"Error in pipeline step {i}: {str(e)}"}), 400
        
        # Execute the pipeline and return results
        result = pipeline.execute_to_dicts()
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": f"Error processing pipeline: {str(e)}"}), 500

@app.route('/labeled-metrics/pipeline', methods=['POST'])
def labeled_pipeline_transform():
    """
    Transform labeled metrics using fluent pipeline API
    ---
    tags:
      - Transformations
    description: |
      Apply transformations to labeled metrics using a fluent pipeline API.
      This endpoint demonstrates working with labeled metrics using the new interface.
      
      Example request body:
      ```json
      {
        "label_operations": [
          {"operation": "filter_by_label", "label": "cpu_usage"}
        ],
        "pipeline": [
          {"operation": "filter", "type": "gt", "value": 50},
          {"operation": "group_by_hour"},
          {"operation": "aggregate", "type": "avg"}
        ]
      }
      ```
      
      Available label operations:
      - filter_by_label: Filter metrics by exact label match (requires label)
      - filter_by_labels: Filter metrics by multiple labels (requires labels array)
      
      See /metrics/pipeline for available pipeline operations.
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            label_operations:
              type: array
              description: Operations to apply to labels before transformation
              items:
                type: object
                required:
                  - operation
                properties:
                  operation:
                    type: string
                    enum: [filter_by_label, filter_by_labels]
                    description: Label operation to apply
                  label:
                    type: string
                    description: Label to filter by (for filter_by_label)
                  labels:
                    type: array
                    items:
                      type: string
                    description: Labels to filter by (for filter_by_labels)
            pipeline:
              type: array
              description: Pipeline operations to apply after label processing
              items:
                type: object
                required:
                  - operation
    responses:
      200:
        description: Transformed metrics
        schema:
          type: array
          items:
            type: object
            properties:
              value:
                type: integer
                description: Transformed metric value
              timestamp:
                type: integer
                description: Timestamp (possibly adjusted by time grouping)
      400:
        description: Invalid request
        schema:
          type: object
          properties:
            error:
              type: string
              description: Error message
    """
    data = request.json
    
    if not data:
        return jsonify({"error": "Empty request data"}), 400
    
    # Create a labeled processor first
    try:
        processor = mq.create_labeled_processor(labeled_metrics_store)
        
        # Apply label operations if any
        if 'label_operations' in data and isinstance(data['label_operations'], list):
            for i, op in enumerate(data['label_operations']):
                if 'operation' not in op:
                    return jsonify({"error": f"Missing operation in label step {i}"}), 400
                
                operation = op['operation']
                
                if operation == 'filter_by_label':
                    if 'label' not in op:
                        return jsonify({"error": f"filter_by_label operation requires label (step {i})"}), 400
                    processor.filter_by_label(op['label'])
                
                elif operation == 'filter_by_labels':
                    if 'labels' not in op or not isinstance(op['labels'], list):
                        return jsonify({"error": f"filter_by_labels operation requires labels array (step {i})"}), 400
                    processor.filter_by_labels(op['labels'])
                
                else:
                    return jsonify({"error": f"Unknown label operation: {operation} (step {i})"}), 400
        
        # Create a pipeline from the processor
        pipeline = processor.to_pipeline()
        
        # Apply pipeline operations if any
        if 'pipeline' in data and isinstance(data['pipeline'], list):
            for i, step in enumerate(data['pipeline']):
                if 'operation' not in step:
                    return jsonify({"error": f"Missing operation in pipeline step {i}"}), 400
                
                operation = step['operation']
                
                try:
                    if operation == 'filter':
                        if 'type' not in step or 'value' not in step:
                            return jsonify({"error": f"Filter operation requires type and value (step {i})"}), 400
                        pipeline.filter(type=step['type'], value=int(step['value']))
                    
                    elif operation == 'greater_than':
                        if 'value' not in step:
                            return jsonify({"error": f"greater_than operation requires value (step {i})"}), 400
                        pipeline.greater_than(value=int(step['value']))
                    
                    elif operation == 'less_than':
                        if 'value' not in step:
                            return jsonify({"error": f"less_than operation requires value (step {i})"}), 400
                        pipeline.less_than(value=int(step['value']))
                    
                    elif operation == 'equal_to':
                        if 'value' not in step:
                            return jsonify({"error": f"equal_to operation requires value (step {i})"}), 400
                        pipeline.equal_to(value=int(step['value']))
                    
                    elif operation == 'aggregate':
                        if 'type' not in step:
                            return jsonify({"error": f"aggregate operation requires type (step {i})"}), 400
                        pipeline.aggregate(type=step['type'])
                    
                    elif operation == 'sum':
                        pipeline.sum()
                    
                    elif operation == 'average':
                        pipeline.average()
                    
                    elif operation == 'group_by':
                        if 'time_grouping' not in step or 'aggregation' not in step:
                            return jsonify({"error": f"group_by operation requires time_grouping and aggregation (step {i})"}), 400
                        pipeline.group_by(
                            time_grouping=step['time_grouping'],
                            aggregation=step['aggregation']
                        )
                    
                    elif operation == 'group_by_minute':
                        agg = step.get('aggregation', 'sum')
                        pipeline.group_by_minute(aggregation=agg)
                    
                    elif operation == 'group_by_hour':
                        agg = step.get('aggregation', 'sum')
                        pipeline.group_by_hour(aggregation=agg)
                    
                    elif operation == 'group_by_day':
                        agg = step.get('aggregation', 'sum')
                        pipeline.group_by_day(aggregation=agg)
                    
                    else:
                        return jsonify({"error": f"Unknown operation: {operation} (step {i})"}), 400
                
                except ValueError as e:
                    return jsonify({"error": f"Error in pipeline step {i}: {str(e)}"}), 400
        
        # Execute the pipeline and return results
        result = pipeline.execute_to_dicts()
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": f"Error processing pipeline: {str(e)}"}), 500

# Extension point: add a custom filter type
@app.route('/transformations/filters', methods=['POST'])
def register_custom_filter():
    """
    Register a custom filter plugin with the transformation registry
    ---
    tags:
      - Extensions
    description: |
      This endpoint demonstrates how to extend the API with custom filters.
      The improved system uses a plugin architecture where new filters can
      be registered at runtime without modifying the core library.
      
      Note: In a production environment, this would involve more security
      and validation to ensure malicious code isn't executed.
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              description: Name of the custom filter
              example: "in_range"
            description:
              type: string
              description: Description of the filter's functionality
              example: "Filter values that fall within a specified range"
            parameters:
              type: object
              description: Parameters required by the custom filter
              example: {"min": 100, "max": 500}
            implementation:
              type: string
              description: Python code implementing the filter logic
              example: "return min_value <= metric.value <= max_value"
    responses:
      201:
        description: Filter registered successfully
        schema:
          type: object
          properties:
            status:
              type: string
              example: "success"
            message:
              type: string
              example: "Custom filter 'in_range' registered successfully"
      400:
        description: Invalid request
        schema:
          type: object
          properties:
            status:
              type: string
              example: "error"
            message:
              type: string
              example: "Missing required field: name"
    """
    # In a real implementation, this would dynamically register a plugin
    # For now, we'll return a placeholder response
    return jsonify({
        "status": "success",
        "message": "Custom filters are supported through the plugin architecture. "
                  "To implement a custom filter, extend the FilterPlugin trait in Rust."
    }), 200

# Extension point: add a custom aggregation type
@app.route('/transformations/aggregations', methods=['POST'])
def register_custom_aggregation():
    """
    Register a custom aggregation plugin with the transformation registry
    ---
    tags:
      - Extensions
    description: |
      This endpoint demonstrates how to extend the API with custom aggregations.
      The improved system uses a plugin architecture where new aggregations can
      be registered at runtime without modifying the core library.
      
      Note: In a production environment, this would involve more security
      and validation to ensure malicious code isn't executed.
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              description: Name of the custom aggregation
              example: "variance"
            description:
              type: string
              description: Description of the aggregation's functionality
              example: "Calculate the variance of the values"
            parameters:
              type: object
              description: Parameters required by the custom aggregation
              example: {}
            implementation:
              type: string
              description: Python code implementing the aggregation logic
              example: "return sum((x - mean)**2 for x in values) / len(values)"
    responses:
      201:
        description: Aggregation registered successfully
        schema:
          type: object
          properties:
            status:
              type: string
              example: "success"
            message:
              type: string
              example: "Custom aggregation 'variance' registered successfully"
      400:
        description: Invalid request
        schema:
          type: object
          properties:
            status:
              type: string
              example: "error"
            message:
              type: string
              example: "Missing required field: name"
    """
    # In a real implementation, this would dynamically register a plugin
    # For now, we'll return a placeholder response
    return jsonify({
        "status": "success",
        "message": "Custom aggregations are supported through the plugin architecture. "
                  "To implement a custom aggregation, extend the AggregationPlugin trait in Rust."
    }), 200

@app.route('/test', methods=['POST'])
def run_test():
    """
    Run a predefined test case on metric data
    ---
    tags:
      - Tests
    description: |
      Execute predefined test cases that demonstrate the Metric Query Interface capabilities.
      
      **Available Test Cases:**
      - **basic_filtering**: Demonstrate filtering metrics by value
      - **time_filtering**: Demonstrate filtering metrics by timestamp
      - **aggregation**: Demonstrate aggregating metric values
      - **time_grouping**: Demonstrate grouping metrics by time units
      - **chained_transformations**: Demonstrate applying multiple transformations in sequence
      - **fluent_api**: Demonstrate using the new fluent pipeline API
      
      All tests operate on metrics from test_data.json and demonstrate the core constraints
      of the Metric Query Interface.
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            test_type:
              type: string
              enum: [basic_filtering, time_filtering, aggregation, time_grouping, chained_transformations, fluent_api]
              example: basic_filtering
            parameters:
              type: object
              properties:
                filter_value:
                  type: integer
                  description: Value to filter by (used in basic_filtering)
                  example: 500
                days_ago:
                  type: integer
                  description: Number of days to look back (used in time_filtering)
                  example: 1
                aggregation_type:
                  type: string
                  enum: [sum, avg, min, max]
                  description: Aggregation function to apply
                  example: avg
                time_grouping:
                  type: string
                  enum: [minute, hour, day]
                  description: Time unit to group by
                  example: hour
    responses:
      200:
        description: Test results
      400:
        description: Invalid request
    """
    data = request.json
    if not data or 'test_type' not in data:
        return jsonify({"error": "Invalid request. Required field: test_type"}), 400
    
    # Load data from test_data.json if metrics_store is empty
    global metrics_store
    if not metrics_store:
        try:
            with open("test_data.json", "r") as f:
                test_data = json.load(f)
                # Convert JSON data to Metric objects
                metrics_store = [mq.Metric(value=item["value"], timestamp=item["timestamp"] // 1000)
                              for item in test_data["basicMetrics"]]
        except FileNotFoundError:
            return jsonify({"error": "No metrics available and test_data.json not found"}), 500
    
    test_type = data['test_type']
    parameters = data.get('parameters', {})
    
    # Basic filtering test
    if test_type == 'basic_filtering':
        filter_value = parameters.get('filter_value', 500)
        
        # Use fluent pipeline API
        pipeline = mq.create_pipeline(metrics_store)
        filtered = pipeline.greater_than(filter_value).execute_to_dicts()
        
        result = {
            "test_name": "Basic filtering",
            "description": f"Filter metrics with values greater than {filter_value}",
            "original_count": len(metrics_store),
            "filtered_count": len(filtered),
            "sample_results": filtered[:5]
        }
        
        return jsonify(result)
    
    # Time-based filtering test
    elif test_type == 'time_filtering':
        days_ago = parameters.get('days_ago', 1)
        cutoff_time = int(datetime.now().timestamp()) - (days_ago * 24 * 60 * 60)
        
        # Use fluent pipeline API 
        pipeline = mq.create_pipeline(metrics_store)
        filtered = pipeline.greater_than_or_equal(cutoff_time).execute_to_dicts()
        
        result = {
            "test_name": "Time-based filtering",
            "description": f"Filter metrics from the past {days_ago} days",
            "original_count": len(metrics_store),
            "filtered_count": len(filtered),
            "sample_results": filtered[:5]
        }
        
        return jsonify(result)
    
    # Aggregation test
    elif test_type == 'aggregation':
        agg_type = parameters.get('aggregation_type', 'avg')
        
        # Use fluent pipeline API
        pipeline = mq.create_pipeline(metrics_store)
        
        if agg_type == 'sum':
            pipeline.sum()
        elif agg_type == 'avg':
            pipeline.average()
        elif agg_type == 'min':
            pipeline.minimum()
        elif agg_type == 'max':
            pipeline.maximum()
        
        result_metrics = pipeline.execute_to_dicts()
        
        result = {
            "test_name": "Aggregation",
            "description": f"Calculate the {agg_type} of all metrics",
            "original_count": len(metrics_store),
            "result_count": len(result_metrics),
            "results": result_metrics
        }
        
        return jsonify(result)
    # Time grouping test
    elif test_type == 'time_grouping':
        agg_type = parameters.get('aggregation_type', 'avg')
        time_group = parameters.get('time_grouping', 'hour')
        
        # Use fluent pipeline API
        pipeline = mq.create_pipeline(metrics_store)
        
        if time_group == 'minute':
            pipeline.group_by_minute(aggregation=agg_type)
        elif time_group == 'hour':
            pipeline.group_by_hour(aggregation=agg_type)
        elif time_group == 'day':
            pipeline.group_by_day(aggregation=agg_type)
        
        result_metrics = pipeline.execute_to_dicts()
        
        # Sort the results by timestamp to ensure chronological order
        sorted_results = sorted(result_metrics, key=lambda x: x['timestamp'])
        
        result = {
            "test_name": "Time grouping",
            "description": f"Group metrics by {time_group} and calculate the {agg_type}",
            "original_count": len(metrics_store),
            "result_count": len(sorted_results),
            "results": sorted_results
        }
        
        return jsonify(result)
    
    # Chained transformations test
    elif test_type == 'chained_transformations':
        filter_value = parameters.get('filter_value', 100)
        agg_type = parameters.get('aggregation_type', 'sum')
        time_group = parameters.get('time_grouping', 'day')
        
        # Use the legacy transformation API
        transformations = [
            {"filter": {"type": "gt", "value": filter_value}},
            {"aggregation": agg_type, "time_grouping": time_group}
        ]
        
        result_metrics = mq.transform_metrics_to_dicts(metrics_store, transformations)
        
        result = {
            "test_name": "Chained transformations",
            "description": f"Filter metrics with value > {filter_value}, group by {time_group}, and calculate {agg_type}",
            "original_count": len(metrics_store),
            "result_count": len(result_metrics),
            "results": result_metrics
        }
        
        return jsonify(result)
    
    # Fluent API test
    elif test_type == 'fluent_api':
        filter_value = parameters.get('filter_value', 100)
        agg_type = parameters.get('aggregation_type', 'sum')
        time_group = parameters.get('time_grouping', 'day')
        
        # Use the fluent pipeline API
        pipeline = mq.create_pipeline(metrics_store)
        
        pipeline.greater_than(filter_value)
        
        if time_group == 'minute':
            pipeline.group_by_minute(aggregation=agg_type)
        elif time_group == 'hour':
            pipeline.group_by_hour(aggregation=agg_type)
        elif time_group == 'day':
            pipeline.group_by_day(aggregation=agg_type)
        
        result_metrics = pipeline.execute_to_dicts()
        
        result = {
            "test_name": "Fluent API",
            "description": f"Using the fluent pipeline API: filter > {filter_value}, group by {time_group}, {agg_type}",
            "original_count": len(metrics_store),
            "result_count": len(result_metrics),
            "fluent_api_example": f"pipeline.greater_than({filter_value}).group_by_{time_group}('{agg_type}').execute()",
            "results": result_metrics
        }
        
        return jsonify(result)
    
    else:
        return jsonify({"error": f"Unknown test type: {test_type}"}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
