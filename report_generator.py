import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# Report function
def generate_medical_report(prediction, confidence):
    prompt = f"""
You are an experienced radiologist.

An AI model analyzed a chest X-ray.

Prediction:
{prediction}

Confidence:
{confidence:.2f}%

Generate a professional medical report.

IMPORTANT:
- Do NOT use Markdown.
- Do NOT use ** or *.
- Do NOT use # headings.
- Return plain text only.
- Use numbered headings like:

AI-Assisted Chest X-ray Report

1. Prediction Summary
2. Possible Findings
3. Clinical Interpretation
4. Possible Symptoms
5. Recommendations
6. Precautions
7. Disclaimer

Keep the report professional and concise.
Mention that this report is AI-assisted and should not replace professional medical advice.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        max_tokens=700
    )

    return response.choices[0].message.content