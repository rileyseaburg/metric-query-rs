"""
Storage for metrics data.
"""
from typing import List
import os
from metric_query_simplified import Metric, LabeledMetric
from utils.utils import load_test_data

# In-memory storage for metrics
metrics_store: List[Metric] = []
labeled_metrics_store: List[LabeledMetric] = []

# Load initial test data
try:
    print("Loading test data...")
    test_data = load_test_data()
    metrics_store.extend(test_data["metrics"])
    labeled_metrics_store.extend(test_data["labeled_metrics"])
    print(f"Loaded {len(metrics_store)} metrics and {len(labeled_metrics_store)} labeled metrics")
except Exception as e:
    print(f"Error loading test data: {e}")