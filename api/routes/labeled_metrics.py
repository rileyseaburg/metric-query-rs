"""
Endpoints for labeled metrics operations.
"""
from datetime import datetime
from flask import request, jsonify, Blueprint
from metric_query_simplified import (
    LabeledMetric, create_pipeline, validate_labeled_metric, validate_transformations
)
from models.store import labeled_metrics_store

# Create a Blueprint for the labeled metrics routes
labeled_metrics_bp = Blueprint('labeled_metrics', __name__)

@labeled_metrics_bp.route('/', methods=['GET'])
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

@labeled_metrics_bp.route('/', methods=['POST'])
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
    metric = LabeledMetric(
        label=data['label'],
        value=int(data['value']),
        timestamp=int(data.get('timestamp', datetime.now().timestamp()))
    )
    
    labeled_metrics_store.append(metric)
    return jsonify({"status": "success", "id": len(labeled_metrics_store) - 1}), 201

@labeled_metrics_bp.route('/transform', methods=['POST'])
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
                    oneOf:
                      - type: string
                        description: Label to filter metrics by (for exact matching)
                        example: cpu_usage
                      - type: array
                        items:
                          type: string
                        description: List of labels to filter metrics by (for matching any in set)
                        example: [cpu_usage, memory_usage]
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
        
    # Create a pipeline with the labeled metrics directly using our new label-aware transformations
    pipeline = create_pipeline(labeled_metrics_store)
    
    # Apply transformations in sequence
    for transform_data in data['transformations']:
        # Apply label filter if present
        if 'label_filter' in transform_data:
            label_filter = transform_data['label_filter']
            if isinstance(label_filter, str):
                # Single label filter (exact match)
                pipeline.filter_by_label('label_eq', label_filter)
            elif isinstance(label_filter, list):
                # Multiple label filter (match any in set)
                pipeline.filter_by_labels('label_in', label_filter)
            else:
                return jsonify({"error": f"Invalid label_filter format: {label_filter}"}), 400
        
        # Apply value filter if present
        if 'filter' in transform_data:
            filter_data = transform_data['filter']
            pipeline.filter(type=filter_data['type'], value=filter_data['value'])
        
        # Apply aggregation and/or time grouping
        if 'aggregation' in transform_data and 'time_grouping' in transform_data:
            pipeline.group_by_time(transform_data['time_grouping'], transform_data['aggregation'])
        elif 'aggregation' in transform_data:
            pipeline.aggregate(transform_data['aggregation'])
    
    result = pipeline.execute_to_dicts()
    return jsonify(result)

@labeled_metrics_bp.route('/pipeline', methods=['POST'])
def labeled_pipeline_transform():
    """
    Transform labeled metrics using fluent pipeline API
    ---
    tags:
      - Transformations
    description: |
      Labeled Metrics Pipeline API
      
      This endpoint extends the pipeline API to work with labeled metrics (metrics that have a category/label attached).
      It's particularly useful for junior data engineers who need to analyze metrics across different categories.
      
      How Labeled Metrics Work:
      
      1. Labels vs. Regular Metrics: Labeled metrics contain an additional "label" field that categorizes the metric (e.g., "CPU_USAGE", "MEMORY_USAGE")
      2. Two-Stage Processing: First, you filter by labels, then you apply regular transformations
      3. Common Pattern: Filter to specific metric types, then analyze trends or patterns within those types
      
      Request Format:
      
      {
        "label_operations": [
          {"operation": "filter_by_label", "label": "CPU_USAGE"}
        ],
        "pipeline": [
          {"operation": "greater_than", "value": 50},
          {"operation": "group_by_hour", "aggregation": "avg"}
        ]
      }
      
      Common Use Cases:
      
      Analyzing CPU Usage Patterns:
      {
        "label_operations": [
          {"operation": "filter_by_label", "label": "CPU_USAGE"}
        ],
        "pipeline": [
          {"operation": "group_by_hour", "aggregation": "avg"}
        ]
      }
      This calculates hourly average CPU usage.
      
      Finding Memory Usage Spikes:
      {
        "label_operations": [
          {"operation": "filter_by_label", "label": "MEMORY_USAGE"}
        ],
        "pipeline": [
          {"operation": "group_by_hour", "aggregation": "max"}
        ]
      }
      This identifies peak memory usage per hour.
      
      Comparing Multiple Metrics:
      {
        "label_operations": [
          {"operation": "filter_by_labels", "labels": ["CPU_USAGE", "MEMORY_USAGE"]}
        ],
        "pipeline": [
          {"operation": "greater_than", "value": 80},
          {"operation": "group_by_day", "aggregation": "count"}
        ]
      }
      This counts how many high-usage events (>80%) occur each day for both CPU and memory.
      
      Label Operations:
      
      - filter_by_label: Keep metrics with a specific label - label: String 
      - filter_by_labels: Keep metrics with any of these labels - labels: Array of strings
      
      Pipeline Operations:
      
      The same pipeline operations from /metrics/pipeline are available for labeled metrics.
      
      Working with Labels - Best Practices:
      
      1. Filter First: Always filter by label first to reduce the dataset size before applying transformations
      2. Consistent Labels: Ensure your label names are consistent (e.g., "CPU_USAGE" vs "cpu_usage")
      3. Related Labels: When using multiple labels, make sure they're logically related for meaningful analysis
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            pipeline:
              type: array
              description: Pipeline operations to apply to labeled metrics
              items:
                type: object
                required:
                  - operation
                properties:
                  operation:
                    type: string
                    enum: [filter, greater_than, less_than, equal_to,
                           aggregate, sum, average,
                           group_by, group_by_minute, group_by_hour, group_by_day,
                           filter_by_label, filter_by_labels]
                    description: Operation to apply
                  type:
                    type: string
                    description: Type for filter or aggregation operations
                  value:
                    type: integer
                    description: Value for filter operations
                  label:
                    type: string
                    description: Label to filter by (for filter_by_label)
                  labels:
                    type: array
                    items:
                      type: string
                    description: Labels to filter by (for filter_by_labels)
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
    
    if not data:
        return jsonify({"error": "Empty request data"}), 400
    
    # Create a pipeline directly with labeled metrics
    try:
        pipeline = create_pipeline(labeled_metrics_store)
        
        # Apply pipeline operations if any
        if 'pipeline' in data and isinstance(data['pipeline'], list):
            for i, step in enumerate(data['pipeline']):
                if 'operation' not in step:
                    return jsonify({"error": f"Missing operation in pipeline step {i}"}), 400
                
                operation = step['operation']
                
                try:
                    if operation == 'filter_by_label':
                        if 'label' not in step:
                            return jsonify({"error": f"filter_by_label operation requires label (step {i})"}), 400
                        pipeline.filter_by_label('label_eq', step['label'])
                    
                    elif operation == 'filter_by_labels':
                        if 'labels' not in step or not isinstance(step['labels'], list):
                            return jsonify({"error": f"filter_by_labels operation requires labels array (step {i})"}), 400
                        pipeline.filter_by_labels('label_in', step['labels'])
                    
                    elif operation == 'filter':
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