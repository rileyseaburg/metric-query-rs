"""
Test script to verify the metric-query-library is properly installed and accessible.
"""
import sys
import os
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print("Python path:")
for p in sys.path:
    print(f"  - {p}")

print("\nAttempting to import metric_query_library...")
try:
    import metric_query_library
    print(f"✓ Successfully imported metric_query_library - version: {metric_query_library.__version__}")
    
    # Test creating a metric
    print("\nCreating a metric...")
    metric = metric_query_library.Metric(value=100, timestamp=1678901234)
    print(f"Created metric: value={metric.value}, timestamp={metric.timestamp}")
    
    # Test creating a labeled metric
    print("\nCreating a labeled metric...")
    labeled_metric = metric_query_library.LabeledMetric(label="test", value=200, timestamp=1678901234)
    print(f"Created labeled metric: label={labeled_metric.label}, value={labeled_metric.value}, timestamp={labeled_metric.timestamp}")
    
    # Test creating a pipeline
    print("\nCreating a pipeline...")
    pipeline = metric_query_library.create_pipeline([metric])
    print("Pipeline created successfully")
    
    # Test pipeline functionality
    print("\nTesting pipeline transformations...")
    result = pipeline.greater_than(50).execute_to_dicts()
    print(f"Transformation result: {result}")
    
except ImportError as e:
    print(f"✗ Failed to import metric_query_library: {e}")
except Exception as e:
    print(f"✗ Error while using metric_query_library: {e}")
    import traceback
    traceback.print_exc()

print("\nTest complete.")