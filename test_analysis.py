import json
from ai_service import extract_bill_data
from analyzer import analyze_line_items

# Step 1: extract (Layer 3)
raw_result = extract_bill_data("uploads/mock_hospital_bill.jpg")
extracted = json.loads(raw_result)

# Step 2: match/flag (Layer 4)
analysis = analyze_line_items(extracted["line_items"])

print(json.dumps(analysis, indent=2))