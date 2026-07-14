import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

def load_json(filename):

    # data/rate_caps.json
    path = DATA_DIR / filename
    with open(path, "r", encoding="utf-8") as f:  # Reads and parses the JSON file into a Python dict
        return json.load(f)

def main():
    rates = load_json("rate_caps.json")
    drugs = load_json("generic_map.json")

    print(f"Loaded {len(rates['procedures'])} rate-capped procedures")
    print(f"Loaded {len(drugs['drugs'])} brand-to-generic mappings")

    # sanity check: no duplicate codes, no missing rates
    codes = [p["code"] for p in rates["procedures"]]
    assert len(codes) == len(set(codes)), "Duplicate procedure codes found!"
    assert all(p["rate"] > 0 for p in rates["procedures"]), "Found a zero/negative rate!"

    print("\nSample lookup — 'MRI Knee Single Joint Without Contrast':")
    match = next(p for p in rates["procedures"] if "MRI Knee" in p["name"])
    print(f"  Capped rate: ₹{match['rate']}")

    print("\nAll checks passed. Layer 0 data is ready.")

if __name__ == "__main__":
    main()