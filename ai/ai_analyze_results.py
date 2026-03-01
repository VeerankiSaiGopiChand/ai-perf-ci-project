import csv
import os
import requests
import json
import sys

RESULT_FILE = "reports/results.jtl"
SUMMARY_FILE = "reports/ai_summary.txt"
CURRENT_METRIC_FILE = "metrics/current_metrics.json"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def extract_metrics(file_path):
    total_time = 0
    count = 0
    errors = 0

    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            total_time += int(row["elapsed"])
            count += 1
            if row["success"] == "false":
                errors += 1

    avg = total_time / count if count else 0
    error_rate = (errors / count) * 100 if count else 0

    return {
        "total_requests": count,
        "avg_response_time": avg,
        "error_rate": error_rate
    }


def fallback_summary(metrics):
    status = "stable"

    if metrics["error_rate"] > 5:
        status = "unstable"
    elif metrics["avg_response_time"] > 1000:
        status = "performance degradation observed"

    return f"""
AI Performance Summary (Fallback Mode)

Total Requests: {metrics['total_requests']}
Average Response Time: {metrics['avg_response_time']:.2f} ms
Error Rate: {metrics['error_rate']:.2f} %

System assessment: The system is {status} under the tested load.
"""


def generate_ai_summary(metrics):
    if not OPENAI_API_KEY:
        return fallback_summary(metrics)

    prompt = f"""
Analyze these performance test results:

Total Requests: {metrics['total_requests']}
Average Response Time: {metrics['avg_response_time']:.2f} ms
Error Rate: {metrics['error_rate']:.2f} %

Provide a concise executive-level performance summary.
"""

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3
            },
            timeout=15
        )

        if response.status_code != 200:
            return fallback_summary(metrics)

        data = response.json()
        return data["choices"][0]["message"]["content"]

    except Exception:
        return fallback_summary(metrics)


if __name__ == "__main__":
    os.makedirs("metrics", exist_ok=True)

    metrics = extract_metrics(RESULT_FILE)

    # Save current metrics
    with open(CURRENT_METRIC_FILE, "w") as f:
        json.dump(metrics, f, indent=4)

    summary = generate_ai_summary(metrics)

    with open(SUMMARY_FILE, "w") as f:
        f.write(summary)

    print("AI Summary + Metrics Stored Successfully")