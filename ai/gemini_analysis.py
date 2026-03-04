import os
import google.generativeai as genai

RESULT_FILE = "reports/results.jtl"
OUTPUT_FILE = "reports/ai_summary.txt"

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-pro")


def read_results():
    try:
        with open(RESULT_FILE, "r") as f:
            return f.read()
    except:
        return "No JMeter results found."


def analyze_performance(data):

    prompt = f"""
You are a performance testing expert.

Analyze the following JMeter test results and produce a short performance summary.

{data}

Provide:
- System health
- Risk level
- SLA breach probability
- Scaling recommendation
"""

    response = model.generate_content(prompt)

    return response.text


if __name__ == "__main__":

    results = read_results()

    summary = analyze_performance(results)

    with open(OUTPUT_FILE, "w") as f:
        f.write(summary)

    print("Gemini AI analysis completed.")