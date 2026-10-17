# 🔄 Pillar 3: Application Flow & Mandatory States — TchaDomains

## 1. End-to-End Radar Flow
```
[User or Daily Schedule (2:00 PM EST)]
       │
       ├──> $ python -m src.core.ingest --source verisign
       │         │
       │         ├──> Downloads raw dropping file (e.g. 110,000 domains)
       │         ├──> Passes raw names through filter_engine (discards hyphens, digits, >10 chars)
       │         │    └── Result: ~8,000 clean candidates
       │         ├──> Tokenizes names with dictionary/commercial weights
       │         ├──> Computes Tcha Alpha Score (0 - 100) for each candidate
       │         └──> Stores in tchadomains.duckdb with indexed drop timestamp
       │
       ├──> $ python -m src.cli.radar_cli --top 50
       │         │
       │         ├──> Loads top 50 ranked dropping names from local DB
       │         ├──> Renders high-density Rich terminal HUD (Score, Name, Length, Words, Niche)
       │         └──> Interactive prompt: Check RDAP, bookmark to watchlist, or export
       │
       └──> $ python -m src.ui.server --port 5520
                 │
                 └──> Spawns Tactical Web Visualizer at http://localhost:5520
                      ├── Interactive filter: Length <= 6, Score >= 80, Category = Fintech/AI
                      ├── Keyboard navigation: [J]/[K] to move, [Enter] to check registrar
                      └── Direct affiliate redirect to registrar checkout (Namecheap/Cloudflare)
```

---

## 2. The 4 Mandatory UI & Terminal States

### State 1: Ingesting & Scoring (In Progress)
- **Terminal**: Animated Rich progress bar showing ingestion throughput and candidate filtering:
  `[RADAR ACTIVE] Ingested 112,400 raw drops ➔ 8,140 clean candidates ➔ Scored in 1.84s`
- **Web UI**: Pulsing gold radar sweep indicator; live metric counters updating with `tabular-nums`.

### State 2: Populated / High-Alpha State (Primary Operation)
- **View**: Dense, sorted ledger showing rank, domain name, Alpha Score ($0-100$), length, detected root words, commercial niche tag (AI, Fintech, DevTools, General), and direct Action button.
- **Microcopy**: *"50 Alpha Opportunities detected for drop cycle 2026-10-17. Top pick: `cloudpulse.com` (Score: 94)."*

### State 3: Empty State (No Candidates Found)
- **Trigger**: User applies ultra-restrictive filters (e.g. Length $\le 4$ and Score $\ge 95$ on a day with no 4-letter drops).
- **Web UI & Terminal**:
  `🔍 No domains match your active filter criteria. Loosen length constraints (try <= 7 characters) or explore all dropping categories.`
- **Action**: 1-click button or shortcut `[R]` to Reset Filters.

### State 4: Error & Network Recovery State
- **Triggers**: Verisign drop feed endpoint unreachable, offline network, or RDAP registrar rate limit hit.
- **Handling**:
  - Automatically falls back to the most recent cached daily drop file.
  - Displays non-blocking warning badge: `⚠️ Offline Mode: Showing cached drop inventory from 2026-10-16. Next sync attempt in 5m.`
  - RDAP requests implement exponential backoff with jitter and token bucket rate-limiting (max 10 req/sec).
