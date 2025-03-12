"""
Utility functions for the Metric Query API.
"""
import os
import json
import metric_query_library as mq
from typing import List, Dict, Any, Optional

def load_test_data(file_path: Optional[str] = None) -> Dict[str, List[mq.Metric]]:
    """
    Load test data from a JSON file.
    
    Args:
        file_path: Path to the test data file. If None, tries to locate test_data.json
                  relative to the root of the project.
    
    Returns:
        Dictionary containing 'metrics' and 'labeled_metrics' lists
    
    Raises:
        FileNotFoundError: If the test data file cannot be found
    """
    if file_path is None:
        # Try to find test_data.json in the project root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        api_dir = os.path.dirname(current_dir)
        file_path = os.path.join(api_dir, "test_data.json")
    
    try:
        with open(file_path, "r") as f:
            test_data = json.load(f)
            
        # Convert JSON data to Metric objects
        metrics = [
            mq.Metric(
                value=item["value"],
                timestamp=item["timestamp"] // 1000 if "timestamp" in item else item.get("timestamp_ms", 0) // 1000
            )
            for item in test_data.get("basicMetrics", [])
        ]
        
        # Convert JSON data to LabeledMetric objects
        labeled_metrics = [
            mq.LabeledMetric(
                label=item["label"],
                value=item["value"],
                timestamp=item["timestamp"] // 1000 if "timestamp" in item else item.get("timestamp_ms", 0) // 1000
            )
            for item in test_data.get("extendedMetrics", [])
        ]
        
        return {
            "metrics": metrics,
            "labeled_metrics": labeled_metrics
        }
    except FileNotFoundError:
        raise FileNotFoundError(f"Test data file not found: {file_path}")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON in test data file: {file_path}")
    except Exception as e:
        raise Exception(f"Error loading test data: {str(e)}")