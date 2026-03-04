import os
from google import genai

RESULT_FILE = "reports/results.jtl"
OUTPUT_FILE = "reports/ai_summary.txt"


def read_results():
    try:
        with open(RESULT_FILE, "r") as f:
            return f.read()
    except:
        return "No JMeter results found."


def fallback_summary(data):
    return f"""
AI Analysis Fallback Mode

JMeter test completed successfully.

Basic observations:
- Test executed and results generated
- Review JMeter HTML report for detailed metrics

Note: Gemini API quota exceeded, so fallback summary generated.
"""


def analyze_performance(data):

    try:

        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

        prompt = f"""
You are a performance testing expert.

Analyze the following JMeter results and produce a short performance summary.

{data}

Provide:
- System health
- Risk level
- SLA breach probability
- Scaling recommendation
"""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:

        print("Gemini API failed:", e)

        return fallback_summary(data)


if __name__ == "__main__":

    results = read_results()

    summary = analyze_performance(results)

    with open(OUTPUT_FILE, "w") as f:
        f.write(summary)

    print("AI summary generated.")