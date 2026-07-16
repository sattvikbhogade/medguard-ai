import time

from google import genai
from google.genai import types

from config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

EXTRACTION_PROMPT = """
You are a document extraction tool. You are given an image of a medical bill.

Extract every billed line item you can see. For each one, capture:
- item: the name of the procedure/test/medicine as written on the bill
- quantity: number of units (default to 1 if not specified)
- charged_amount: the amount charged in INR, as a number (no currency symbol)

Do NOT judge whether any charge is reasonable or suspicious. Only extract
what is written. If a value is unclear or unreadable, use null.

Return ONLY valid JSON in this exact structure, nothing else - no markdown,
no explanation:

{
  "hospital_name": "string or null",
  "bill_date": "string or null",
  "line_items": [
    {"item": "string", "quantity": number, "charged_amount": number}
  ]
}
"""


def extract_bill_data(image_path: str, max_retries: int = 3) -> str:
    """
    Sends a bill image to Gemini and returns structured line-item data as raw text.
    Tries gemini-flash-latest first; if that fails completely, falls back to
    gemini-2.5-flash-lite as a second attempt before giving up.
    """
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    models_to_try = ["gemini-flash-latest", "gemini-2.0-flash"]

    last_error = None
    for model_name in models_to_try:
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=[
                        types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                        EXTRACTION_PROMPT,
                    ],
                )
                return response.text
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"[{model_name}] Attempt {attempt + 1} failed ({e}). Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"[{model_name}] All {max_retries} attempts failed. Trying next model...")

    raise last_error

COMPLAINT_PROMPT_TEMPLATE = """
You are drafting a formal but simple complaint letter for a patient to submit
to a hospital's billing department or a consumer grievance authority.

Hospital: {hospital}
Bill date: {date}

The following potential billing concerns were identified:
{findings_text}

Write a short, polite, factual complaint letter. Do NOT accuse the hospital
of fraud. Use "potential concern" language throughout. List each issue as a
numbered point. End asking for a review and itemized clarification.

Return plain text only, no markdown formatting.
"""


def generate_complaint(hospital_name: str, bill_date: str, findings: list) -> str:
    findings_text = "\n".join(
        f"- {f['message']}" for f in findings
    ) or "- No specific issues listed."

    prompt = COMPLAINT_PROMPT_TEMPLATE.format(
        hospital=hospital_name or "the hospital",
        date=bill_date or "the date on the bill",
        findings_text=findings_text
    )

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-flash-latest",
                contents=[prompt],
            )
            return response.text
        except Exception as e:
            if attempt < 2:
                time.sleep(2 ** attempt)
            else:
                raise