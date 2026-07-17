from rapidfuzz import fuzz, process
from analyzer import load_data

procedures, drugs = load_data()
brand_names = [d["brand"] for d in drugs]

item_name = "Crocin Advance Tablet (strip of 10)"

result = process.extractOne(item_name, brand_names, scorer=fuzz.token_sort_ratio)
print("token_sort_ratio:", result)

result2 = process.extractOne(item_name, brand_names, scorer=fuzz.partial_ratio)
print("partial_ratio:", result2)