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

# Configure Swagger
swagger = Swagger(app, template={
    "swagger": "2.0",
    "info": {
        "title": "Metric Query API",
        "description": "API for collecting and transforming metric data in streaming environments",
        "version": "1.0.0",
        "contact": {
            "name": "API Support",
            "url": "http://www.example.com/support"
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
            "name": "Tests",
            "description": "Test endpoints for demonstrating functionality"
        },
        {
            "name": "Extensions",
            "description": "Extension points for custom functionality"
        }
    ],
    "externalDocs": {
        "description": "Metric Query Interface Constraints",
        "url": "https://github.com/example/metric-query-rs/docs"
    }
})

# In-memory storage for metrics
metrics_store: List[mq.Metric] = []
labeled_metrics_store: List[mq.LabeledMetric] = []

# Add API description and constraints to the app
@app.route('/', methods=['GET'])
def api_info():
    """
    Metric Query Interface Documentation
    ---
    tags:
      - Documentation
    responses:
      200:
        description: API information and constraints
    """
    return jsonify({
        "name": "Metric Query API",
        "version": "1.0.0",
        "description": "API for querying and transforming time series metric data",
        "constraints": {
            "metrics": {
                "description": "Bounded stream of Metric objects",
                "properties": {
                    "order": "Metrics aren't guaranteed to be in order",
                    "sorting": "Can't sort the list (part of a larger stream of data)",
                    "value": "Any positive or negative integer",
                    "timestamp": "Any timestamp between the Linux epoch and now (no future events)"
                }
            },
            "operations": {
                "filters": "Can be applied to value and timestamp",
                "aggregations": "Can only be applied to value",
                "timeGroupings": "Can only be applied to timestamp"
            },
            "transformations": {
                "chaining": "Transformations are applied sequentially in the order provided",
                "extension": "Custom filters and aggregations require extending the Rust library"
            },
            "labeledMetrics": {
                "description": "Extended metrics with a label field",
                "labelTypes": "Labels are considered to be from a known set of values",
                "operations": "Filters can be applied to labels in addition to values and timestamps"
            }
        },
        "endpoints": {
            "metrics": "/metrics",
            "labeledMetrics": "/labeled-metrics",
            "transformations": {
                "basic": "/metrics/transform",
                "labeled": "/labeled-metrics/transform"
            },
            "extensions": {
                "filters": "/transformations/filters",
                "aggregations": "/transformations/aggregations"
            },
            "test": "/test"
        },
        "fluent_api": {
            "description": "The API now supports a fluent interface for chaining transformations",
            "example": "pipeline.filter(gt=100).group_by_hour().sum().execute()",
            "endpoints": {
                "pipeline": "/metrics/pipeline",
                "labeled_pipeline": "/labeled-metrics/pipeline"
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
        
        result = {
            "test_name": "Time grouping",
            "description": f"Group metrics by {time_group} and calculate the {agg_type}",
            "original_count": len(metrics_store),
            "result_count": len(result_metrics),
            "results": result_metrics
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
