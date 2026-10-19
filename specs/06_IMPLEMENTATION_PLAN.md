# 📅 Pillar 6: Implementation Plan & Definition of Done — TchaDomains

## 1. Chronological Roadmap & Milestones

### Milestone 1: Feed Ingestion & Normalizer Engine
- **Tasks**:
  1. Author `src/core/ingest.py`: Automated download and local streaming decompression of Verisign daily `.com` / `.net` pending-delete lists.
  2. Implement local fallback cache mechanism if network is unreachable.
- **Definition of Done**: Successfully streams and decompresses 100k+ drop records in $<2.0$ seconds without memory bloat.

---

### Milestone 2: Filtering & High-Speed Tokenizer
- **Tasks**:
  1. Author `src/core/filter_engine.py`: Instant rejection of hyphens, digits, repeated consonants, and names $>10$ characters.
  2. Author `src/core/tokenizer.py`: Triaged dictionary matching using `data/dictionary/words.txt` and `data/dictionary/commercial.json` to decompose compounds and calculate syllable metrics.
- **Definition of Done**: 100k raw names filtered down to $\sim$5,000–8,000 clean candidates in $<1.5$ seconds.

---

### Milestone 3: Tcha Alpha Valuation Engine ($0 - 100$)
- **Tasks**:
  1. Author `src/core/scorer.py`: Implements the 4-part weighted scoring formula ($S_{\text{len}}, S_{\text{ling}}, S_{\text{comm}}, S_{\text{tld}}$).
  2. Tag each candidate with primary commercial categories (`AI`, `Fintech`, `DevTools`, `Brandable`).
- **Definition of Done**: Unit tests verify that high-value names (`payflow.com`, `agentshield.com`) score $>90$, while obscure strings (`xzkpq.com`) score $<30$.

---

### Milestone 4: Analytical Storage & Query Layer (DuckDB / SQLite)
- **Tasks**:
  1. Author `src/db/storage.py`: Schema creation, batch inserts with transaction wrapping, and indexed retrieval functions.
  2. Support querying top $N$ alpha domains filtered by max length and category.
- **Definition of Done**: Querying Top 50 Alpha domains executes in $<15$ milliseconds.

---

### Milestone 5: Domainer Terminal Radar (CLI)
- **Tasks**:
  1. Author `src/cli/radar_cli.py`: Rich terminal interface displaying the live drop radar table with colorized score badges.
  2. Include CLI flags: `--top 50`, `--niche ai`, `--max-len 6`, `--min-score 80`.
- **Definition of Done**: Running `python -m src.cli.radar_cli` renders a clean, styled radar terminal in $<0.5$ seconds.

---

### Milestone 6: Domainer Tactical Web Visualizer (Port 5520)
- **Tasks**:
  1. Author `src/ui/server.py`: Lightweight HTTP server on port 5520 serving static assets and JSON endpoints (`/api/drops`, `/api/watchlist`).
  2. Author `src/ui/public/` (`index.html`, `style.css`, `app.js`):
     - Tactical dark-mode DOM with obsidian glass surfaces.
     - Full keyboard navigation (`J`/`K` navigation, `Enter` checkout, `B` bookmark).
     - Direct affiliate links into Namecheap/Cloudflare registration.
- **Definition of Done**: Web dashboard loads at `http://localhost:5520` with instant reactivity and zero console errors.

---

### Milestone 7: Automated Test Suite & Verification (COMPLETED)
- **Tasks**:
  1. Author `tests/test_filter.py`, `tests/test_tokenizer.py`, `tests/test_scorer.py`, `tests/test_storage.py`.
  2. Verify performance budgets: Total RAM $<80$ MB, scoring throughput $>40,000$ names/sec.
- **Definition of Done**: 100% of test suites pass cleanly in $<1.0$ second.

---

### Milestone 8: Automated Daily Alpha Drops Dispatcher (Telegram & Email) (COMPLETED)
- **Tasks**:
  1. Author `src/dispatch/telegram_notifier.py`: High-priority Telegram alert bot with rich Markdown formatting, Alpha badges, and 1-click registrar lookup URLs. (Done)
  2. Author `src/dispatch/email_dispatcher.py`: Museum-grade dark-mode responsive HTML email newsletter template (*The Daily Tcha*) with tabular valuation metrics and SMTP/TLS delivery. (Done)
  3. Author `src/dispatch/alert_dispatcher.py`: Pipeline coordinator extracting top 5 AI + top 5 Fintech alpha drops from DuckDB, executing dual dispatch. (Done)
  4. Author CLI runner with `--channel [both|telegram|email]` and `--dry-run` modes. (Done)
  5. Author `tests/test_dispatcher.py` to verify formatting, payload assembly, and mock dispatch delivery. (Done)
- **Definition of Done**: Automated dispatch generates verified Telegram & Email dispatches for Top 10 AI/Fintech drops in $<500$ms. (Achieved: 454ms)
