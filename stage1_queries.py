"""
Stage 1: Query Generator
Generates search queries from the cartesian product of cities × categories × templates.
"""

from cities import get_cities, get_city_count
from config import CATEGORIES, QUERY_TEMPLATES
import db


def generate_queries() -> list[dict]:
    """
    Generate all search queries.
    Returns list of dicts: {query, city, state, category}
    """
    cities = get_cities()
    queries = []

    for city_info in cities:
        city = city_info["city"]
        state = city_info["state"]
        for category in CATEGORIES:
            for template in QUERY_TEMPLATES:
                query_text = template.format(category=category, city=city)
                queries.append({
                    "query": query_text,
                    "city": city,
                    "state": state,
                    "category": category,
                })

    return queries


def run():
    """Run Stage 1: Generate and display query stats."""
    db.init_db()

    cities_count = get_city_count()
    categories_count = len(CATEGORIES)
    templates_count = len(QUERY_TEMPLATES)

    queries = generate_queries()
    total = len(queries)

    print("=" * 60)
    print("  STAGE 1: Query Generator")
    print("=" * 60)
    print(f"  Cities:     {cities_count}")
    print(f"  Categories: {categories_count} ({', '.join(CATEGORIES)})")
    print(f"  Templates:  {templates_count}")
    print(f"  ─────────────────────────────")
    print(f"  Total queries: {total}")
    print("=" * 60)

    # Show sample queries
    print("\n  Sample queries:")
    for q in queries[:10]:
        print(f"    • {q['query']}")
    if total > 10:
        print(f"    ... and {total - 10} more")

    print(f"\n  ✓ Stage 1 complete. {total} queries ready for discovery.\n")
    return queries


if __name__ == "__main__":
    run()
