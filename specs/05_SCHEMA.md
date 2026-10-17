# 🗄️ Pillar 5: Data Schema & Valuation Mathematics — TchaDomains

## 1. Storage Schema (DuckDB / SQLite 3)

### Table 1: `dropping_domains`
Stores all parsed and scored candidate domains from the daily drop feeds:

```sql
CREATE TABLE IF NOT EXISTS dropping_domains (
    id VARCHAR(64) PRIMARY KEY,           -- MD5(domain_name + drop_date)
    domain_name VARCHAR(128) NOT NULL,    -- e.g. 'cloudpulse.com'
    sld VARCHAR(64) NOT NULL,             -- e.g. 'cloudpulse'
    tld VARCHAR(16) NOT NULL,             -- e.g. 'com'
    char_length INTEGER NOT NULL,         -- Length of sld (excluding .com)
    syllable_count INTEGER NOT NULL,      -- Estimated pronounceable syllables
    word_count INTEGER NOT NULL,          -- Number of detected English words
    detected_words JSON,                  -- ['cloud', 'pulse']
    primary_category VARCHAR(32),         -- 'AI', 'Fintech', 'DevTools', 'Brandable', 'General'
    commercial_multiplier REAL DEFAULT 1.0,
    alpha_score REAL NOT NULL,            -- Final score from 0.0 to 100.0
    status VARCHAR(32) DEFAULT 'DROPPING',-- 'DROPPING', 'PENDING_DELETE', 'AVAILABLE', 'ACQUIRED'
    drop_date DATE NOT NULL,              -- Scheduled deletion date
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dropping_score ON dropping_domains(alpha_score DESC);
CREATE INDEX idx_dropping_date ON dropping_domains(drop_date);
CREATE INDEX idx_dropping_cat ON dropping_domains(primary_category);
CREATE INDEX idx_dropping_len ON dropping_domains(char_length);
```

### Table 2: `watchlists`
Stores the user's bookmarked domains with personal notes and alert thresholds:

```sql
CREATE TABLE IF NOT EXISTS watchlists (
    domain_name VARCHAR(128) PRIMARY KEY,
    notes TEXT,
    max_bid_usd REAL DEFAULT 50.0,
    target_registrar VARCHAR(64) DEFAULT 'Namecheap',
    is_acquired BOOLEAN DEFAULT FALSE,
    acquisition_price_usd REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Table 3: `daily_ingest_metrics`
Tracks historical ingestion throughput and drop volume:

```sql
CREATE TABLE IF NOT EXISTS daily_ingest_metrics (
    drop_date DATE PRIMARY KEY,
    raw_drops_count INTEGER NOT NULL,
    clean_candidates_count INTEGER NOT NULL,
    alpha_gems_count INTEGER NOT NULL,     -- Score >= 80
    ingest_duration_ms INTEGER NOT NULL,
    scoring_duration_ms INTEGER NOT NULL
);
```

---

## 2. The Tcha Alpha Score Mathematical Formula ($0 - 100$)

The score combines 4 orthogonal vectors:

$$\text{AlphaScore} = \min\left(100, \left( w_{\text{len}} \cdot S_{\text{len}} + w_{\text{ling}} \cdot S_{\text{ling}} + w_{\text{comm}} \cdot S_{\text{comm}} + w_{\text{tld}} \cdot S_{\text{tld}} \right)\right)$$

### 1. Length Sub-Score ($S_{\text{len}}$) — Weight: $0.30$
- $L = \text{length of SLD}$:
  - If $L \le 4$: $S_{\text{len}} = 100$
  - If $L = 5$: $S_{\text{len}} = 90$
  - If $L = 6$: $S_{\text{len}} = 80$
  - If $L = 7$: $S_{\text{len}} = 70$
  - If $L = 8$: $S_{\text{len}} = 55$
  - If $L = 9$: $S_{\text{len}} = 40$
  - If $L = 10$: $S_{\text{len}} = 25$
  - If $L > 10$: $S_{\text{len}} = \max(0, 25 - 5 \cdot (L - 10))$

### 2. Linguistic & Brandability Sub-Score ($S_{\text{ling}}$) — Weight: $0.25$
- Evaluates syllable rhythm and dictionary composition:
  - Valid 1-word dictionary noun/verb: $+100$ points.
  - Valid 2-word clean compound (e.g. `payflow`): $+85$ points.
  - Pronounceable CVCV non-dictionary name (e.g. `zulu`, `bivo`): $+75$ points.
  - 3+ compound words: $-30$ point penalty.

### 3. Commercial Intent & Niche Sub-Score ($S_{\text{comm}}$) — Weight: $0.35$
- Evaluates industry buyer demand and CPC value:
  - Category A (Fintech, AI, Security): Keywords `pay`, `ai`, `agent`, `shield`, `token`, `bank`, `flow`, `vault` $\rightarrow S_{\text{comm}} = 100$.
  - Category B (SaaS, Cloud, Data): Keywords `cloud`, `data`, `stack`, `sync`, `grid`, `core`, `ops` $\rightarrow S_{\text{comm}} = 85$.
  - Category C (General Commerce): Keywords `shop`, `direct`, `market`, `deal`, `hub` $\rightarrow S_{\text{comm}} = 70$.
  - Uncategorized standard words: $S_{\text{comm}} = 40$.

### 4. TLD Extension Prestige ($S_{\text{tld}}$) — Weight: $0.10$
- `.com`: $100$
- `.ai`: $95$
- `.io`: $85$
- `.co`: $75$
- `.net`: $65$
- Others: $40$
