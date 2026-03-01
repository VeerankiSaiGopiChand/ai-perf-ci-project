import csv
import os
import json
import requests

RESULT_FILE = "reports/results.jtl"
TECH_FILE = "reports/technical_summary.txt"
BUSINESS_FILE = "reports/business_summary.txt"
CAPACITY_FILE = "reports/capacity_forecast.txt"
CURRENT_METRIC_FILE = "metrics/current_metrics.json"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# --------------------------------
# STEP 1: Extract Metrics
# --------------------------------
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


# --------------------------------
# STEP 2: Health Score Logic
# --------------------------------
def calculate_health_score(metrics):
    score = 100

    if metrics["avg_response_time"] > 1000:
        score -= 40
    elif metrics["avg_response_time"] > 500:
        score -= 20
    elif metrics["avg_response_time"] > 300:
        score -= 10

    if metrics["error_rate"] > 5:
        score -= 40
    elif metrics["error_rate"] > 2:
        score -= 20
    elif metrics["error_rate"] > 1:
        score -= 10

    return max(score, 0)


def classify_risk(score):
    if score >= 85:
        return "LOW"
    elif score >= 65:
        return "MEDIUM"
    elif score >= 40:
        return "HIGH"
    else:
        return "CRITICAL"


def calculate_sla_probability(metrics):
    if metrics["error_rate"] > 5 or metrics["avg_response_time"] > 1000:
        return "HIGH"
    elif metrics["error_rate"] > 2 or metrics["avg_response_time"] > 500:
        return "MEDIUM"
    else:
        return "LOW"


def calculate_customer_impact(risk):
    if risk == "LOW":
        return "Minimal"
    elif risk == "MEDIUM":
        return "Moderate"
    elif risk == "HIGH":
        return "Significant"
    else:
        return "Severe"


# --------------------------------
# STEP 3: Predictive Capacity Model (NEW)
# --------------------------------
def predictive_capacity_model(metrics):

    base_response = metrics["avg_response_time"]
    base_error = metrics["error_rate"]

    scenarios = [1.25, 1.5, 2.0]

    predictions = []

    for multiplier in scenarios:
        predicted_response = base_response * multiplier
        predicted_error = base_error * multiplier

        predicted_health = 100

        if predicted_response > 1000:
            predicted_health -= 40
        elif predicted_response > 500:
            predicted_health -= 20
        elif predicted_response > 300:
            predicted_health -= 10

        if predicted_error > 5:
            predicted_health -= 40
        elif predicted_error > 2:
            predicted_health -= 20
        elif predicted_error > 1:
            predicted_health -= 10

        predicted_health = max(predicted_health, 0)

        predictions.append({
            "traffic_multiplier": multiplier,
            "predicted_response_time": round(predicted_response, 2),
            "predicted_error_rate": round(predicted_error, 2),
            "predicted_health_score": predicted_health
        })

    return predictions


# --------------------------------
# STEP 4: Generate Technical Summary
# --------------------------------
def generate_technical_summary(metrics):
    return f"""
TECHNICAL PERFORMANCE SUMMARY

Total Requests: {metrics['total_requests']}
Average Response Time: {metrics['avg_response_time']:.2f} ms
Error Rate: {metrics['error_rate']:.2f} %

Health Score: {metrics['health_score']}/100
Risk Level: {metrics['risk_level']}
"""


# --------------------------------
# STEP 5: Generate Business Summary
# --------------------------------
def generate_business_summary(metrics):

    if not OPENAI_API_KEY:
        return f"""
BUSINESS PERFORMANCE SUMMARY

Performance Health Score: {metrics['health_score']} / 100
Risk Level: {metrics['risk_level']}
SLA Breach Probability: {metrics['sla_probability']}
Customer Impact: {metrics['customer_impact']}

System stability is classified as {metrics['risk_level']} under current workload.
"""

    prompt = f"""
Provide a business-level executive summary based on:

Performance Health Score: {metrics['health_score']} / 100
Risk Level: {metrics['risk_level']}
SLA Breach Probability: {metrics['sla_probability']}
Customer Impact: {metrics['customer_impact']}

Explain impact on users and business operations.
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
            raise Exception("API Error")

        data = response.json()
        return data["choices"][0]["message"]["content"]

    except:
        return f"""
BUSINESS PERFORMANCE SUMMARY

Performance Health Score: {metrics['health_score']} / 100
Risk Level: {metrics['risk_level']}
SLA Breach Probability: {metrics['sla_probability']}
Customer Impact: {metrics['customer_impact']}
"""


# --------------------------------
# MAIN EXECUTION
# --------------------------------
if __name__ == "__main__":

    os.makedirs("metrics", exist_ok=True)

    metrics = extract_metrics(RESULT_FILE)

    # Intelligence Layer
    metrics["health_score"] = calculate_health_score(metrics)
    metrics["risk_level"] = classify_risk(metrics["health_score"])
    metrics["sla_probability"] = calculate_sla_probability(metrics)
    metrics["customer_impact"] = calculate_customer_impact(metrics["risk_level"])

    # Save JSON
    with open(CURRENT_METRIC_FILE, "w") as f:
        json.dump(metrics, f, indent=4)

    # Generate summaries
    technical_summary = generate_technical_summary(metrics)
    business_summary = generate_business_summary(metrics)

    with open(TECH_FILE, "w") as f:
        f.write(technical_summary)

    with open(BUSINESS_FILE, "w") as f:
        f.write(business_summary)

    # Capacity Forecast
    predictions = predictive_capacity_model(metrics)

    capacity_text = "CAPACITY FORECAST REPORT\n"

    for p in predictions:
        capacity_text += f"""
Traffic Increase: {int(p['traffic_multiplier']*100)}%
Predicted Response Time: {p['predicted_response_time']} ms
Predicted Error Rate: {p['predicted_error_rate']} %
Predicted Health Score: {p['predicted_health_score']}/100
-----------------------------------
"""

    with open(CAPACITY_FILE, "w") as f:
        f.write(capacity_text)

    print("Phase 3B Complete: Scoring + Risk + Capacity Forecast Generated")