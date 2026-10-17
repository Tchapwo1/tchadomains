# 🎨 Pillar 4: UI / UX Design Specification — TchaDomains

## 1. Visual Identity & Palette ("Cyber-Domainer HUD")
TchaDomains adopts a tactical, high-finance dark mode theme with obsidian base surfaces, translucent glass borders, and vivid functional accents designed for long trading sessions:

```css
:root {
  /* Surfaces */
  --color-bg-base: oklch(0.12 0.02 260);        /* Deep Obsidian background */
  --color-bg-surface: oklch(0.16 0.03 260 / 0.85); /* Frosted card surface */
  --color-border: oklch(1 0 0 / 0.08);          /* Translucent hair-line border */
  
  /* Alpha & Status Accents */
  --color-gold-alpha: oklch(0.85 0.18 85);       /* Vivid Gold for top-tier Alpha scores (>=85) */
  --color-emerald-avail: oklch(0.72 0.18 150);   /* Emerald green for verified dropping/available */
  --color-crimson-taken: oklch(0.65 0.22 25);    /* Crimson for backordered / taken */
  --color-cyan-radar: oklch(0.75 0.14 210);      /* Cyan for radar scanner telemetry */
  --color-violet-niche: oklch(0.70 0.18 290);    /* Violet for category tags (AI, Fintech) */

  /* Typography */
  --color-text-main: oklch(0.98 0 0);           /* Bright crisp white */
  --color-text-muted: oklch(0.65 0.02 260);     /* Secondary parameter slate */
}
```

---

## 2. Typography & Numerical Stability
- **Headings & Body**: `Inter`, `-apple-system`, `system-ui`, sans-serif.
- **Data Table, Scores & Short Cuts**: `JetBrains Mono`, `SF Mono`, `Consolas`, monospace.
- **Mandatory Numeric Rule**:
  ```css
  .metric-value, .alpha-score, .domain-length, .drop-countdown {
    font-variant-numeric: tabular-nums;
  }
  ```
  Prevents layout shifts during real-time filtering and scrolling.

---

## 3. Surface Polish & Micro-Elevations
- **Concentric Radius System**:
  - Outer container / HUD wrapper: `border-radius: 14px;`
  - Table rows & action cards: `border-radius: 8px;`
  - Filter pills & score badges: `border-radius: 6px;`
- **Subtle Layered Glow on Alpha Picks**:
  ```css
  .alpha-badge-high {
    background: oklch(0.85 0.18 85 / 0.15);
    border: 1px solid oklch(0.85 0.18 85 / 0.4);
    box-shadow: 0 0 12px oklch(0.85 0.18 85 / 0.2);
    color: var(--color-gold-alpha);
  }
  ```

---

## 4. Keyboard-First Domainer Ergonomics
Every critical workflow is accessible without touching the mouse:
- `J` / `↓`: Move focus to the next domain row.
- `K` / `↑`: Move focus to the previous domain row.
- `Enter`: Open primary registrar checkout (Namecheap/Cloudflare with affiliate tag).
- `B`: Toggle bookmark into local personal watchlist.
- `/`: Instantly focus the filter/search bar.
- `R`: Reset all filters to default.
- `Space`: Open RDAP details drawer for the currently focused domain.
