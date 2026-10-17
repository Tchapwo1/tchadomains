"""
Unit Tests for TchaDomains DuckDB Storage Engine
"""

from datetime import date
from pathlib import Path
import pytest
from src.db.storage import DomainStore

@pytest.fixture
def temp_store(tmp_path):
    db_file = tmp_path / "test_tchadomains.duckdb"
    store = DomainStore(db_path=db_file)
    yield store
    store.close()

def test_insert_and_query_alpha(temp_store):
    sample_records = [
        {
            "domain_name": "payflow.com",
            "sld": "payflow",
            "tld": "com",
            "char_length": 7,
            "syllables": 2,
            "detected_words": ["pay", "flow"],
            "primary_category": "Fintech",
            "commercial_multiplier": 1.35,
            "alpha_score": 88.5
        },
        {
            "domain_name": "aihub.com",
            "sld": "aihub",
            "tld": "com",
            "char_length": 5,
            "syllables": 2,
            "detected_words": ["ai", "hub"],
            "primary_category": "AI",
            "commercial_multiplier": 1.4,
            "alpha_score": 94.5
        },
        {
            "domain_name": "junkstring.com",
            "sld": "junkstring",
            "tld": "com",
            "char_length": 10,
            "syllables": 2,
            "detected_words": ["junk", "string"],
            "primary_category": "General",
            "commercial_multiplier": 1.0,
            "alpha_score": 52.0
        }
    ]

    temp_store.insert_batch(sample_records, drop_date=date.today())
    results = temp_store.query_top_alpha(limit=10, min_score=80.0)

    assert len(results) == 2
    assert results[0]["domain_name"] == "aihub.com"
    assert results[0]["alpha_score"] == 94.5
    assert results[1]["domain_name"] == "payflow.com"

def test_watchlist_operations(temp_store):
    temp_store.add_to_watchlist("cloudpulse.com", notes="High target for SaaS flip", max_bid=100.0)
    watchlist = temp_store.get_watchlist()

    assert len(watchlist) == 1
    assert watchlist[0]["domain_name"] == "cloudpulse.com"
    assert watchlist[0]["max_bid_usd"] == 100.0
