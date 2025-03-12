#!/usr/bin/env python
"""
Test Data Generator for Metric Query Interface Problem

This script generates test data for the Metric Query Interface design problem.
It creates two datasets:
1. A basic dataset with Metric(value, timestamp) objects
2. An extended dataset with Metric(label, value, timestamp) objects

The data is designed to test various aspects of the interface including:
- Out-of-order timestamps
- Positive and negative values
- Data spanning different time periods
- Various labels (for the extended version)
"""

import random
import json
import datetime
import time
from typing import List, Dict, Any

# Helper function to generate a random integer between min and max (inclusive)
def get_random_int(min_val: int, max_val: int) -> int:
    return random.randint(min_val, max_val)

# Helper function to generate a random timestamp between start and end dates
def get_random_timestamp(start: datetime.datetime, end: datetime.datetime) -> int:
    delta = end - start
    int_delta = delta.total_seconds() * 1000  # milliseconds
    random_ms = random.randint(0, int(int_delta))
    random_date = start + datetime.timedelta(milliseconds=random_ms)
    return int(random_date.timestamp() * 1000)  # Unix timestamp in milliseconds

# Generate basic metrics (value, timestamp)
def generate_basic_metrics(count: int) -> List[Dict[str, Any]]:
    metrics = []
    
    # Define date range (from one month ago to now)
    now = datetime.datetime.now()
    one_month_ago = now - datetime.timedelta(days=30)
    
    for _ in range(count):
        timestamp = get_random_timestamp(one_month_ago, now)
        value = get_random_int(-100, 1000)  # Mix of positive and negative values
        
        metrics.append({
            "value": value,
            "timestamp": timestamp
        })
    
    return metrics

# Generate extended metrics (label, value, timestamp)
def generate_extended_metrics(count: int) -> List[Dict[str, Any]]:
    metrics = []
    labels = ["API_LATENCY", "DB_CONNECTIONS", "MEMORY_USAGE", "CPU_USAGE", "NETWORK_THROUGHPUT"]
    
    # Define date range (from one month ago to now)
    now = datetime.datetime.now()
    one_month_ago = now - datetime.timedelta(days=30)
    
    for _ in range(count):
        timestamp = get_random_timestamp(one_month_ago, now)
        value = get_random_int(-100, 1000)
        label = random.choice(labels)
        
        metrics.append({
            "label": label,
            "value": value,
            "timestamp": timestamp
        })
    
    return metrics

# Generate special test cases
def generate_special_case_metrics() -> List[Dict[str, Any]]:
    now = datetime.datetime.now()
    
    return [
        # Edge case: very old timestamp (Unix epoch)
        {"value": 42, "timestamp": 0},  # January 1, 1970, 00:00:00 UTC
        
        # Edge case: exactly one hour ago
        {"value": 100, "timestamp": int((now - datetime.timedelta(hours=1)).timestamp() * 1000)},
        
        # Edge case: repeated timestamps with different values
        {"value": 50, "timestamp": int((now - datetime.timedelta(hours=2)).timestamp() * 1000)},
        {"value": 51, "timestamp": int((now - datetime.timedelta(hours=2)).timestamp() * 1000)},
        
        # Edge case: extreme values
        {"value": 9007199254740991, "timestamp": int((now - datetime.timedelta(seconds=1)).timestamp() * 1000)},  # MAX_SAFE_INTEGER in JS
        {"value": -9007199254740991, "timestamp": int((now - datetime.timedelta(seconds=2)).timestamp() * 1000)},  # MIN_SAFE_INTEGER in JS
        
        # Edge case: zero value
        {"value": 0, "timestamp": int((now - datetime.timedelta(seconds=3)).timestamp() * 1000)}
    ]

# Generate extended special test cases
def generate_extended_special_case_metrics() -> List[Dict[str, Any]]:
    now = datetime.datetime.now()
    
    return [
        # Edge case: very old timestamp with each label
        {"label": "API_LATENCY", "value": 42, "timestamp": 0},  # Unix epoch
        {"label": "DB_CONNECTIONS", "value": 43, "timestamp": 1000},  # Unix epoch + 1 second
        
        # Edge case: same timestamp, same label, different values
        {"label": "MEMORY_USAGE", "value": 100, "timestamp": int((now - datetime.timedelta(hours=1)).timestamp() * 1000)},
        {"label": "MEMORY_USAGE", "value": 101, "timestamp": int((now - datetime.timedelta(hours=1)).timestamp() * 1000)},
        
        # Edge case: same timestamp, different labels
        {"label": "CPU_USAGE", "value": 80, "timestamp": int((now - datetime.timedelta(hours=2)).timestamp() * 1000)},
        {"label": "NETWORK_THROUGHPUT", "value": 90, "timestamp": int((now - datetime.timedelta(hours=2)).timestamp() * 1000)},
    ]

# Create complete datasets
def create_test_data_sets():
    # Create basic dataset
    basic_count = 100
    basic_metrics = generate_basic_metrics(basic_count)
    special_case_metrics = generate_special_case_metrics()
    combined_basic_metrics = basic_metrics + special_case_metrics
    
    # Shuffle to ensure they're not in order
    random.shuffle(combined_basic_metrics)
    
    # Create extended dataset
    extended_count = 200
    extended_metrics = generate_extended_metrics(extended_count)
    extended_special_case_metrics = generate_extended_special_case_metrics()
    combined_extended_metrics = extended_metrics + extended_special_case_metrics
    
    # Shuffle to ensure they're not in order
    random.shuffle(combined_extended_metrics)
    
    return {
        "basicMetrics": combined_basic_metrics,
        "extendedMetrics": combined_extended_metrics
    }

if __name__ == "__main__":
    # Set the random seed for reproducibility
    random.seed(42)

    # Generate the test data
    test_data = create_test_data_sets()

    # Write to a JSON file
    with open("test_data.json", "w") as f:
        json.dump(test_data, f, indent=2)

    # Output some statistics about the data
    print(f"Basic metrics count: {len(test_data['basicMetrics'])}")
    print(f"Extended metrics count: {len(test_data['extendedMetrics'])}")

    # Extract a few sample metrics to display
    basic_samples = test_data["basicMetrics"][:5]
    extended_samples = test_data["extendedMetrics"][:5]

    print("Basic metric samples:")
    for sample in basic_samples:
        time_str = datetime.datetime.fromtimestamp(sample["timestamp"] / 1000).strftime('%Y-%m-%d %H:%M:%S')
        print(f"Value: {sample['value']}, Timestamp: {time_str}")

    print("\nExtended metric samples:")
    for sample in extended_samples:
        time_str = datetime.datetime.fromtimestamp(sample["timestamp"] / 1000).strftime('%Y-%m-%d %H:%M:%S')
        print(f"Label: {sample['label']}, Value: {sample['value']}, Timestamp: {time_str}")
