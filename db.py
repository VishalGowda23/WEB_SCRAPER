"""
SQLite database manager for the scraper pipeline.
Handles schema creation, CRUD operations, and resume tracking.
"""

import os
import sqlite3
from datetime import datetime, timezone

from config import DATA_DIR, DB_PATH


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    """Get a database connection with WAL mode for better concurrency."""
    _ensure_data_dir()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Create all tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS discovered_urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL,
            source TEXT DEFAULT 'duckduckgo',
            city TEXT,
            state TEXT,
            category TEXT,
            query TEXT,
            title TEXT,
            snippet TEXT,
            scraped INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS institutes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            address TEXT,
            city TEXT,
            state TEXT,
            website TEXT,
            source_url TEXT,
            category TEXT,
            is_duplicate INTEGER DEFAULT 0,
            duplicate_of INTEGER,
            last_seen TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS completed_queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT UNIQUE NOT NULL,
            results_count INTEGER DEFAULT 0,
            completed_at TEXT DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_discovered_urls_scraped
            ON discovered_urls(scraped);
        CREATE INDEX IF NOT EXISTS idx_institutes_phone
            ON institutes(phone);
        CREATE INDEX IF NOT EXISTS idx_institutes_name_city
            ON institutes(name, city);
        CREATE INDEX IF NOT EXISTS idx_institutes_duplicate
            ON institutes(is_duplicate);
    """)

    conn.commit()
    conn.close()


# ─── Discovered URLs (Stage 2) ──────────────────────────────────────

def save_url(url: str, city: str, state: str, category: str,
             query: str, title: str = None, snippet: str = None):
    """Save a discovered URL. Silently skips duplicates."""
    conn = get_connection()
    try:
        conn.execute(
            """INSERT OR IGNORE INTO discovered_urls
               (url, city, state, category, query, title, snippet)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (url, city, state, category, query, title, snippet)
        )
        conn.commit()
    finally:
        conn.close()


def save_urls_batch(urls: list[dict]):
    """Save multiple discovered URLs in a single transaction."""
    conn = get_connection()
    try:
        conn.executemany(
            """INSERT OR IGNORE INTO discovered_urls
               (url, city, state, category, query, title, snippet)
               VALUES (:url, :city, :state, :category, :query, :title, :snippet)""",
            urls
        )
        conn.commit()
    finally:
        conn.close()


def get_unscraped_urls(limit: int = None) -> list[dict]:
    """Get URLs that haven't been scraped yet."""
    conn = get_connection()
    try:
        query = "SELECT * FROM discovered_urls WHERE scraped = 0"
        if limit:
            query += f" LIMIT {limit}"
        rows = conn.execute(query).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def mark_scraped(url_id: int):
    """Mark a URL as scraped."""
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE discovered_urls SET scraped = 1 WHERE id = ?",
            (url_id,)
        )
        conn.commit()
    finally:
        conn.close()


# ─── Institutes (Stage 3) ───────────────────────────────────────────

def save_institute(name: str, phone: str, address: str, city: str,
                   state: str, website: str, source_url: str,
                   category: str) -> int:
    """Save an institute record. Returns the new row ID."""
    conn = get_connection()
    now = datetime.now(timezone.utc).isoformat()
    try:
        cursor = conn.execute(
            """INSERT INTO institutes
               (name, phone, address, city, state, website, source_url,
                category, last_seen)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (name, phone, address, city, state, website, source_url,
             category, now)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def save_institutes_batch(records: list[dict]):
    """Save multiple institute records in a single transaction."""
    conn = get_connection()
    now = datetime.now(timezone.utc).isoformat()
    try:
        for r in records:
            r.setdefault("last_seen", now)
        conn.executemany(
            """INSERT INTO institutes
               (name, phone, address, city, state, website, source_url,
                category, last_seen)
               VALUES (:name, :phone, :address, :city, :state, :website,
                       :source_url, :category, :last_seen)""",
            records
        )
        conn.commit()
    finally:
        conn.close()


def get_all_institutes(include_duplicates: bool = False) -> list[dict]:
    """Get all institutes, optionally excluding duplicates."""
    conn = get_connection()
    try:
        if include_duplicates:
            rows = conn.execute("SELECT * FROM institutes").fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM institutes WHERE is_duplicate = 0"
            ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def mark_duplicate(institute_id: int, duplicate_of: int):
    """Mark an institute as a duplicate of another."""
    conn = get_connection()
    try:
        conn.execute(
            """UPDATE institutes
               SET is_duplicate = 1, duplicate_of = ?
               WHERE id = ?""",
            (duplicate_of, institute_id)
        )
        conn.commit()
    finally:
        conn.close()


# ─── Completed Queries (Resume Support) ─────────────────────────────

def mark_query_complete(query: str, results_count: int):
    """Mark a search query as completed."""
    conn = get_connection()
    try:
        conn.execute(
            """INSERT OR IGNORE INTO completed_queries
               (query, results_count)
               VALUES (?, ?)""",
            (query, results_count)
        )
        conn.commit()
    finally:
        conn.close()


def get_completed_queries() -> set[str]:
    """Get the set of all completed query strings."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT query FROM completed_queries"
        ).fetchall()
        return {row["query"] for row in rows}
    finally:
        conn.close()


# ─── Statistics ──────────────────────────────────────────────────────

def get_stats() -> dict:
    """Get pipeline statistics."""
    conn = get_connection()
    try:
        stats = {}

        row = conn.execute("SELECT COUNT(*) as c FROM completed_queries").fetchone()
        stats["queries_completed"] = row["c"]

        row = conn.execute("SELECT COUNT(*) as c FROM discovered_urls").fetchone()
        stats["urls_discovered"] = row["c"]

        row = conn.execute(
            "SELECT COUNT(*) as c FROM discovered_urls WHERE scraped = 1"
        ).fetchone()
        stats["urls_scraped"] = row["c"]

        row = conn.execute(
            "SELECT COUNT(*) as c FROM discovered_urls WHERE scraped = 0"
        ).fetchone()
        stats["urls_pending"] = row["c"]

        row = conn.execute("SELECT COUNT(*) as c FROM institutes").fetchone()
        stats["institutes_total"] = row["c"]

        row = conn.execute(
            "SELECT COUNT(*) as c FROM institutes WHERE is_duplicate = 0"
        ).fetchone()
        stats["institutes_unique"] = row["c"]

        row = conn.execute(
            "SELECT COUNT(*) as c FROM institutes WHERE is_duplicate = 1"
        ).fetchone()
        stats["institutes_duplicates"] = row["c"]

        # Breakdown by category
        rows = conn.execute(
            """SELECT category, COUNT(*) as c FROM institutes
               WHERE is_duplicate = 0
               GROUP BY category ORDER BY c DESC"""
        ).fetchall()
        stats["by_category"] = {row["category"]: row["c"] for row in rows}

        # Breakdown by city (top 20)
        rows = conn.execute(
            """SELECT city, COUNT(*) as c FROM institutes
               WHERE is_duplicate = 0
               GROUP BY city ORDER BY c DESC LIMIT 20"""
        ).fetchall()
        stats["top_cities"] = {row["city"]: row["c"] for row in rows}

        return stats
    finally:
        conn.close()
