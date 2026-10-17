# 📋 Pillar 1: Product Requirements Document (PRD) — TchaDomains

## 1. Executive Summary & Value Proposition
**TchaDomains** is a high-velocity, personal domain intelligence radar and dropping-list discovery engine. It automates the daily ingestion of expiring `.com`, `.net`, and high-value ccTLDs, filters out 99% of junk (hyphenated names, numeric spam, trademark hazards), scores every candidate domain using the proprietary **Tcha Alpha Valuation Formula ($0 - 100$)**, and presents the top high-intent, brandable domain assets through an ultra-fast tactical domainer HUD.

It bridges the gap between mining undervalued domains to flip for high ROI and serving as the foundational engine for a next-generation SaaS competitor to legacy, cluttered platforms like `ExpiredDomains.net`.

---

## 2. Target Persona & Core Problem
- **Persona**: Domain investors, startup founders, indie builders, and acquisition specialists hunting for high-intent, short, brandable, or high-SEO domain names.
- **Pain Point**: Over 100,000 domains drop every single day at 2:00 PM EST (Verisign drop cycle). Legacy tools (such as `ExpiredDomains.net`) are plagued with 2004-era table interfaces, slow pagination, heavy Cloudflare anti-bot blocks, no algorithmic commercial scoring, and zero modern workflow automation.
- **Core Promise**: Ingest, filter, and score 100,000+ dropping domains in under 3 seconds; rank and surface the top 20–50 high-alpha domain assets daily with 1-click registrar availability verification and affiliate routing.

---

## 3. Scope & MVP Features

### Feature 1: Automated Daily Drop Feed Ingest Engine
- Automatically ingests daily drop lists:
  - **Verisign Pending Delete Lists**: Daily `.com` and `.net` deletions (100k–150k names/day).
  - **Dynadot / GoDaddy Closeout Feeds**: Expired auctions and direct marketplace closeouts.
  - **Local Caching & Delta Diffing**: Avoids redundant processing and tracks day-over-day drop trends.

### Feature 2: High-Speed Noise Filter & Linguistic Tokenizer
- Rejects 99% of deadweight candidates instantly:
  - Strict exclusion of hyphens (`-`), numbers/digits, and consecutive identical consonants.
  - Length filter: Strict focus on $\le 10$ characters (with priority given to 4, 5, 6-letter dot-coms).
  - Lexical Tokenizer: Deconstructs compound names (e.g. `cloudguard`, `paypulse`) into recognized root words using an embedded frequency dictionary.

### Feature 3: Tcha Alpha Valuation Engine ($0 - 100$)
- Proprietary algorithmic scoring:
  - **Length Score (30%)**: Exponential decay penalty as character count increases.
  - **Pronounceability & Syllables (25%)**: Alternating consonant-vowel patterns (CVCV) for high brandability.
  - **Commercial Intent & Niche Multipliers (35%)**: High-CPC keywords (e.g. `pay`, `ai`, `agent`, `flow`, `shield`, `cloud`, `hub`, `data`).
  - **TLD Prestige (10%)**: Premium multiplier for `.com`, followed by `.ai`, `.io`, `.co`.

### Feature 4: Domainer Tactical HUD (CLI & Web Dashboard)
- **Terminal Radar (`python -m src.cli.radar_cli`)**: High-density, colored table ranking today's top alpha drops with keyboard navigation.
- **Tactical Web Visualizer (`http://localhost:5520`)**:
  - Dark-mode domainer interface (`oklch` obsidian palette with gold alpha highlights).
  - Keyboard traversal (`J`/`K` navigation, `Enter` to check registrar, `B` to bookmark).
  - Instant live search and category filtering (Fintech, AI Agents, DevTools, Clean Short).
  - 1-click registrar lookup with user affiliate tracking tags.

---

## 4. Out-of-Scope (Non-Goals for v1.0)
- Processing the complete 350M-record full ICANN CZDS zone file on local laptop SSD (deferred to v2.0 cloud cluster).
- Direct automated drop-catching backorder bidding bots (which require \$10,000+ registrar escrow deposits with DropCatch/NameJet).
- Automated trademark dispute filing or legal escrow management.
