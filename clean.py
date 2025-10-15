import json

# Load and clean bulk.json (removes BOM if present)
with open("bulk.json", "r", encoding="utf-8-sig") as f:
    data = json.load(f)

cleaned_docs = []

for doc in data["docs"]:
    # --- Fix bad field names ---
    if "runtime,," in doc:
        doc["runtime"] = doc.pop("runtime,,").strip(",")

    # --- Clean trailing commas in string values ---
    for k, v in list(doc.items()):
        if isinstance(v, str):
            doc[k] = v.strip(",")

    # --- Fix illegal _id values ---
    if "_id" in doc:
        # Replace spaces with underscores
        new_id = doc["_id"].replace(" ", "_")
        # If it starts with "_", prepend "id"
        if new_id.startswith("_"):
            new_id = "id" + new_id
        doc["_id"] = new_id
    else:
        # If no _id at all, let CouchDB generate one
        pass

    cleaned_docs.append(doc)

# Save cleaned file
with open("bulk_clean.json", "w", encoding="utf-8") as f:
    json.dump({"docs": cleaned_docs}, f, ensure_ascii=False, indent=2)

print(f"Cleaned {len(cleaned_docs)} docs and wrote to bulk_clean.json")
