"""
Stage 3: Contact Extraction
Fetches each discovered URL and extracts institute name, phone, and address.
Uses Google's phonenumbers library for robust Indian phone number detection.
"""

import random
import re
import sys
import time

import phonenumbers
import requests
from bs4 import BeautifulSoup

import db
from config import (
    ADDRESS_INDICATORS,
    COMMERCE_KEYWORDS,
    EXTRACT_DELAY_MAX,
    EXTRACT_DELAY_MIN,
    IRRELEVANT_NAME_KEYWORDS,
    JUNK_ADDRESS_PHRASES,
    JUNK_TITLE_PHRASES,
    REQUEST_HEADERS,
    REQUEST_TIMEOUT,
)


# ─── Phone Extraction ───────────────────────────────────────────────

def _extract_phones(text: str) -> list[str]:
    """
    Extract Indian phone numbers from text using Google's phonenumbers library.
    Returns deduplicated list of formatted phone strings.
    """
    phones = set()

    # Use PhoneNumberMatcher for robust extraction
    for match in phonenumbers.PhoneNumberMatcher(text, "IN"):
        number = match.number
        if phonenumbers.is_valid_number(number):
            formatted = phonenumbers.format_number(
                number, phonenumbers.PhoneNumberFormat.E164
            )
            phones.add(formatted)

    # Fallback: simple regex for common Indian patterns that phonenumbers might miss
    # Matches: +91XXXXXXXXXX, 91XXXXXXXXXX, 0XX-XXXXXXXX, XXXXXXXXXX (10 digits starting 6-9)
    mobile_pattern = r'(?<!\d)(?:\+?91[-.\s]?)?([6-9]\d{9})(?!\d)'
    for m in re.findall(mobile_pattern, text):
        try:
            parsed = phonenumbers.parse(m, "IN")
            if phonenumbers.is_valid_number(parsed):
                formatted = phonenumbers.format_number(
                    parsed, phonenumbers.PhoneNumberFormat.E164
                )
                phones.add(formatted)
        except phonenumbers.NumberParseException:
            pass

    return list(phones)


# ─── Name Extraction ────────────────────────────────────────────────

def _extract_name(soup: BeautifulSoup, url: str) -> str:
    """Extract the institute name from the page."""
    candidates = []

    # 1. Try og:title meta tag
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        candidates.append(og_title["content"].strip())

    # 2. Try <title> tag
    title_tag = soup.find("title")
    if title_tag and title_tag.string:
        title = title_tag.string.strip()
        # Remove common suffixes like " | Home", " - Official Website"
        for sep in [" | ", " - ", " – ", " — ", " :: "]:
            if sep in title:
                title = title.split(sep)[0].strip()
        if title:
            candidates.append(title)

    # 3. Try first <h1>
    h1 = soup.find("h1")
    if h1:
        h1_text = h1.get_text(strip=True)
        if h1_text and len(h1_text) < 150:
            candidates.append(h1_text)

    # 4. Try schema.org name
    schema_name = soup.find("meta", {"itemprop": "name"})
    if schema_name and schema_name.get("content"):
        candidates.append(schema_name["content"].strip())

    # Return the best candidate (prefer og:title, then title, then h1)
    for name in candidates:
        if name and len(name) > 2:
            return name[:200]  # Cap length

    return ""


# ─── Address Extraction ─────────────────────────────────────────────

