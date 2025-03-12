#!/usr/bin/env python
"""
Test Harness for Metric Query Interface

This script demonstrates how the Metric Query Interface might be used and
provides test cases to validate the implementation.
"""

import json
import datetime
import metric_query_library as mq
from typing import List, Dict, Any, Union

class FilterType:
    VALUE = "value"
    TIMESTAMP = "timestamp"
    LABEL = "label"

class FilterOperator:
    EQ = "eq"
    GT = "gt"
    LT = "lt"
    GTE = "gte"
    LTE = "lte"
    NE = "ne"

class AggregationType:
    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    COUNT = "count"

class TimeGrouping:
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"

class GroupByType:
    TIME = "time"
    LABEL = "label"

# Helper functions to convert JSON to Metric objects
def json_to_basic_metrics(data: List[Dict[str, Any]]) -> List[mq.Metric]:
    """Convert JSON data to basic Metric objects"""
    return [mq.Metric(value=item["value"], timestamp=item["timestamp"] // 1000) for item in data]

def json_to_labeled_metrics(data: List[Dict[str, Any]]) -> List:
    """Convert JSON data to LabeledMetric objects"""
    return [mq.LabeledMetric(label=item["label"], value=item["value"], timestamp=item["timestamp"] // 1000) for item in data]

# Helper function to create transformations
def create_filter_transformation(filter_type: str, operator: str, value: Any) -> mq.Transformation:
    """Create a filter transformation"""
    transformation = mq.Transformation()
    if filter_type == FilterType.VALUE:
        if operator == FilterOperator.GT:
            transformation.filter = mq.Filter("gt", value)
        elif operator == FilterOperator.LT:
            transformation.filter = mq.Filter("lt", value)
        elif operator == FilterOperator.GTE:
            transformation.filter = mq.Filter("ge", value)
        elif operator == FilterOperator.LTE:
            transformation.filter = mq.Filter("le", value)
        elif operator == FilterOperator.EQ:
            transformation.filter = mq.Filter("eq", value)
            transformation.filter = mq.Filter.Equal(value=value)
    
    return transformation

def create_aggregation_transformation(agg_type: str, time_grouping: str = None) -> mq.Transformation:
    """Create an aggregation transformation"""
    transformation = mq.Transformation()
    
    if agg_type == AggregationType.SUM:
        transformation.aggregation = mq.Aggregation("sum")
    elif agg_type == AggregationType.AVG:
        transformation.aggregation = mq.Aggregation("avg")
    elif agg_type == AggregationType.MIN:
        transformation.aggregation = mq.Aggregation("min")
    elif agg_type == AggregationType.MAX:
        transformation.aggregation = mq.Aggregation("max")
    
    if time_grouping:
        if time_grouping == TimeGrouping.HOUR:
            transformation.time_grouping = mq.TimeGrouping("hour")
        elif time_grouping == TimeGrouping.MINUTE:
            transformation.time_grouping = mq.TimeGrouping("minute")
        elif time_grouping == TimeGrouping.DAY:
            transformation.time_grouping = mq.TimeGrouping("day")
    
    return transformation

# Convert metrics to a human-readable format for display
def format_metrics(metrics: List[mq.Metric]) -> List[Dict[str, Any]]:
    """Convert metrics to a readable format"""
    result = []
    for metric in metrics:
        time_str = datetime.datetime.fromtimestamp(metric.timestamp).strftime('%Y-%m-%d %H:%M:%S')
        result.append({
            "value": metric.value,
            "timestamp": time_str
        })
    return result

# Test cases

def test_basic_filtering(metrics: List[mq.Metric]):
    """
    TEST CASE 1: Basic filtering
    Filter metrics to only include those with values greater than 500
    """
    transformation = create_filter_transformation(FilterType.VALUE, FilterOperator.GT, 500)
    filtered = mq.transform(metrics, [transformation])
    
    print("TEST CASE 1: Basic filtering")
    print(f"Original count: {len(metrics)}")
    print(f"Filtered count: {len(filtered)}")
    print("Sample filtered metrics:", format_metrics(filtered[:3]))
    print("\n")
    
    return filtered

def test_time_filtering(metrics: List[mq.Metric]):
    """
    TEST CASE 2: Time-based filtering
    Filter metrics to only include those from the past 24 hours
    """
    # Convert 24 hours ago to a timestamp
    one_day_ago = int(datetime.datetime.now().timestamp()) - (24 * 60 * 60)
    
    transformation = create_filter_transformation(FilterType.TIMESTAMP, FilterOperator.GTE, one_day_ago)
    filtered = mq.transform(metrics, [transformation])
    
    print("TEST CASE 2: Time-based filtering")
    print(f"Original count: {len(metrics)}")
    print(f"Filtered count: {len(filtered)}")
    print("Sample filtered metrics:", format_metrics(filtered[:3]))
    print("\n")
    
    return filtered
def test_aggregation(metrics: List[mq.Metric]):
    """
    TEST CASE 3: Aggregation
    Calculate the average value of all metrics
    """
    transformation = create_aggregation_transformation(AggregationType.AVG)
    result = mq.transform(metrics, [transformation])
    
    print("TEST CASE 3: Aggregation")
    print(f"Original count: {len(metrics)}")
    if len(result) == 1:
        # Print as a single aggregated value
        print(f"Average value: {result[0].value}")
    else:
        # Fallback in case something went wrong
        print(f"Result count: {len(result)}")
        print("Result metrics:", format_metrics(result[:3]))
    print("\n")
    
    return result
    return result

def test_time_grouping(metrics: List[mq.Metric]):
    """
    TEST CASE 4: Time grouping
    Group metrics by hour and calculate the average value for each hour
    """
    transformation = create_aggregation_transformation(AggregationType.AVG, TimeGrouping.HOUR)
    result = mq.transform(metrics, [transformation])
    
    print("TEST CASE 4: Time grouping")
    print(f"Original count: {len(metrics)}")
    print(f"Result count: {len(result)}")
    print("Sample grouped results:", format_metrics(result[:3]))
    print("\n")
    
    return result

def test_chained_transformations(metrics: List[mq.Metric]):
    """
    TEST CASE 5: Chaining multiple transformations
    Filter metrics with value > 100, group by day, and calculate sum for each day
    """
    filter_transformation = create_filter_transformation(FilterType.VALUE, FilterOperator.GT, 100)
    agg_transformation = create_aggregation_transformation(AggregationType.SUM, TimeGrouping.DAY)
    
    # Chain transformations
    result = mq.transform(metrics, [filter_transformation, agg_transformation])
    
    print("TEST CASE 5: Chained transformations")
    print(f"Original count: {len(metrics)}")
    print(f"Result count: {len(result)}")
    print("Sample results:", format_metrics(result[:3]))
    print("\n")
    
    return result

# Main execution
if __name__ == "__main__":
    # Load test data
    try:
        with open("test_data.json", "r") as f:
            test_data = json.load(f)
    except FileNotFoundError:
        print("Could not find test_data.json. Please run generate_test_data.py first.")
        exit(1)

    # Convert JSON data to Metric objects
    basic_metrics = json_to_basic_metrics(test_data["basicMetrics"])
    
    # Run test cases
    test_basic_filtering(basic_metrics)
    test_time_filtering(basic_metrics)
    test_aggregation(basic_metrics)
    test_time_grouping(basic_metrics)
    test_chained_transformations(basic_metrics)
    
    print("All test cases completed.")
