"""
Stage 4: Deduplication
Identifies and marks duplicate institute records using:
  1. Exact phone number match
  2. Fuzzy name + city match
"""

from difflib import SequenceMatcher

import db
from config import NAME_SIMILARITY_THRESHOLD


def _normalize_phone(phone: str) -> str:
    """Normalize phone to digits only for comparison."""
    if not phone:
        return ""
    return "".join(c for c in phone if c.isdigit())


def _normalize_name(name: str) -> str:
    """Normalize name for comparison: lowercase, strip common suffixes."""
    if not name:
        return ""
    name = name.lower().strip()
    # Remove common suffixes
    for suffix in [" pvt ltd", " pvt. ltd.", " pvt. ltd", " private limited",
                   " limited", " ltd", " ltd.", " llp", " institute",
                   " academy", " classes", " coaching", " education",
                   " educational", " - home", " home"]:
        if name.endswith(suffix):
            name = name[:-len(suffix)].strip()
    return name


def _name_similarity(name1: str, name2: str) -> float:
    """Compute similarity ratio between two names (0.0 to 1.0)."""
    n1 = _normalize_name(name1)
    n2 = _normalize_name(name2)
    if not n1 or not n2:
        return 0.0
    return SequenceMatcher(None, n1, n2).ratio()


def _record_completeness(record: dict) -> int:
    """Score how complete a record is (higher = more data)."""
    score = 0
    if record.get("name"):
        score += 3
    if record.get("phone"):
        score += 3
    if record.get("address"):
        score += 2
    if record.get("website"):
        score += 1
    return score


def run():
    """Run Stage 4: Deduplication."""
    db.init_db()

    # Get all institutes (including previously marked duplicates — we'll re-process)
    all_records = db.get_all_institutes(include_duplicates=True)

    print("=" * 60)
    print("  STAGE 4: Deduplication")
    print("=" * 60)
    print(f"  Total records: {len(all_records)}")
    print("=" * 60)

    if not all_records:
        print("\n  ✓ No records to deduplicate.\n")
        return

    # Reset all duplicate flags first
    conn = db.get_connection()
    try:
        conn.execute("UPDATE institutes SET is_duplicate = 0, duplicate_of = NULL")
        conn.commit()
    finally:
        conn.close()

    # ─── Phase 1: Exact Phone Match ─────────────────────────────────
    print("\n  Phase 1: Exact phone number matching...")

    phone_groups: dict[str, list[dict]] = {}
    for record in all_records:
        phone = _normalize_phone(record.get("phone", ""))
        if phone and len(phone) >= 10:
            if phone not in phone_groups:
                phone_groups[phone] = []
            phone_groups[phone].append(record)

    phone_dupes = 0
    for phone, group in phone_groups.items():
        if len(group) <= 1:
            continue
        # Sort by completeness — keep the most complete record
        group.sort(key=_record_completeness, reverse=True)
        original = group[0]
        for dupe in group[1:]:
            db.mark_duplicate(dupe["id"], original["id"])
            phone_dupes += 1

    print(f"    Found {phone_dupes} duplicates by phone number.")

    # ─── Phase 2: Fuzzy Name + City Match ────────────────────────────
    print("  Phase 2: Fuzzy name + city matching...")

    # Reload to get updated duplicate flags
    remaining = db.get_all_institutes(include_duplicates=False)

    # Group by city
    city_groups: dict[str, list[dict]] = {}
    for record in remaining:
        city = (record.get("city") or "").lower().strip()
        if city:
            if city not in city_groups:
                city_groups[city] = []
            city_groups[city].append(record)

    name_dupes = 0
    for city, group in city_groups.items():
        if len(group) <= 1:
            continue

        # Compare all pairs within the city
        marked = set()
        for i in range(len(group)):
            if group[i]["id"] in marked:
                continue
            for j in range(i + 1, len(group)):
                if group[j]["id"] in marked:
                    continue
                sim = _name_similarity(
                    group[i].get("name", ""),
                    group[j].get("name", "")
                )
                if sim >= NAME_SIMILARITY_THRESHOLD:
                    # Keep the more complete record
                    if _record_completeness(group[i]) >= _record_completeness(group[j]):
                        db.mark_duplicate(group[j]["id"], group[i]["id"])
                        marked.add(group[j]["id"])
                    else:
                        db.mark_duplicate(group[i]["id"], group[j]["id"])
                        marked.add(group[i]["id"])
                    name_dupes += 1

    print(f"    Found {name_dupes} duplicates by fuzzy name + city.")

    # ─── Summary ─────────────────────────────────────────────────────
    stats = db.get_stats()
    total_dupes = phone_dupes + name_dupes

    print(f"\n  ✓ Stage 4 complete.")
    print(f"    Total duplicates marked: {total_dupes}")
    print(f"    Unique institutes:       {stats['institutes_unique']}")
    print(f"    Duplicate records:       {stats['institutes_duplicates']}\n")


if __name__ == "__main__":
    run()
