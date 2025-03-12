Usage
=====

This page provides examples and guidance on how to use the Metric Query Library.

Basic Usage
----------

Importing the Library
~~~~~~~~~~~~~~~~~~~~

To use the Metric Query Library in your Python code, import it as follows:

.. code-block:: python

    import metric_query_library as mql

Working with Metrics
~~~~~~~~~~~~~~~~~~~

The library provides functions for working with metrics data:

.. code-block:: python

    # Create a metric
    metric = {
        "name": "cpu_usage",
        "values": [10.5, 15.2, 12.8, 9.7, 11.3],
        "timestamps": [1615000000, 1615000060, 1615000120, 1615000180, 1615000240]
    }
    
    # Apply a transformation
    result = mql.transformations.moving_average(metric, window_size=3)
    
    print(result)

Labeled Metrics
--------------

Working with labeled metrics:

.. code-block:: python

    # Create a labeled metric
    labeled_metric = {
        "name": "http_requests",
        "values": [100, 150, 200, 175, 225],
        "timestamps": [1615000000, 1615000060, 1615000120, 1615000180, 1615000240],
        "labels": {
            "endpoint": "/api/users",
            "method": "GET",
            "status": "200"
        }
    }
    
    # Filter metrics by label
    filtered = mql.label_ops.filter_by_label(
        [labeled_metric], 
        {"endpoint": "/api/users"}
    )
    
    print(filtered)

Advanced Transformations
-----------------------

The library provides several advanced transformations:

.. code-block:: python

    # Rate calculation
    rate = mql.transformations.rate(metric)
    
    # Aggregation
    metrics = [metric1, metric2, metric3]
    sum_result = mql.transformations.sum(metrics)
    
    # Filtering
    filtered = mql.transformations.filter_values(
        metric, 
        lambda x: x > 10
    )

Using with Flask API
------------------

The library can be used with the included Flask API:

.. code-block:: python

    from flask import Flask, request, jsonify
    from metric_query_library import transformations
    
    app = Flask(__name__)
    
    @app.route('/api/metrics/transform', methods=['POST'])
    def transform_metric():
        data = request.json
        metric = data['metric']
        transform_type = data['transform_type']
        
        if transform_type == 'moving_average':
            window_size = data.get('window_size', 3)
            result = transformations.moving_average(metric, window_size)
        elif transform_type == 'rate':
            result = transformations.rate(metric)
        else:
            return jsonify({"error": f"Unknown transformation: {transform_type}"}), 400
            
        return jsonify({"result": result})
    
    if __name__ == '__main__':
        app.run(debug=True)

Performance Considerations
-------------------------

Since the core functionality is implemented in Rust, the library offers excellent performance. However, there are some considerations to keep in mind:

* Large datasets are processed efficiently due to Rust's performance
* The Python/Rust boundary crossing has some overhead, so it's best to batch operations when possible
* For very large datasets, consider using the streaming API to avoid memory issues

Error Handling
-------------

The library provides clear error messages for common issues:

.. code-block:: python

    try:
        result = mql.transformations.moving_average(metric, window_size=0)
    except ValueError as e:
        print(f"Error: {e}")  # Will print an error about invalid window size