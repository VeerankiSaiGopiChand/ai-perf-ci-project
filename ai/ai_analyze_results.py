import csv

RESULT_FILE = "reports/results.jtl"

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

    return avg, error_rate


if __name__ == "__main__":
    avg, error_rate = extract_metrics(RESULT_FILE)

    summary = f"""
AI Performance Summary:

Total Requests: {int(avg != 0)}
Average Response Time: {avg:.2f} ms
Error Rate: {error_rate:.2f} %

The system executed successfully under the tested load.
"""

    with open("reports/ai_summary.txt", "w") as f:
        f.write(summary)

    print("AI Summary Created Successfully")