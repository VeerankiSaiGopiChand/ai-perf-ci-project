import csv
import os
import requests
import sys

RESULT_FILE = "reports/results.jtl"
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

    return count, avg, error_rate


def fallback_summary(total, avg, error_rate):
    status = "stable"
    if error_rate > 5:
        status = "unstable"
    elif avg > 1000:
        status = "performance degradation observed"

    return f"""
AI Performance Summary (Fallback Mode):

Total Requests: {total}
Average Response Time: {avg:.2f} ms
Error Rate: {error_rate:.2f} %

System assessment: The system is {status} under the tested load.
"""


def generate_ai_summary(total_requests, avg_response, error_rate):
    if not OPENAI_API_KEY:
        return fallback_summary(total_requests, avg_response, error_rate)

    prompt = f"""
Analyze these performance test results:

Total Requests: {total_requests}
Average Response Time: {avg_response:.2f} ms
Error Rate: {error_rate:.2f} %

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
            return fallback_summary(total_requests, avg_response, error_rate)

        data = response.json()
        return data["choices"][0]["message"]["content"]

    except Exception:
        return fallback_summary(total_requests, avg_response, error_rate)


if __name__ == "__main__":
    total, avg, error_rate = extract_metrics(RESULT_FILE)
    summary = generate_ai_summary(total, avg, error_rate)

    with open("reports/ai_summary.txt", "w") as f:
        f.write(summary)

    print("AI Summary Generated (with fallback protection)")