def _extract_address(soup: BeautifulSoup) -> str:
    """Extract address from the page using multiple strategies."""
    candidates = []

    # 1. Try <address> HTML tag
    address_tag = soup.find("address")
    if address_tag:
        text = address_tag.get_text(separator=" ", strip=True)
        if text and len(text) > 10:
            candidates.append(text)

    # 2. Try schema.org PostalAddress
    for tag in soup.find_all(attrs={"itemtype": re.compile(r"PostalAddress", re.I)}):
        text = tag.get_text(separator=" ", strip=True)
        if text and len(text) > 10:
            candidates.append(text)

    # 3. Try elements with "address" in class or id
    for attr in ["class", "id"]:
        for el in soup.find_all(attrs={attr: re.compile(r"address", re.I)}):
            text = el.get_text(separator=" ", strip=True)
            if text and 10 < len(text) < 500:
                candidates.append(text)

    # 4. Look for text near "Address" label
    for label_text in ["Address:", "Address", "Our Address", "Office Address",
                       "Location:", "Location", "Visit Us"]:
        label = soup.find(string=re.compile(re.escape(label_text), re.I))
        if label:
            parent = label.parent
            if parent:
                # Check next sibling or parent's next sibling
                next_el = parent.find_next_sibling()
                if next_el:
                    text = next_el.get_text(separator=" ", strip=True)
                    if text and 10 < len(text) < 500:
                        candidates.append(text)
                # Also try the parent's full text
                parent_text = parent.get_text(separator=" ", strip=True)
                # Remove the label itself
                addr = parent_text.replace(label_text, "").strip()
                if addr and 10 < len(addr) < 500:
                    candidates.append(addr)

    # 5. Try meta description as last resort for address-like content
    # (some simple sites put address in meta)

    # Return the best candidate (shortest reasonable one is usually most precise)
    candidates = [_clean_text(c) for c in candidates if c]
    candidates = [c for c in candidates if len(c) > 10 and not _is_junk_text(c)]

    valid_candidates = []
    for c in candidates:
        if _is_junk_address(c):
            continue
        c_lower = c.lower()
        # Must have pin code OR address indicator
        has_pin = bool(re.search(r'\b\d{6}\b', c))
        has_indicator = any(ind in c_lower for ind in ADDRESS_INDICATORS)
        if has_pin or has_indicator:
            valid_candidates.append(c)

    if valid_candidates:
        valid_candidates.sort(key=len)
        return valid_candidates[0][:500]

    return ""


# ─── Utilities ───────────────────────────────────────────────────────

def _is_junk_text(text: str) -> bool:
    """Detect if text is JavaScript, CSS, or other non-content junk."""
    if not text:
        return True
    junk_indicators = [
        "function(", "function (", "var ", "const ", "let ",
        "jQuery", "$(document)", "window.location", "document.get",
        "addEventListener", "createElement", "innerHTML",
        "sessionStorage", "localStorage", "console.log",
        ".css(", ".js", "http://", "https://",
        "{", "}", "=>", "===", "!==" ,
        "@media", "@import", "@keyframes",
    ]
    text_lower = text.lower()
    junk_count = sum(1 for ind in junk_indicators if ind.lower() in text_lower)
    # If multiple junk indicators found, it's likely code
    if junk_count >= 2:
        return True
    # If text has too many special characters relative to its length
    special = sum(1 for c in text if c in '{}();=<>$')
    if len(text) > 0 and special / len(text) > 0.05:
        return True
    return False


def _is_junk_address(text: str) -> bool:
    """Check if 'address' text is actually junk UI text, not a real address."""
    if not text:
        return False  # Empty is fine, just means no address found
    text_lower = text.lower()
    for phrase in JUNK_ADDRESS_PHRASES:
        if phrase.lower() in text_lower:
            return True
    return False


def _is_relevant(name: str, page_text: str) -> bool:
    """
    Check if a page is actually about a commerce coaching institute.
    At least one COMMERCE_KEYWORD must appear in the name or page text.
    Rejects immediately if an IRRELEVANT_NAME_KEYWORD or JUNK_TITLE_PHRASE appears in the name.
    """
    name_lower = name.lower()
    for keyword in IRRELEVANT_NAME_KEYWORDS:
        if keyword.lower() in name_lower:
            return False

    for phrase in JUNK_TITLE_PHRASES:
        if phrase.lower() in name_lower:
            return False

    combined = (name + " " + page_text).lower()
    for keyword in COMMERCE_KEYWORDS:
        if keyword.lower() in combined:
            return True
    return False


