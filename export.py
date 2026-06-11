"""
Export: CSV and JSON output for deduplicated institute records.
"""

import csv
import json
import os

import db
from config import DATA_DIR


EXPORT_FIELDS = [
    "id", "name", "phone", "address", "city", "state",
    "website", "source_url", "category", "last_seen",
]


def export_csv(filepath: str = None) -> str:
    """Export deduplicated institutes to CSV. Returns the filepath."""
    if filepath is None:
        filepath = os.path.join(DATA_DIR, "institutes.csv")

    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    records = db.get_all_institutes(include_duplicates=False)

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=EXPORT_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for record in records:
            writer.writerow(record)

    return filepath


def export_json(filepath: str = None) -> str:
    """Export deduplicated institutes to JSON. Returns the filepath."""
    if filepath is None:
        filepath = os.path.join(DATA_DIR, "institutes.json")

    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    records = db.get_all_institutes(include_duplicates=False)

    # Filter to only export fields
    clean_records = []
    for r in records:
        clean = {k: r.get(k, "") for k in EXPORT_FIELDS}
        clean_records.append(clean)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(clean_records, f, indent=2, ensure_ascii=False)

    return filepath


def run():
    """Run export to both CSV and JSON."""
    db.init_db()

    records = db.get_all_institutes(include_duplicates=False)
    total = len(records)

    print("=" * 60)
    print("  EXPORT: CSV & JSON")
    print("=" * 60)
    print(f"  Unique records to export: {total}")
    print("=" * 60)

    if total == 0:
        print("\n  [WARNING] No records to export. Run the pipeline first.\n")
        return

    csv_path = export_csv()
    print(f"\n  [OK] CSV exported:  {csv_path}")

    json_path = export_json()
    print(f"  [OK] JSON exported: {json_path}")

    # Sync with React Web Application assets
    try:
        import shutil
        web_assets_dir = os.path.join(os.path.dirname(os.path.dirname(json_path)), "web", "src", "assets")
        if os.path.exists(web_assets_dir):
            shutil.copy2(json_path, os.path.join(web_assets_dir, "institutes.json"))
            print(f"  [OK] Synced with React Web App assets: {os.path.join(web_assets_dir, 'institutes.json')}")
    except Exception as e:
        print(f"  [WARNING] Could not sync with React Web App assets: {e}")

    print(f"\n  Total records exported: {total}\n")


if __name__ == "__main__":
    run()
