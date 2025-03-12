"""
Minimal test script for metric_query_library
"""
import sys

print("Python path:")
for p in sys.path:
    print(p)

try:
    print("\nTrying to import metric_query_library...")
    import metric_query_library
    print("SUCCESS: metric_query_library imported")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("Done")