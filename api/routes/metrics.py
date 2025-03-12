"""
Endpoints for basic metrics operations.
"""
from datetime import datetime
from flask import request, jsonify, Blueprint
from metric_query_simplified import (
    Metric, transform_metrics_to_dicts, create_pipeline,
    validate_metric, validate_transformations
)
from models.store import metrics_store

# Create a Blueprint for the metrics routes
metrics_bp = Blueprint('metrics', __name__)

@metrics_bp.route('/', methods=['GET'])
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

@metrics_bp.route('/', methods=['POST'])
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
    metric = Metric(
        value=int(data['value']),
        timestamp=int(data.get('timestamp', datetime.now().timestamp()))
    )
    
    metrics_store.append(metric)
    return jsonify({"status": "success", "id": len(metrics_store) - 1}), 201

@metrics_bp.route('/transform', methods=['POST'])
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
    result = transform_metrics_to_dicts(metrics_store, data['transformations'])
    return jsonify(result)

@metrics_bp.route('/pipeline', methods=['POST'])
def pipeline_transform():
    """
    Transform metrics using fluent pipeline API
    ---
    tags:
      - Transformations
    description: |
      Metric Pipeline Transformation API
      
      This endpoint allows you to transform time-series metrics using a fluent pipeline interface. 
      It's designed to help junior data engineers apply complex transformations with minimal code.
      
      How Pipeline Transformations Work:
      
      1. The Pipeline Concept: Think of a pipeline as a series of data processing steps. Each metric flows through these steps in sequence.
      2. Sequential Processing: Operations are applied in the exact order you specify them in the pipeline array.
      3. Transformation Flow: Metrics → Filter Operations → Aggregation Operations → Time Grouping Operations → Results
      
      Request Format:
      
      {
        "pipeline": [
          {"operation": "greater_than", "value": 50},
          {"operation": "group_by_hour", "aggregation": "sum"}
        ]
      }
      
      Common Use Cases:
      
      Filtering High-Value Metrics:
      {
        "pipeline": [
          {"operation": "greater_than", "value": 100}
        ]
      }
      This filters your metrics to only include values greater than 100.
      
      Finding Hourly Averages:
      {
        "pipeline": [
          {"operation": "group_by_hour", "aggregation": "avg"}
        ]
      }
      This groups metrics by hour and calculates the average value for each hour.
      
      Daily Max Values Above Threshold:
      {
        "pipeline": [
          {"operation": "greater_than", "value": 50},
          {"operation": "group_by_day", "aggregation": "max"}
        ]
      }
      This filters metrics to those above 50, then finds the maximum value for each day.
      
      Available Operations:
      
      Filter Operations:
      - filter: Generic filter - type: One of (gt, lt, ge, le, eq), value: Number to compare against
      - greater_than: Value > threshold - value: Number
      - less_than: Value < threshold - value: Number 
      - equal_to: Value = threshold - value: Number
      
      Aggregation Operations:
      - aggregate: Generic aggregation - type: One of (sum, avg, min, max)
      - sum: Sum all values - No parameters
      - average: Average of values - No parameters
      
      Time Grouping Operations:
      - group_by: Generic time grouping - time_grouping: One of (minute, hour, day), aggregation: One of (sum, avg, min, max)
      - group_by_minute: Group by minute - aggregation: Aggregation type (default: sum)
      - group_by_hour: Group by hour - aggregation: Aggregation type (default: sum)
      - group_by_day: Group by day - aggregation: Aggregation type (default: sum)
      
      Common Mistakes to Avoid:
      
      1. Order Matters: Placing a grouping operation before filtering will give different results than filtering first.
      2. Multiple Aggregations: You can't chain multiple aggregations together (e.g., sum, then avg).
      3. Time Unit Selection: Choose appropriate time units - minute grouping on months of data will return many data points.
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
        # Create a pipeline with the metrics
        pipeline = create_pipeline(metrics_store)
        
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
            except Exception as e:
                import logging
                logging.error(f"Unexpected error in pipeline step {i}: {str(e)}")
                return jsonify({"error": f"Unexpected error in pipeline step {i}: {str(e)}"}), 500
        
        # Execute the pipeline and return results
        try:
            result = pipeline.execute_to_dicts()
            return jsonify(result)
        except Exception as e:
            import logging
            logging.error(f"Error executing pipeline: {str(e)}")
            # Fallback to returning original metrics
            result = [{'value': m.value, 'timestamp': m.timestamp} for m in metrics_store]
            return jsonify(result)
    
    except Exception as e:
        import logging
        logging.error(f"Error processing pipeline: {str(e)}")
        return jsonify({"error": f"Error processing pipeline: {str(e)}"}), 500