"""
Stage 2: Website Discovery
Searches DuckDuckGo for each generated query and stores discovered URLs.
Supports resume — skips already-completed queries.
"""

import random
import sys
import time
from urllib.parse import urlparse

from ddgs import DDGS

import db
from config import (
    EXCLUDED_DOMAINS,
    SEARCH_DELAY_MAX,
    SEARCH_DELAY_MIN,
    SEARCH_MAX_RESULTS,
)
from stage1_queries import generate_queries


def _is_excluded(url: str) -> bool:
    """Check if a URL belongs to an excluded domain."""
    try:
        domain = urlparse(url).netloc.lower()
        # Check against excluded domains (including subdomains)
        for excluded in EXCLUDED_DOMAINS:
            if domain == excluded or domain.endswith("." + excluded):
                return True
        return False
    except Exception:
        return True


def _search_query(ddgs: DDGS, query_info: dict) -> list[dict]:
    """
    Search a single query and return discovered URLs.
    Returns list of dicts ready for db.save_urls_batch().
    """
    query = query_info["query"]
    city = query_info["city"]
    state = query_info["state"]
    category = query_info["category"]

    try:
        results = ddgs.text(query, max_results=SEARCH_MAX_RESULTS)
    except Exception as e:
        print(f"    ⚠ Search failed: {e}")
        return []

    urls = []
    for r in results:
        url = r.get("href", "")
        if not url or _is_excluded(url):
            continue
        urls.append({
            "url": url,
            "city": city,
            "state": state,
            "category": category,
            "query": query,
            "title": r.get("title", ""),
            "snippet": r.get("body", ""),
        })

    return urls


def run(limit: int = None):
    """
    Run Stage 2: Website Discovery.

    Args:
        limit: Max number of queries to process (None = all).
               Useful for testing with a small sample.
    """
    db.init_db()

    # Generate all queries
    all_queries = generate_queries()

    # Filter out already-completed queries (resume support)
    completed = db.get_completed_queries()
    pending = [q for q in all_queries if q["query"] not in completed]

    if limit:
        pending = pending[:limit]

    total = len(pending)
    skipped = len(all_queries) - len([q for q in all_queries if q["query"] not in completed])

    print("=" * 60)
    print("  STAGE 2: Website Discovery")
    print("=" * 60)
    print(f"  Total queries:     {len(all_queries)}")
    print(f"  Already completed: {skipped}")
    print(f"  Pending:           {total}")
    if limit:
        print(f"  Limit:             {limit}")
    print("=" * 60)

    if total == 0:
        print("\n  ✓ All queries already completed. Nothing to do.\n")
        return

    total_urls_found = 0

    with DDGS() as ddgs:
        for i, query_info in enumerate(pending, 1):
            query = query_info["query"]
            print(f"  [{i}/{total}] Searching: {query}", end="", flush=True)

            urls = _search_query(ddgs, query_info)

            if urls:
                db.save_urls_batch(urls)
                total_urls_found += len(urls)

            db.mark_query_complete(query, len(urls))
            print(f"  → {len(urls)} URLs")

            # Rate limiting — don't hammer the search engine
            if i < total:
                delay = random.uniform(SEARCH_DELAY_MIN, SEARCH_DELAY_MAX)
                time.sleep(delay)

    print(f"\n  ✓ Stage 2 complete.")
    print(f"    Queries processed: {total}")
    print(f"    URLs discovered:   {total_urls_found}")

    stats = db.get_stats()
    print(f"    Total URLs in DB:  {stats['urls_discovered']}\n")


if __name__ == "__main__":
    # Allow running with a limit: python stage2_discovery.py 10
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    run(limit=limit)
