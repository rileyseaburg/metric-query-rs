"""
Endpoints for extending the API with custom plugins.
"""
from flask import jsonify, Blueprint, request

# Create a Blueprint for the extensions routes
extensions_bp = Blueprint('extensions', __name__)

@extensions_bp.route('/transformations/filters', methods=['POST'])
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

@extensions_bp.route('/transformations/aggregations', methods=['POST'])
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