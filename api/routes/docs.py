"""
Documentation routes for the Metric Query API.
"""
from flask import jsonify, Blueprint, send_from_directory, current_app
import os

# Create a Blueprint for the documentation routes
docs_bp = Blueprint('docs', __name__)

@docs_bp.route('/', methods=['GET'])
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
                    "signature": "filter_by_label('label_eq', label)",
                    "fluent_api": "filter_by_label('label_eq', label)",
                    "example": "pipeline.filter_by_label('label_eq', 'CPU_USAGE')",
                    "application": "Filters labeled metrics where label == 'CPU_USAGE'"
                },
                "label_in_filter": {
                    "description": "Filter by label set (labeled metrics only)",
                    "signature": "filter_by_labels('label_in', [label1, label2, ...])",
                    "fluent_api": "filter_by_labels('label_in', [label1, label2, ...])",
                    "example": "pipeline.filter_by_labels('label_in', ['CPU_USAGE', 'MEMORY_USAGE'])",
                    "application": "Filters labeled metrics where label is in the provided set"
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
                    "pipeline": [
                        {"operation": "filter_by_label", "label": "CPU_USAGE"},
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
            "github_repository": "https://github.com/rileyseaburg/metric-query-rs",
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

@docs_bp.route('/sphinx-docs/')
@docs_bp.route('/sphinx-docs/<path:path>')
def sphinx_docs(path='index.html'):
    """
    Serve Sphinx documentation
    ---
    tags:
      - Documentation
    description: |
      Sphinx-generated documentation for the Metric Query Library.
      
      This documentation provides comprehensive information on installing, using,
      and extending the Metric Query Library.
    produces:
      - text/html
    parameters:
      - name: path
        in: path
        type: string
        required: false
        default: index.html
        description: Path to the documentation file
    responses:
      200:
        description: HTML documentation
      404:
        description: Documentation file not found
    """
    docs_dir = os.path.join(current_app.root_path, '..', 'docs', '_build', 'html')
    return send_from_directory(docs_dir, path)