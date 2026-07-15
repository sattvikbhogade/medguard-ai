import json
from pathlib import Path
from rapidfuzz import fuzz, process

DATA_DIR = Path(__file__).parent / "data"

# Line items whose text is too generic/vague to verify against any rate list.
# If the fuzzy matcher can't do better than this list, we flag it as vague
# rather than pretending we found a real match.
VAGUE_KEYWORDS = ["miscellaneous", "misc", "other charges", "sundry", "consumables"]

# Minimum similarity score (0-100) to accept a fuzzy match as real.
# Below this, we treat the item as "no reference rate available" instead
# of forcing a bad match - a wrong match is worse than no match.
MATCH_THRESHOLD = 65


def load_data():
    with open(DATA_DIR / "rate_caps.json", "r", encoding="utf-8") as f:
        rates = json.load(f)
    with open(DATA_DIR / "generic_map.json", "r", encoding="utf-8") as f:
        drugs = json.load(f)
    return rates["procedures"], drugs["drugs"]


def is_vague(item_name: str) -> bool:
    name_lower = item_name.lower()
    return any(keyword in name_lower for keyword in VAGUE_KEYWORDS)


def find_rate_match(item_name: str, procedures: list):
    """
    Fuzzy-matches a bill's line item text against known procedure names.
    Returns the matched procedure dict, or None if nothing scores above threshold.
    """
    choices = {p["name"]: p for p in procedures}
    result = process.extractOne(
        item_name, choices.keys(), scorer=fuzz.token_sort_ratio
    )
    if result is None:
        return None
    matched_name, score, _ = result
    if score < MATCH_THRESHOLD:
        return None
    return choices[matched_name]


def find_generic_alternative(item_name: str, drugs: list):
    """
    Checks if a line item matches a known brand drug with a generic alternative.
    Uses partial_ratio (not token_sort_ratio) because brand names are usually
    short and embedded inside a longer bill description (e.g. dosage, pack size).
    """
    brand_names = {d["brand"]: d for d in drugs}
    result = process.extractOne(
        item_name, brand_names.keys(), scorer=fuzz.partial_ratio
    )
    if result is None:
        return None
    matched_brand, score, _ = result
    if score < MATCH_THRESHOLD:
        return None
    return brand_names[matched_brand]


def analyze_line_items(line_items: list) -> dict:
    """
    Takes extracted line items (from Layer 3) and returns flagged findings.
    Pure Python - no AI calls, fully deterministic, fully explainable.
    """
    procedures, drugs = load_data()

    findings = []
    seen_items = {}  # tracks item names we've already processed, to catch duplicates

    for idx, line in enumerate(line_items):
        item_name = line.get("item", "")
        charged = line.get("charged_amount") or 0
        qty = line.get("quantity", 1)

        # --- Check 1: Duplicate line item ---
        normalized = item_name.strip().lower()
        if normalized in seen_items:
            findings.append({
                "type": "duplicate_charge",
                "item": item_name,
                "charged_amount": charged,
                "message": f"'{item_name}' appears more than once on this bill. "
                           f"Verify both instances were actually provided."
            })
        seen_items[normalized] = idx

        # --- Check 2: Vague/unclear charge ---
        if is_vague(item_name):
            findings.append({
                "type": "vague_charge",
                "item": item_name,
                "charged_amount": charged,
                "message": f"'{item_name}' is too generic to verify. "
                           f"Request an itemized breakdown for this charge."
            })
            continue  # can't rate-match a vague item, move on

        # --- Check 3: Overcharge vs CGHS rate cap ---
        match = find_rate_match(item_name, procedures)
        if match:
            capped_total = match["rate"] * qty
            if charged > capped_total:
                overcharge_amount = charged - capped_total
                findings.append({
                    "type": "overcharge",
                    "item": item_name,
                    "matched_procedure": match["name"],
                    "charged_amount": charged,
                    "capped_rate": capped_total,
                    "overcharge_amount": overcharge_amount,
                    "message": f"Charged Rs.{charged} vs CGHS reference rate of "
                               f"Rs.{capped_total}. Rs.{overcharge_amount} above reference."
                })

        # --- Check 4: Brand drug with generic alternative ---
        generic = find_generic_alternative(item_name, drugs)
        if generic:
            findings.append({
                "type": "generic_available",
                "item": item_name,
                "generic_name": generic["generic"],
                "charged_amount": charged,
                "message": f"'{item_name}' is a branded medicine. Generic "
                           f"equivalent ({generic['generic']}) is typically cheaper."
            })

    return {
        "total_line_items": len(line_items),
        "total_findings": len(findings),
        "findings": findings
    }