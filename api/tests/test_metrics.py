import pytest
import sys
import os
from datetime import datetime, timedelta
import time

# Add the parent directory to sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import metric_query_library as mq
from metric_query_library.type_defs import (
    FilterSpec, TransformationSpec, MetricDict, LabeledMetricDict
)

# Test fixtures
@pytest.fixture
def sample_metrics():
    """Create a set of sample metrics for testing"""
    now = int(datetime.now().timestamp())
    
    # Create metrics with different times and values
    return [
        mq.Metric(value=10, timestamp=now - 3600),  # 1 hour ago
        mq.Metric(value=20, timestamp=now - 7200),  # 2 hours ago
        mq.Metric(value=30, timestamp=now - 10800),  # 3 hours ago
        mq.Metric(value=40, timestamp=now - 3600 * 24),  # 1 day ago
        mq.Metric(value=50, timestamp=now - 3600 * 24 * 2),  # 2 days ago
    ]

@pytest.fixture
def sample_labeled_metrics():
    """Create a set of sample labeled metrics for testing"""
    now = int(datetime.now().timestamp())
    
    # Create metrics with different labels, times, and values
    return [
        mq.LabeledMetric(label="cpu", value=10, timestamp=now - 3600),
        mq.LabeledMetric(label="memory", value=20, timestamp=now - 3600),
        mq.LabeledMetric(label="cpu", value=30, timestamp=now - 7200),
        mq.LabeledMetric(label="memory", value=40, timestamp=now - 7200),
        mq.LabeledMetric(label="disk", value=50, timestamp=now - 10800),
    ]

# Basic tests for metrics
def test_create_metric():
    """Test creating a metric"""
    now = int(datetime.now().timestamp())
    metric = mq.Metric(value=42, timestamp=now)
    
    assert metric.value == 42
    assert metric.timestamp == now

def test_create_labeled_metric():
    """Test creating a labeled metric"""
    now = int(datetime.now().timestamp())
    metric = mq.LabeledMetric(label="cpu", value=42, timestamp=now)
    
    assert metric.label == "cpu"
    assert metric.value == 42
    assert metric.timestamp == now

# Filter tests
def test_filter_greater_than(sample_metrics):
    """Test filtering metrics with value greater than a threshold"""
    pipeline = mq.create_pipeline(sample_metrics)
    result = pipeline.greater_than(25).execute()
    
    assert len(result) == 3
    assert all(m.value > 25 for m in result)

def test_filter_less_than(sample_metrics):
    """Test filtering metrics with value less than a threshold"""
    pipeline = mq.create_pipeline(sample_metrics)
    result = pipeline.less_than(25).execute()
    
    assert len(result) == 2
    assert all(m.value < 25 for m in result)

def test_filter_equal_to(sample_metrics):
    """Test filtering metrics with value equal to a threshold"""
    pipeline = mq.create_pipeline(sample_metrics)
    result = pipeline.equal_to(30).execute()
    
    assert len(result) == 1
    assert result[0].value == 30

# Aggregation tests
def test_sum_aggregation(sample_metrics):
    """Test sum aggregation of metric values"""
    pipeline = mq.create_pipeline(sample_metrics)
    result = pipeline.sum().execute()
    
    assert len(result) == 1
    assert result[0].value == sum(m.value for m in sample_metrics)

def test_average_aggregation(sample_metrics):
    """Test average aggregation of metric values"""
    pipeline = mq.create_pipeline(sample_metrics)
    result = pipeline.average().execute()
    
    expected_avg = sum(m.value for m in sample_metrics) // len(sample_metrics)
    assert len(result) == 1
    assert result[0].value == expected_avg

# Time grouping tests
def test_group_by_hour(sample_metrics):
    """Test grouping metrics by hour with sum aggregation"""
    pipeline = mq.create_pipeline(sample_metrics)
    result = pipeline.group_by_hour(aggregation="sum").execute()
    
    # Should have at most 5 groups (one for each unique hour in sample data)
    assert 1 <= len(result) <= 5
    
    # Sum of all values should be the same before and after grouping
    original_sum = sum(m.value for m in sample_metrics)
    grouped_sum = sum(m.value for m in result)
    assert original_sum == grouped_sum

def test_group_by_day(sample_metrics):
    """Test grouping metrics by day with sum aggregation"""
    pipeline = mq.create_pipeline(sample_metrics)
    result = pipeline.group_by_day(aggregation="sum").execute()
    
    # Should have at most 3 groups (one for each unique day in sample data)
    assert 1 <= len(result) <= 3
    
    # Sum of all values should be the same before and after grouping
    original_sum = sum(m.value for m in sample_metrics)
    grouped_sum = sum(m.value for m in result)
    assert original_sum == grouped_sum

