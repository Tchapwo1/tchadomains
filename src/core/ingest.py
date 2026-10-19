"""
TchaDomains Ingestion & Normalizer Pipeline
Ingests daily Verisign drop lists, extracts candidates, scores them,
and writes directly into DuckDB.
"""

import time
import random
from datetime import date
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import httpx

from src.core.filter_engine import FilterEngine
from src.core.scorer import AlphaScorer
from src.db.storage import DomainStore

RAW_DIR = Path("data/raw")

class IngestPipeline:
    def __init__(self, store: DomainStore = None):
        self.store = store or DomainStore()
        self.filter = FilterEngine(max_length=10)
        self.scorer = AlphaScorer()
        RAW_DIR.mkdir(parents=True, exist_ok=True)

    def process_domain_list(self, raw_domains: List[str], drop_date: date = None) -> Dict:
        """
        Takes a list of raw domain names, filters out noise, scores candidates,
        and persists to DuckDB.
        """
        drop_date = drop_date or date.today()
        start_time = time.time()

        raw_count = len(raw_domains)
        candidates = []
        for domain in raw_domains:
            valid, _ = self.filter.is_candidate(domain)
            if valid:
                candidates.append(domain)

        filter_time = time.time()
        scored_records = []
        for domain in candidates:
            score_data = self.scorer.score(domain)
            scored_records.append(score_data)

        score_time = time.time()
        self.store.insert_batch(scored_records, drop_date=drop_date)
        total_time = time.time() - start_time

        alpha_gems = [d for d in scored_records if d["alpha_score"] >= 80.0]

        return {
            "drop_date": str(drop_date),
            "raw_count": raw_count,
            "candidates_count": len(candidates),
            "alpha_gems_count": len(alpha_gems),
            "filter_duration_ms": round((filter_time - start_time) * 1000),
            "score_duration_ms": round((score_time - filter_time) * 1000),
            "total_duration_ms": round(total_time * 1000),
            "throughput_domains_per_sec": round(raw_count / max(0.001, total_time)),
            "top_gem": alpha_gems[0]["domain_name"] if alpha_gems else None
        }

    def sync_daily_drops(self, drop_date: Optional[date] = None, force_refresh: bool = False) -> Dict:
        """
        Pulls the live or cached dropping feed for the date, parses, scores, and updates DuckDB.
        """
        from src.core.drop_stream import fetch_daily_drops
        target_date = drop_date or date.today()
        raw_stream = fetch_daily_drops(target_date=target_date, force_refresh=force_refresh)
        return self.process_domain_list(raw_stream, drop_date=target_date)

    def generate_benchmark_feed(self, count: int = 50000) -> List[str]:
        """
        Generates a realistic benchmark drop stream containing:
        - 15% high-intent commercial keywords (e.g. cloudpulse, payflow, agentguard)
        - 10% 4-6 letter brandable CVCVs (e.g. luma, zulu, viva, fidu)
        - 50% noisy strings with hyphens and digits (e.g. auto-repair123.com)
        - 25% long general names (e.g. bestresidentialplumbingnearme.com)
        """
        commercial_stems = [
            "pay", "coin", "token", "vault", "cloud", "data", "stack", "sync",
            "agent", "ai", "flow", "shield", "guard", "code", "dev", "fast",
            "pulse", "nexus", "core", "mesh", "node", "mind", "bot", "fund"
        ]
        cvcv_consonants = ["b", "c", "d", "f", "g", "k", "l", "m", "n", "p", "r", "s", "t", "v", "z"]
        cvcv_vowels = ["a", "e", "i", "o", "u"]
        general_words = ["house", "water", "tree", "river", "road", "stone", "star", "light", "blue", "green"]

        domains = []
        for _ in range(count):
            dice = random.random()
            if dice < 0.15:
                # High-value 2-word commercial dot-com
                w1 = random.choice(commercial_stems)
                w2 = random.choice(commercial_stems + general_words)
                domains.append(f"{w1}{w2}.com")
            elif dice < 0.25:
                # CVCV or CVCVC brandable
                c1, c2, c3 = random.choice(cvcv_consonants), random.choice(cvcv_consonants), random.choice(cvcv_consonants)
                v1, v2 = random.choice(cvcv_vowels), random.choice(cvcv_vowels)
                domains.append(f"{c1}{v1}{c2}{v2}.com")
            elif dice < 0.70:
                # Noisy hyphen/digit domain (to be weeded out)
                domains.append(f"service-{random.randint(10, 9999)}-deal.com")
            else:
                # Long multi-word domain
                domains.append(f"best{random.choice(general_words)}online{random.randint(1, 99)}.com")

        return domains
