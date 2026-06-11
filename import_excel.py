"""
Import Excel data from targetstudy (1).xlsx into SQLite database.
"""

import os
import re
import pandas as pd
import phonenumbers
from datetime import datetime, timezone

import db
from cities import get_cities


def parse_city_state(address, default_city="Mumbai", default_state="Maharashtra"):
    """Parse city and state from address by searching for matching cities."""
    if not address or not isinstance(address, str):
        return default_city, default_state

    address_lower = address.lower()
    cities = get_cities()

    # Search for longer names first (e.g. "Navi Mumbai" before "Mumbai")
    for c_info in sorted(cities, key=lambda x: len(x["city"]), reverse=True):
        city_name = c_info["city"]
        state_name = c_info["state"]
        if re.search(r"\b" + re.escape(city_name.lower()) + r"\b", address_lower):
            return city_name, state_name

    # Check for "mumbai" substring in case there are no word boundaries
    if "mumbai" in address_lower:
        return "Mumbai", "Maharashtra"

    return default_city, default_state


def extract_phones(phone_text) -> list[str]:
    """Extract and format Indian phone numbers from text using phonenumbers."""
    if not phone_text or pd.isna(phone_text):
        return []

    phone_text = str(phone_text)
    phones = set()

    # 1. Use phonenumbers matcher
    for match in phonenumbers.PhoneNumberMatcher(phone_text, "IN"):
        number = match.number
        if phonenumbers.is_valid_number(number):
            formatted = phonenumbers.format_number(
                number, phonenumbers.PhoneNumberFormat.E164
            )
            phones.add(formatted)

    # 2. Fallback: simple mobile number regex
    mobile_pattern = r"(?<!\d)(?:\+?91[-.\s]?)?([6-9]\d{9})(?!\d)"
    for m in re.findall(mobile_pattern, phone_text):
        try:
            parsed = phonenumbers.parse(m, "IN")
            if phonenumbers.is_valid_number(parsed):
                formatted = phonenumbers.format_number(
                    parsed, phonenumbers.PhoneNumberFormat.E164
                )
                phones.add(formatted)
        except Exception:
            pass

    # 3. Fallback: landline pattern
    landline_pattern = r"\(?0\d{2,4}\)?[-.\s]?\d{6,8}"
    for m in re.findall(landline_pattern, phone_text):
        try:
            parsed = phonenumbers.parse(m, "IN")
            if phonenumbers.is_valid_number(parsed):
                formatted = phonenumbers.format_number(
                    parsed, phonenumbers.PhoneNumberFormat.E164
                )
                phones.add(formatted)
        except Exception:
            pass

    return list(phones)


def run():
    db.init_db()

    excel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "targetstudy (1).xlsx")
    if not os.path.exists(excel_path):
        print(f"  [ERROR] Excel file not found at {excel_path}")
        return

    print("=" * 60)
    print("  IMPORTING EXCEL DATA")
    print("=" * 60)
    print(f"  Reading file: {excel_path} ...")

    try:
        df = pd.read_excel(excel_path)
    except Exception as e:
        print(f"  [ERROR] Error reading Excel file: {e}")
        return

    total_rows = len(df)
    print(f"  Found {total_rows} rows in Excel sheet.")

    records_to_insert = []
    now = datetime.now(timezone.utc).isoformat()

    for idx, row in df.iterrows():
        # Get values
        name = row.get("card-title")
        url = row.get("card-title href")
        address = row.get("card-subtitle")
        phone_raw = row.get("card-subtitle 2")

        # Skip rows with no name
        if not name or pd.isna(name):
            continue

        name = str(name).strip()
        address = str(address).strip() if (address and not pd.isna(address)) else ""
        url = str(url).strip() if (url and not pd.isna(url)) else ""

        # Parse city and state from address
        city, state = parse_city_state(address)

        # Parse phones
        phones = extract_phones(phone_raw)

        # If we have phones, insert one record per phone
        if phones:
            for phone in phones:
                records_to_insert.append({
                    "name": name,
                    "phone": phone,
                    "address": address,
                    "city": city,
                    "state": state,
                    "website": url,
                    "source_url": url,
                    "category": "Commerce",
                    "last_seen": now,
                })
        else:
            records_to_insert.append({
                "name": name,
                "phone": "",
                "address": address,
                "city": city,
                "state": state,
                "website": url,
                "source_url": url,
                "category": "Commerce",
                "last_seen": now,
            })

    print(f"  Prepared {len(records_to_insert)} records to insert.")

    # Save to SQLite database
    if records_to_insert:
        db.save_institutes_batch(records_to_insert)
        print(f"  [OK] Successfully imported {len(records_to_insert)} records into SQLite.")
    else:
        print("  [WARNING] No records were prepared for import.")

    print("=" * 60)


if __name__ == "__main__":
    run()
