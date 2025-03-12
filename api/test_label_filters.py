#!/usr/bin/env python3
"""
Test script for demonstrating label-aware metric transformations.

This script creates metrics with different labels and shows how to
filter and transform them using the integrated label handling approach.
"""

import sys
import os
import datetime

# Import directly from the Rust library to avoid circular imports
try:
    from metric_query_library import Metric, MetricPipeline
except ImportError as e:
    print(f"Error importing from metric_query_library: {e}")
    sys.exit(1)

def test_label_filtering():
    """Test the label filtering capabilities"""
    
    print("Creating test metrics with different labels...")
    
    # Create metrics with different labels
    metrics = [
        # CPU usage metrics (high values)
        Metric(value=80, timestamp=1614556800, label="cpu_usage"),
        Metric(value=85, timestamp=1614556860, label="cpu_usage"),
        Metric(value=90, timestamp=1614556920, label="cpu_usage"),
        
        # Memory usage metrics (medium values)
        Metric(value=50, timestamp=1614556800, label="memory_usage"),
        Metric(value=55, timestamp=1614556860, label="memory_usage"),
        Metric(value=60, timestamp=1614556920, label="memory_usage"),
        
        # Disk IO metrics (low values)
        Metric(value=20, timestamp=1614556800, label="disk_io"),
        Metric(value=25, timestamp=1614556860, label="disk_io"),
        Metric(value=30, timestamp=1614556920, label="disk_io"),
    ]
    
    # Print all metrics
    print("\nAll metrics:")
    for m in metrics:
        print(f"Label: {m.label}, Value: {m.value}, Timestamp: {m.timestamp}")
    
    # Test 1: Filter by exact label
    print("\nTest 1: Filter metrics with label 'cpu_usage'")
    pipeline = MetricPipeline(metrics)
    result = pipeline.filter_by_label("label_eq", "cpu_usage").execute()
    
    print("\nResult (cpu_usage metrics only):")
    for m in result:
        print(f"Label: {m.label}, Value: {m.value}, Timestamp: {m.timestamp}")
    
    # Test 2: Filter by multiple labels
    print("\nTest 2: Filter metrics with labels in ['cpu_usage', 'memory_usage']")
    pipeline = MetricPipeline(metrics)
    result = pipeline.filter_by_labels("label_in", ["cpu_usage", "memory_usage"]).execute()
    
    print("\nResult (cpu_usage and memory_usage metrics):")
    for m in result:
        print(f"Label: {m.label}, Value: {m.value}, Timestamp: {m.timestamp}")
    
    # Test 3: Filter by label and then apply a value filter
    print("\nTest 3: Filter cpu_usage metrics with value > 85")
    pipeline = MetricPipeline(metrics)
    # First filter by label
    pipeline = pipeline.filter_by_label("label_eq", "cpu_usage")
    # Then filter by value (using the filter method with gt type)
    pipeline = pipeline.filter("gt", 85)
    result = pipeline.execute()
    
    print("\nResult (cpu_usage metrics with value > 85):")
    for m in result:
        print(f"Label: {m.label}, Value: {m.value}, Timestamp: {m.timestamp}")
    
    # Test 4: Filter by label and then apply aggregation
    print("\nTest 4: Get average of memory_usage metrics")
    pipeline = MetricPipeline(metrics)
    # First filter by label
    pipeline = pipeline.filter_by_label("label_eq", "memory_usage")
    # Then aggregate
    pipeline = pipeline.aggregate("avg")
    result = pipeline.execute()
    
    print("\nResult (average of memory_usage metrics):")
    for m in result:
        print(f"Label: {m.label}, Value: {m.value}, Timestamp: {m.timestamp}")
    
    # Test 5: Filter by label and then group by time
    print("\nTest 5: Group disk_io metrics by minute and sum")
    pipeline = MetricPipeline(metrics)
    # First filter by label
    pipeline = pipeline.filter_by_label("label_eq", "disk_io")
    # Then group by minute and sum
    pipeline = pipeline.group_by_time("minute", "sum")
    result = pipeline.execute()
    
    print("\nResult (disk_io metrics grouped by minute and summed):")
    for m in result:
        print(f"Label: {m.label}, Value: {m.value}, Timestamp: {m.timestamp}")

if __name__ == "__main__":
    test_label_filtering()