def _clean_text(text: str) -> str:
    """Clean extracted text: normalize whitespace, remove excess newlines."""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def _fetch_page(url: str) -> BeautifulSoup | None:
    """Fetch a URL and return parsed BeautifulSoup, or None on failure."""
    try:
        resp = requests.get(
            url,
            headers=REQUEST_HEADERS,
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True,
        )
        resp.raise_for_status()

        # Only process HTML content
        content_type = resp.headers.get("Content-Type", "")
        if "text/html" not in content_type and "application/xhtml" not in content_type:
            return None

        return BeautifulSoup(resp.text, "lxml")
    except requests.RequestException:
        return None
    except Exception:
        return None


# ─── Main Extraction ────────────────────────────────────────────────

def extract_from_url(url_record: dict) -> list[dict]:
    """
    Extract institute information from a single URL.
    Returns a list of institute dicts (usually 1, but could be 0).
    """
    url = url_record["url"]
    soup = _fetch_page(url)

    if not soup:
        return []

    # Remove script and style tags before text extraction
    for tag in soup.find_all(["script", "style", "noscript"]):
        tag.decompose()

    # Get the full page text for phone extraction
    page_text = soup.get_text(separator=" ")

    name = _extract_name(soup, url)
    phones = _extract_phones(page_text)
    address = _extract_address(soup)

    # Validate: skip junk data
    if _is_junk_text(address) or _is_junk_address(address):
        address = ""
    if _is_junk_text(name):
        name = ""

    # If we didn't find a name and no phone, skip this URL
    if not name and not phones:
        return []

    # STRICT: skip if the page is not about commerce coaching
    if not _is_relevant(name, page_text):
        return []

    # Create one record per phone number found, or one with no phone if we have a name
    records = []

    if phones:
        for phone in phones:
            records.append({
                "name": name,
                "phone": phone,
                "address": address,
                "city": url_record.get("city", ""),
                "state": url_record.get("state", ""),
                "website": url,
                "source_url": url,
                "category": url_record.get("category", ""),
            })
    elif name:
        records.append({
            "name": name,
            "phone": "",
            "address": address,
            "city": url_record.get("city", ""),
            "state": url_record.get("state", ""),
            "website": url,
            "source_url": url,
            "category": url_record.get("category", ""),
        })

    return records


def run(limit: int = None):
    """
    Run Stage 3: Contact Extraction.

    Args:
        limit: Max number of URLs to process (None = all).
    """
    db.init_db()

    pending = db.get_unscraped_urls(limit=limit)
    total = len(pending)

    stats = db.get_stats()

    print("=" * 60)
    print("  STAGE 3: Contact Extraction")
    print("=" * 60)
    print(f"  Total URLs in DB:    {stats['urls_discovered']}")
    print(f"  Already scraped:     {stats['urls_scraped']}")
    print(f"  Pending:             {total}")
    if limit:
        print(f"  Limit:               {limit}")
    print("=" * 60)

    if total == 0:
        print("\n  ✓ No pending URLs to scrape.\n")
        return

    extracted_count = 0
    failed_count = 0

    for i, url_record in enumerate(pending, 1):
        url = url_record["url"]
        # Truncate URL for display
        display_url = url[:60] + "..." if len(url) > 63 else url
        print(f"  [{i}/{total}] {display_url}", end="", flush=True)

        records = extract_from_url(url_record)

        if records:
            db.save_institutes_batch(records)
            extracted_count += len(records)
            print(f"  → {len(records)} record(s)")
        else:
            failed_count += 1
            print(f"  → no data")

        db.mark_scraped(url_record["id"])

        # Rate limiting
        if i < total:
            delay = random.uniform(EXTRACT_DELAY_MIN, EXTRACT_DELAY_MAX)
            time.sleep(delay)

    print(f"\n  ✓ Stage 3 complete.")
    print(f"    URLs processed:     {total}")
    print(f"    Records extracted:  {extracted_count}")
    print(f"    URLs with no data:  {failed_count}\n")


if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    run(limit=limit)
