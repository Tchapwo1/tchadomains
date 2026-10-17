# 🛠️ Pillar 2: Technical Requirements Document (TRD) — TchaDomains

## 1. Technical Stack & Architecture
- **Language**: Python 3.10+ (core data processing, linguistic analysis, scoring, and CLI) and modern Node.js/TypeScript (Web UI backend or static fast server).
- **Analytical Storage Engine**: **DuckDB / SQLite 3** with WAL mode and in-memory columnar execution for microsecond queries across 150,000 daily drop rows.
- **Linguistic Engine**: Custom Aho-Corasick / Trie compound word tokenizer paired with a curated English frequency dictionary (30,000 common words + 1,500 high-intent commercial keywords).
- **Asynchronous Network Resolver**: `httpx` + `dnspython` for non-blocking RDAP (Registration Data Access Protocol) and DNS NS resolution to verify real-time status.
- **Web UI Engine**: Zero-bloat HTTP server on port 5520 serving an ultra-dense, responsive dashboard styled with `oklch` CSS variables, glassmorphism, and vanilla ES modules.

---

## 2. Strict Performance & Resource Budgets
| Metric | Budget Target | Rationale |
|---|---|---|
| **Memory Footprint** | **< 80 MB RAM** | Runs quietly as a background radar without impacting laptop performance. |
| **Ingest Throughput** | **> 40,000 domains/sec** | A 120,000-domain drop file must ingest and normalize in under 3.0 seconds. |
| **Scoring Latency** | **< 2.5s for 100k domains** | Instant ranking allows the user to act before competitor scrapers. |
| **HUD Load Time** | **< 150ms** | Keyboard-driven tactical terminal & web dashboard with zero hydration delay. |
| **Local Disk Storage** | **< 45 MB per 30 days** | Compressed DuckDB / Parquet storage for rolling 30-day drop logs. |

---

## 3. Mandatory File Tree Contract
```
tchadomains/
├── package.json              # Node dependencies (UI server, tailwind if needed)
├── requirements.txt          # Python dependencies (duckdb, httpx, rich)
├── README.md                 # Project manifesto & quickstart
├── specs/
│   ├── 01_PRD.md
│   ├── 02_TRD.md
│   ├── 03_APP_FLOW.md
│   ├── 04_UI_UX.md
│   ├── 05_SCHEMA.md
│   └── 06_IMPLEMENTATION_PLAN.md
├── data/
│   ├── dictionary/
│   │   ├── words.txt         # 30k English root words for compound tokenization
│   │   └── commercial.json   # High-intent keyword weights (fintech, ai, saas)
│   ├── raw/                  # Daily drop feed downloads (cached .txt/.gz)
│   └── tchadomains.duckdb    # Analytical domain storage & watchlists
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── ingest.py         # Pulls Verisign daily drop list & marketplace feeds
│   │   ├── filter_engine.py  # Filters hyphens, digits, spam, length bounds
│   │   ├── tokenizer.py      # Compound word & syllable decomposition
│   │   ├── scorer.py         # Mathematical Tcha Alpha Valuation Engine (0-100)
│   │   └── resolver.py       # Asynchronous RDAP / DNS live status checker
│   ├── db/
│   │   ├── __init__.py
│   │   └── storage.py        # DuckDB / SQLite connection, queries, migrations
│   ├── cli/
│   │   ├── __init__.py
│   │   └── radar_cli.py      # Rich terminal UI with colorized alpha table
│   └── ui/
│       ├── __init__.py
│       ├── server.py         # HTTP server on port 5520 with REST endpoints
│       └── public/
│           ├── index.html    # Domainer Tactical HUD
│           ├── style.css     # oklch obsidian palette, micro-elevations, dark mode
│           └── app.js        # Keyboard shortcuts, filters, affiliate links
└── tests/
    ├── test_filter.py
    ├── test_tokenizer.py
    ├── test_scorer.py
    └── test_storage.py
```