# Chained transformations tests
def test_filter_then_aggregate(sample_metrics):
    """Test filtering metrics then aggregating results"""
    pipeline = mq.create_pipeline(sample_metrics)
    result = pipeline.greater_than(20).sum().execute()
    
    assert len(result) == 1
    
    # Sum should include only values > 20
    expected_sum = sum(m.value for m in sample_metrics if m.value > 20)
    assert result[0].value == expected_sum

def test_filter_then_group_by_hour(sample_metrics):
    """Test filtering metrics then grouping by hour"""
    pipeline = mq.create_pipeline(sample_metrics)
    result = pipeline.greater_than(20).group_by_hour().execute()
    
    # Grouped metrics should all have values > 20
    filtered_metrics = [m for m in sample_metrics if m.value > 20]
    assert len(result) <= len(filtered_metrics)
    
    # Sum of grouped values should equal sum of filtered values
    filtered_sum = sum(m.value for m in filtered_metrics)
    grouped_sum = sum(m.value for m in result)
    assert filtered_sum == grouped_sum

# Label operations tests
def test_filter_by_label(sample_labeled_metrics):
    """Test filtering labeled metrics by label"""
    processor = mq.create_labeled_processor(sample_labeled_metrics)
    filtered = processor.filter_by_label("cpu").get_metrics()
    
    assert len(filtered) == 2
    assert all(m.label == "cpu" for m in filtered)

def test_filter_by_labels(sample_labeled_metrics):
    """Test filtering labeled metrics by multiple labels"""
    processor = mq.create_labeled_processor(sample_labeled_metrics)
    filtered = processor.filter_by_labels(["cpu", "memory"]).get_metrics()
    
    assert len(filtered) == 4
    assert all(m.label in ["cpu", "memory"] for m in filtered)

def test_label_filter_with_pipeline(sample_labeled_metrics):
    """Test filtering by label then applying a transformation pipeline"""
    processor = mq.create_labeled_processor(sample_labeled_metrics)
    result = (
        processor
        .filter_by_label("cpu")
        .to_pipeline()
        .sum()
        .execute()
    )
    
    assert len(result) == 1
    
    # Sum should include only cpu metrics
    cpu_metrics = [m for m in sample_labeled_metrics if m.label == "cpu"]
    expected_sum = sum(m.value for m in cpu_metrics)
    assert result[0].value == expected_sum

# Legacy API tests
def test_legacy_transform_api(sample_metrics):
    """Test the legacy transform API for backward compatibility"""
    # Create transformations in the legacy format
    transformations = [
        {"filter": {"type": "gt", "value": 20}},
        {"aggregation": "sum"}
    ]
    
    result = mq.transform_metrics(sample_metrics, transformations)
    
    assert len(result) == 1
    
    # Result should be sum of values > 20
    expected_sum = sum(m.value for m in sample_metrics if m.value > 20)
    assert result[0].value == expected_sum

def test_transform_to_dicts(sample_metrics):
    """Test transforming metrics and converting results to dictionaries"""
    transformations = [
        {"filter": {"type": "gt", "value": 20}},
        {"aggregation": "sum"}
    ]
    
    result = mq.transform_metrics_to_dicts(sample_metrics, transformations)
    
    assert len(result) == 1
    assert "value" in result[0]
    assert "timestamp" in result[0]
    
    # Result should be sum of values > 20
    expected_sum = sum(m.value for m in sample_metrics if m.value > 20)
    assert result[0]["value"] == expected_sum

# Integration tests
def test_complex_pipeline(sample_metrics):
    """Test a complex pipeline with multiple operations"""
    # Get current timestamp
    now = int(datetime.now().timestamp())
    
    # Create a pipeline that:
    # 1. Filters metrics from the last day
    # 2. Groups them by hour
    # 3. Filters groups with sum > 25
    pipeline = mq.create_pipeline(sample_metrics)
    result = (
        pipeline
        .greater_than(now - 24 * 3600)  # From last 24 hours
        .group_by_hour()
        .greater_than(25)  # Only hours with sum > 25
        .execute()
    )
    
    # Manually verify the pipeline logic
    last_day_metrics = [m for m in sample_metrics if m.timestamp > now - 24 * 3600]
    
    # Convert result to dictionary for easier comparison
    result_dict = {}
    for m in result:
        result_dict[m.timestamp] = m.value
    
    # Verify each hour in the result meets our criteria
    for timestamp, value in result_dict.items():
        assert value > 25  # Verify the filter worked