"""
Swagger configuration for the Metric Query API.
"""

def get_swagger_template():
    """
    Returns the Swagger template for the API.
    """
    return {
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
            
            ## Documentation
            For comprehensive documentation, visit our [Sphinx Documentation](/sphinx-docs/) which provides detailed
            information on installation, usage, and the complete API reference.
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
            "LabelFilterOperation": {
                "type": "object",
                "description": "Label filter operation specification",
                "required": ["type", "value"],
                "properties": {
                    "type": {
                        "type": "string",
                        "description": "Label filter operator type",
                        "enum": ["label_eq", "label_in"],
                        "example": "label_eq"
                    },
                    "value": {
                        "oneOf": [
                            {
                                "type": "string",
                                "description": "Single label to match (for label_eq)"
                            },
                            {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "description": "List of labels to match (for label_in)"
                            }
                        ],
                        "example": "cpu_usage"
                    }
                }
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
                        "oneOf": [
                            {
                                "type": "string",
                                "description": "Label to filter metrics by (for exact matching)",
                                "example": "cpu_usage"
                            },
                            {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "description": "List of labels to filter metrics by (for matching any in set)",
                                "example": ["cpu_usage", "memory_usage"]
                            }
                        ]
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
            "description": "Metric Query Interface Documentation",
            "url": "/sphinx-docs/"
        },
        "x-additional-documentation": [
            {
                "name": "Sphinx Documentation",
                "description": "Comprehensive Sphinx documentation for the Metric Query Library",
                "url": "/sphinx-docs/"
            },
            {
                "name": "GitHub Repository",
                "description": "Source code and design documentation",
                "url": "https://github.com/rileyseaburg/metric-query-rs"
            }
        ]
    }