"""
Test endpoints for demonstrating the API's functionality.
"""
from datetime import datetime
import json
from flask import jsonify, Blueprint, request
from utils.utils import load_test_data
from metric_query_simplified import create_pipeline, transform_metrics_to_dicts
from models.store import metrics_store

# Create a Blueprint for the test routes
tests_bp = Blueprint('tests', __name__)

@tests_bp.route('/', methods=['POST'])
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
            test_data = load_test_data()
            metrics_store = test_data["metrics"]
        except Exception as e:
            return jsonify({"error": f"Error loading test data: {str(e)}"}), 500
    
    test_type = data['test_type']
    parameters = data.get('parameters', {})
    
    # Basic filtering test
    if test_type == 'basic_filtering':
        filter_value = parameters.get('filter_value', 500)
        
        # Use fluent pipeline API
        pipeline = create_pipeline(metrics_store)
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
        pipeline = create_pipeline(metrics_store)
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
        pipeline = create_pipeline(metrics_store)
        
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
        pipeline = create_pipeline(metrics_store)
        
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
        
        result_metrics = transform_metrics_to_dicts(metrics_store, transformations)
        
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
        pipeline = create_pipeline(metrics_store)
        
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