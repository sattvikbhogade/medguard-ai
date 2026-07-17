import json
import urllib.request

from config import GROK_API_KEY

if not GROK_API_KEY:
    raise SystemExit("GROK_API_KEY not configured")

request = urllib.request.Request(
    "https://api.x.ai/v1/models",
    headers={"Authorization": f"Bearer {GROK_API_KEY}"},
    method="GET",
)

with urllib.request.urlopen(request, timeout=30) as response:
    data = json.load(response)

for model in data.get("data", []):
    print(model.get("id"), "-", model.get("object"))