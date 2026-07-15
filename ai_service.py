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


def extract_bill_data(image_path: str) -> dict:
    """
    Sends a bill image to Gemini and returns structured line-item data.
    This function does ONLY extraction - no rate comparison, no flagging.
    """
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
            EXTRACTION_PROMPT,
        ],
    )

    return response.text