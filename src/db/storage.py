"""
TchaDomains Analytical Storage Engine (DuckDB)
Manages dropping domains, watchlists, and daily ingest telemetry.
"""

import duckdb
import hashlib
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Optional, Any

DB_PATH = Path("data/tchadomains.duckdb")

class DomainStore:
    def __init__(self, db_path: Optional[Path] = None, read_only: bool = False):
        self.db_path = db_path or DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self.conn = duckdb.connect(str(self.db_path), read_only=read_only)
            self.read_only = read_only
            if not read_only:
                self.init_schema()
        except (duckdb.IOException, Exception):
            # Fallback to read-only mode if write lock is held by another process
            self.conn = duckdb.connect(str(self.db_path), read_only=True)
            self.read_only = True

    def init_schema(self):
        """Creates the DuckDB tables as specified in Pillar 5."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS dropping_domains (
                id VARCHAR PRIMARY KEY,
                domain_name VARCHAR NOT NULL,
                sld VARCHAR NOT NULL,
                tld VARCHAR NOT NULL,
                char_length INTEGER NOT NULL,
                syllable_count INTEGER NOT NULL,
                word_count INTEGER NOT NULL,
                detected_words VARCHAR,
                primary_category VARCHAR,
                commercial_multiplier DOUBLE,
                alpha_score DOUBLE NOT NULL,
                status VARCHAR DEFAULT 'DROPPING',
                drop_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS watchlists (
                domain_name VARCHAR PRIMARY KEY,
                notes VARCHAR,
                max_bid_usd DOUBLE DEFAULT 50.0,
                target_registrar VARCHAR DEFAULT 'Namecheap',
                is_acquired BOOLEAN DEFAULT FALSE,
                acquisition_price_usd DOUBLE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS daily_ingest_metrics (
                drop_date DATE PRIMARY KEY,
                raw_drops_count INTEGER NOT NULL,
                clean_candidates_count INTEGER NOT NULL,
                alpha_gems_count INTEGER NOT NULL,
                ingest_duration_ms INTEGER NOT NULL,
                scoring_duration_ms INTEGER NOT NULL
            );
        """)

    def insert_batch(self, scored_domains: List[Dict], drop_date: date):
        """Batch inserts scored domain candidates efficiently."""
        if not scored_domains:
            return

        records = []
        for d in scored_domains:
            # MD5 hash of domain_name + drop_date for primary key
            pk = hashlib.md5(f"{d['domain_name']}_{drop_date}".encode()).hexdigest()
            words_str = ",".join(d.get("detected_words", []))
            records.append((
                pk,
                d["domain_name"],
                d["sld"],
                d["tld"],
                d["char_length"],
                d.get("syllables", 1),
                len(d.get("detected_words", [])),
                words_str,
                d.get("primary_category", "General"),
                d.get("commercial_multiplier", 1.0),
                d["alpha_score"],
                "DROPPING",
                drop_date,
                datetime.now()
            ))

        self.conn.executemany("""
            INSERT OR REPLACE INTO dropping_domains (
                id, domain_name, sld, tld, char_length, syllable_count,
                word_count, detected_words, primary_category, commercial_multiplier,
                alpha_score, status, drop_date, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, records)

    def query_top_alpha(
        self,
        limit: int = 50,
        min_score: float = 70.0,
        max_length: int = 10,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Queries highest scoring dropping domains matching filters."""
        query = """
            SELECT 
                domain_name, sld, tld, char_length, syllable_count,
                detected_words, primary_category, commercial_multiplier,
                alpha_score, status, drop_date
            FROM dropping_domains
            WHERE alpha_score >= ? AND char_length <= ?
        """
        params = [min_score, max_length]

        if category and category.lower() != "all":
            query += " AND primary_category = ?"
            params.append(category)

        query += " ORDER BY alpha_score DESC, char_length ASC LIMIT ?"
        params.append(limit)

        result = self.conn.execute(query, params).fetchall()
        columns = [
            "domain_name", "sld", "tld", "char_length", "syllable_count",
            "detected_words", "primary_category", "commercial_multiplier",
            "alpha_score", "status", "drop_date"
        ]
        return [dict(zip(columns, row)) for row in result]

    def add_to_watchlist(self, domain_name: str, notes: str = "", max_bid: float = 50.0):
        """Adds a domain to the user's personal watchlist."""
        self.conn.execute("""
            INSERT OR REPLACE INTO watchlists (domain_name, notes, max_bid_usd, created_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """, [domain_name, notes, max_bid])

    def get_watchlist(self) -> List[Dict]:
        """Returns all domains currently watchlisted."""
        result = self.conn.execute("SELECT * FROM watchlists ORDER BY created_at DESC").fetchall()
        columns = ["domain_name", "notes", "max_bid_usd", "target_registrar", "is_acquired", "acquisition_price_usd", "created_at"]
        return [dict(zip(columns, row)) for row in result]

    def close(self):
        self.conn.close()
