"""
Pipeline CLI — Main entry point for the Commerce Coaching Institute Scraper.

Usage:
    python pipeline.py --stage all         # Run full pipeline
    python pipeline.py --stage queries     # Stage 1: Generate queries
    python pipeline.py --stage discover    # Stage 2: Website discovery
    python pipeline.py --stage extract     # Stage 3: Contact extraction
    python pipeline.py --stage dedup       # Stage 4: Deduplication
    python pipeline.py --stage export      # Export to CSV/JSON
    python pipeline.py --stats             # Show pipeline statistics
    python pipeline.py --stage discover --limit 10   # Test with 10 queries
"""

import argparse
import sys

import db


def print_stats():
    """Print pipeline statistics."""
    db.init_db()
    stats = db.get_stats()

    print()
    print("=" * 60)
    print("  PIPELINE STATISTICS")
    print("=" * 60)
    print(f"  Queries completed:     {stats['queries_completed']}")
    print(f"  ─────────────────────────────")
    print(f"  URLs discovered:       {stats['urls_discovered']}")
    print(f"  URLs scraped:          {stats['urls_scraped']}")
    print(f"  URLs pending:          {stats['urls_pending']}")
    print(f"  ─────────────────────────────")
    print(f"  Institutes (total):    {stats['institutes_total']}")
    print(f"  Institutes (unique):   {stats['institutes_unique']}")
    print(f"  Institutes (dupes):    {stats['institutes_duplicates']}")

    if stats["by_category"]:
        print(f"  ─────────────────────────────")
        print(f"  By Category:")
        for cat, count in stats["by_category"].items():
            print(f"    {cat:25s} {count}")

    if stats["top_cities"]:
        print(f"  ─────────────────────────────")
        print(f"  Top Cities:")
        for city, count in stats["top_cities"].items():
            print(f"    {city:25s} {count}")

    print("=" * 60)
    print()


def run_stage(stage: str, limit: int = None):
    """Run a specific pipeline stage."""
    if stage == "queries":
        from stage1_queries import run
        run()

    elif stage == "discover":
        from stage2_discovery import run
        run(limit=limit)

    elif stage == "extract":
        from stage3_extraction import run
        run(limit=limit)

    elif stage == "dedup":
        from stage4_dedup import run
        run()

    elif stage == "export":
        from export import run
        run()

    elif stage == "all":
        print("\n" + "━" * 60)
        print("  RUNNING FULL PIPELINE")
        print("━" * 60 + "\n")

        from stage1_queries import run as run_queries
        run_queries()

        from stage2_discovery import run as run_discover
        run_discover(limit=limit)

        from stage3_extraction import run as run_extract
        run_extract(limit=limit)

        from stage4_dedup import run as run_dedup
        run_dedup()

        from export import run as run_export
        run_export()

        print_stats()
    else:
        print(f"  ✗ Unknown stage: {stage}")
        print("  Valid stages: queries, discover, extract, dedup, export, all")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Commerce Coaching Institute Scraper Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pipeline.py --stage all              Run full pipeline
  python pipeline.py --stage queries          Generate search queries
  python pipeline.py --stage discover         Run website discovery
  python pipeline.py --stage discover --limit 10  Test with 10 queries
  python pipeline.py --stage extract          Extract contact info
  python pipeline.py --stage extract --limit 50   Extract from 50 URLs
  python pipeline.py --stage dedup            Deduplicate records
  python pipeline.py --stage export           Export to CSV/JSON
  python pipeline.py --stats                  Show pipeline statistics
        """,
    )

    parser.add_argument(
        "--stage",
        choices=["all", "queries", "discover", "extract", "dedup", "export"],
        help="Pipeline stage to run",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show pipeline statistics",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit the number of items to process (for testing)",
    )

    args = parser.parse_args()

    if not args.stage and not args.stats:
        parser.print_help()
        sys.exit(0)

    if args.stats:
        print_stats()

    if args.stage:
        run_stage(args.stage, limit=args.limit)


if __name__ == "__main__":
    main()
