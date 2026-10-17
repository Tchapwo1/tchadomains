# 🎯 TchaDomains (Tactical Domain Radar)

**TchaDomains** is a high-velocity, lightweight personal domain intelligence radar and dropping-list discovery engine. Built to outperform cluttered legacy tools like `ExpiredDomains.net`, it continuously filters out 99% of deadweight dropping names, decomposes compound words, calculates syllable pronounceability, and ranks high-intent digital real estate using the proprietary **Tcha Alpha Valuation Formula ($0 - 100$)**.

---

## ⚡ Key Features

- **Ingest Pipeline**: Capable of processing 50,000+ dropping domain records in seconds.
- **Strict Noise Filter**: Discards hyphens, numbers, non-alphanumeric chars, repeated consonants, and strings $>10$ characters.
- **Linguistic Compound Tokenizer**: Decomposes SLDs (e.g., `cloudpulse` ➔ `['cloud', 'pulse']`, `payflow` ➔ `['pay', 'flow']`) using a 9,500-word English root lexicon and high-intent commercial keyword weights.
- **Tcha Alpha Valuation Formula**: Evaluates Length (30%), Linguistic Harmony (25%), Commercial Intent (35%), and TLD Prestige (10%).
- **DuckDB Columnar Store**: Analytical SQL engine executing Top-Alpha ranking queries in under 15ms.
- **Tactical Domainer Terminal HUD**: Rich terminal interface with color-graded alpha badges.
- **Cyber-Domainer Web Dashboard (Port 5520)**: High-density dark mode HUD with keyboard traversal (`J`/`K` navigation, `Enter` checkout, `B` bookmark, `/` search).

---

## 🚀 Quickstart

### 1. Requirements
Ensure Python 3.10+ is installed:
```bash
pip install -r requirements.txt
```

### 2. Run the Terminal Radar CLI
Inspect today's top dropping alpha candidates:
```bash
python -m src.cli.radar_cli --limit 25 --min-score 75
```

Filter by commercial niche:
```bash
python -m src.cli.radar_cli --category AI --limit 15
python -m src.cli.radar_cli --category Fintech --limit 15
```

### 3. Launch the Tactical Web HUD
Start the local dashboard server:
```bash
python -m src.ui.server
```
Then open `http://localhost:5520` in your browser.

---

## ⌨️ Tactical HUD Keyboard Shortcuts

| Key | Action |
|---|---|
| `J` or `↓` | Move focus to next domain row |
| `K` or `↑` | Move focus to previous domain row |
| `Enter` | Open primary registrar lookup / checkout |
| `B` | Bookmark domain to local Watchlist |
| `/` | Instantly focus search bar |
| `W` | Toggle Watchlist Drawer |
| `Esc` | Blur search / close modal |

---

## 🧪 Testing

Run the automated test suite:
```bash
pytest tests -v
```
All 7 unit tests covering filter rejection, compound tokenization, CVCV brandable detection, scoring hierarchy, and DuckDB storage execute in $<1.0$s.

---

## 🛡️ License
Copyright (c) 2026 Tcha. All rights reserved.
Part of the Tcha ecosystem.
