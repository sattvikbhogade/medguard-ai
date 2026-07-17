import base64
import json
import mimetypes
import time
import urllib.error
import urllib.request

from config import GEMINI_API_KEY, OPENROUTER_API_KEY, GROK_API_KEY
from google import genai
from google.genai import types

GEMINI_MODELS = ["gemini-flash-latest", "gemini-2.0-flash"]
OPENROUTER_URL = "https://api.openrouter.ai/v1/chat/completions"
OPENROUTER_MODEL = "gpt-4o-mini"
GROK_API_URL = "https://api.x.ai/v1/responses"
GROK_MODEL = "grok-4.5"

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


def build_image_content(prompt: str, image_path: str | None = None, image_bytes: bytes | None = None) -> list:
    content = [{"type": "input_text", "text": prompt}]

    if image_path is not None or image_bytes is not None:
        if image_bytes is None:
            with open(image_path, "rb") as f:
                image_bytes = f.read()

        mime_type = _detect_mime_type(image_path or "bill.jpg")
        encoded = base64.b64encode(image_bytes).decode("utf-8")
        content.append(
            {
                "type": "input_image",
                "image_url": f"data:{mime_type};base64,{encoded}",
            }
        )

    return content


def build_grok_payload(prompt: str, image_path: str | None = None, image_bytes: bytes | None = None, model: str = GROK_MODEL) -> dict:
    return {
        "model": model,
        "input": [
            {
                "role": "user",
                "content": build_image_content(prompt, image_path=image_path, image_bytes=image_bytes),
            }
        ],
        "temperature": 0.2,
        "max_output_tokens": 1200,
    }


def build_openrouter_payload(prompt: str, image_path: str | None = None, image_bytes: bytes | None = None, model: str = OPENROUTER_MODEL) -> dict:
    return {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": build_image_content(prompt, image_path=image_path, image_bytes=image_bytes),
            }
        ],
        "temperature": 0.2,
        "max_tokens": 1200,
    }


def _detect_mime_type(image_path: str) -> str:
    guessed_type, _ = mimetypes.guess_type(image_path)
    if guessed_type in {"image/jpeg", "image/png", "image/webp", "image/gif"}:
        return guessed_type
    return "image/jpeg"


def _call_http_api(url: str, payload: dict, api_key: str, timeout: int = 60) -> dict:
    request_data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=request_data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"AI provider request failed: {exc.code} {error_body}") from exc


def call_gemini(prompt: str, image_path: str | None = None, image_bytes: bytes | None = None) -> str:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    client = genai.Client(api_key=GEMINI_API_KEY)
    if image_path is not None or image_bytes is not None:
        if image_bytes is None:
            with open(image_path, "rb") as f:
                image_bytes = f.read()

        contents = [
            types.Part.from_bytes(data=image_bytes, mime_type=_detect_mime_type(image_path or "bill.jpg")),
            prompt,
        ]
    else:
        contents = [prompt]

    last_error = None
    for model_name in GEMINI_MODELS:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
            )
            return response.text
        except Exception as exc:
            last_error = exc
            print(f"[Gemini] Model {model_name} failed: {exc}")

    raise RuntimeError("Gemini provider failed.") from last_error


def call_openrouter(prompt: str, image_path: str | None = None, image_bytes: bytes | None = None) -> str:
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not configured.")

    payload = build_openrouter_payload(prompt, image_path=image_path, image_bytes=image_bytes)
    response = _call_http_api(OPENROUTER_URL, payload, OPENROUTER_API_KEY)

    if "output_text" in response:
        return response["output_text"].strip()
    if "choices" in response and response["choices"]:
        choice = response["choices"][0]
        if isinstance(choice.get("message"), dict):
            return choice["message"].get("content", "").strip()
    raise RuntimeError("OpenRouter returned no usable response.")


def _call_grok_api(payload: dict, timeout: int = 60) -> str:
    if not GROK_API_KEY:
        raise RuntimeError("GROK_API_KEY is not configured.")

    response_data = _call_http_api(GROK_API_URL, payload, GROK_API_KEY, timeout=timeout)

    output_text = response_data.get("output_text")
    if output_text:
        return output_text.strip()

    if "output" in response_data:
        output = response_data["output"]
        if isinstance(output, list):
            text_parts = []
            for item in output:
                if isinstance(item, dict):
                    if item.get("type") == "output_text":
                        text_parts.append(item.get("text", ""))
                    elif item.get("type") == "output":
                        text_parts.append(item.get("text", ""))
            if text_parts:
                return "".join(text_parts).strip()

    raise RuntimeError("Grok API did not return any usable text output.")


def call_grok(prompt: str, image_path: str | None = None, image_bytes: bytes | None = None, max_retries: int = 3) -> str:
    payload = build_grok_payload(prompt, image_path=image_path, image_bytes=image_bytes)

    last_error = None
    for attempt in range(max_retries):
        try:
            return _call_grok_api(payload)
        except Exception as exc:
            last_error = exc
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"[Grok] Attempt {attempt + 1} failed ({exc}). Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"[Grok] All {max_retries} attempts failed.")

    raise last_error


def call_ai_provider(prompt: str, image_path: str | None = None, image_bytes: bytes | None = None, max_retries: int = 3) -> str:
    providers = [
        ("gemini", GEMINI_API_KEY, call_gemini),
        ("openrouter", OPENROUTER_API_KEY, call_openrouter),
        ("grok", GROK_API_KEY, lambda p, image_path, image_bytes: call_grok(p, image_path=image_path, image_bytes=image_bytes, max_retries=max_retries)),
    ]

    last_error = None
    for name, key, func in providers:
        if not key:
            continue
        try:
            return func(prompt, image_path=image_path, image_bytes=image_bytes)
        except Exception as exc:
            last_error = exc
            print(f"[{name}] provider failed: {exc}")

    raise RuntimeError("No AI provider succeeded.") from last_error


def extract_bill_data(image_path: str, max_retries: int = 3) -> str:
    """
    Sends a bill image to the best available AI provider and returns structured line-item data as raw text.
    """
    return call_ai_provider(EXTRACTION_PROMPT, image_path=image_path, max_retries=max_retries)


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

    return call_ai_provider(prompt, max_retries=3)
