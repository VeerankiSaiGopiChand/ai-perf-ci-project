import json
import os
import sys

CURRENT_FILE = "metrics/current_metrics.json"
LAST_FILE = "metrics/last_metrics.json"

THRESHOLD_PERCENT = 15  # Fail if response time increases by 15%

def load_metrics(path):
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)

def save_last_metrics(metrics):
    with open(LAST_FILE, "w") as f:
        json.dump(metrics, f, indent=4)

if __name__ == "__main__":

    current = load_metrics(CURRENT_FILE)
    last = load_metrics(LAST_FILE)

    if not last:
        print("No previous metrics found. Saving current as baseline.")
        save_last_metrics(current)
        sys.exit(0)

    current_avg = current["avg_response_time"]
    last_avg = last["avg_response_time"]

    increase_percent = ((current_avg - last_avg) / last_avg) * 100

    print(f"Previous Avg: {last_avg}")
    print(f"Current Avg: {current_avg}")
    print(f"Increase %: {increase_percent:.2f}")

    if increase_percent > THRESHOLD_PERCENT:
        print("Performance regression detected! Failing pipeline.")
        sys.exit(1)
    else:
        print("Performance stable. Updating baseline.")
        save_last_metrics(current)
        sys.exit(0)