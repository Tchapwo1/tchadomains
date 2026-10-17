/**
 * TchaDomains Tactical HUD Client Application
 * Full keyboard-driven domainer terminal and real-time radar feed.
 */

let allDomains = [];
let focusedRowIndex = -1;
let activeCategory = 'all';

// DOM Elements
const domainsBody = document.getElementById('domainsBody');
const metricTotal = document.getElementById('metricTotal');
const metricGems = document.getElementById('metricGems');
const metricAvgScore = document.getElementById('metricAvgScore');
const cycleDate = document.getElementById('cycleDate');
const resultsCount = document.getElementById('resultsCount');
const searchInput = document.getElementById('searchInput');
const minScoreSlider = document.getElementById('minScoreSlider');
const minScoreLabel = document.getElementById('minScoreLabel');
const maxLenSelect = document.getElementById('maxLenSelect');
const categoryPills = document.getElementById('categoryPills');
const btnWatchlistToggle = document.getElementById('btnWatchlistToggle');
const watchlistModal = document.getElementById('watchlistModal');
const btnCloseWatchlist = document.getElementById('btnCloseWatchlist');
const watchlistBody = document.getElementById('watchlistBody');
const watchlistCount = document.getElementById('watchlistCount');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  fetchStats();
  fetchDrops();
  fetchWatchlist();
  setupEventListeners();
  setupKeyboardNavigation();
});

// Fetch Global Stats
async function fetchStats() {
  try {
    const res = await fetch('/api/stats');
    const data = await res.json();
    metricTotal.textContent = data.total_dropping.toLocaleString();
    metricGems.textContent = data.alpha_gems.toLocaleString();
    metricAvgScore.textContent = data.avg_alpha_score.toFixed(1);
    if (data.cycle_date) {
      cycleDate.textContent = data.cycle_date;
    }
  } catch (err) {
    console.error('Failed to load stats:', err);
  }
}

// Fetch Candidate Drops
async function fetchDrops() {
  const minScore = minScoreSlider.value;
  const maxLen = maxLenSelect.value;
  
  domainsBody.innerHTML = `
    <tr>
      <td colspan="7" class="loading-state">
        <div class="spinner"></div> Scanning dropping candidate feeds...
      </td>
    </tr>
  `;

  try {
    const url = `/api/drops?min_score=${minScore}&max_len=${maxLen}&category=${activeCategory}&limit=100`;
    const res = await fetch(url);
    const data = await res.json();
    allDomains = data.domains || [];
    renderTable();
  } catch (err) {
    domainsBody.innerHTML = `
      <tr>
        <td colspan="7" class="empty-state">
          ⚠️ Failed to reach radar server. Please ensure server is running.
        </td>
      </tr>
    `;
  }
}

// Render Table Rows
function renderTable() {
  const query = searchInput.value.trim().toLowerCase();
  const filtered = allDomains.filter(d => {
    if (!query) return true;
    return d.domain_name.toLowerCase().includes(query) || 
           (d.detected_words && d.detected_words.toLowerCase().includes(query));
  });

  resultsCount.textContent = `${filtered.length} candidates`;

  if (filtered.length === 0) {
    domainsBody.innerHTML = `
      <tr>
        <td colspan="7" class="empty-state">
          🔍 No domains match your active filters. Try lowering Min Score or loosening length constraints.
        </td>
      </tr>
    `;
    focusedRowIndex = -1;
    return;
  }

  let html = '';
  filtered.forEach((d, idx) => {
    const score = d.alpha_score.toFixed(1);
    let badgeClass = 'score-slate';
    let icon = '';
    if (d.alpha_score >= 85) {
      badgeClass = 'score-gold';
      icon = '★ ';
    } else if (d.alpha_score >= 75) {
      badgeClass = 'score-emerald';
      icon = '◆ ';
    }

    const words = d.detected_words ? d.detected_words.split(',').join(' + ') : '—';
    const affiliateUrl = `https://namecheap.pxf.io/c/tcha/${d.domain_name}`;

    html += `
      <tr data-index="${idx}" data-domain="${d.domain_name}" class="${idx === focusedRowIndex ? 'row-focused' : ''}">
        <td style="color: var(--color-text-dim);">${idx + 1}</td>
        <td>
          <span class="domain-name">${d.domain_name}</span>
        </td>
        <td>
          <span class="alpha-score-badge ${badgeClass}">${icon}${score}</span>
        </td>
        <td style="font-family: var(--font-mono); color: var(--color-text-dim);">${d.char_length}</td>
        <td>
          <span class="niche-tag">${d.primary_category}</span>
        </td>
        <td class="words-list">${words}</td>
        <td style="text-align: right;">
          <button class="btn-bookmark" title="Bookmark (B)" onclick="toggleWatchlist('${d.domain_name}', event)">★</button>
          <a href="${affiliateUrl}" target="_blank" rel="noopener noreferrer" class="btn-buy">
            Check Registrar ➔
          </a>
        </td>
      </tr>
    `;
  });

  domainsBody.innerHTML = html;
  attachRowClickHandlers();
}

// Row Click Handlers
function attachRowClickHandlers() {
  const rows = domainsBody.querySelectorAll('tr[data-index]');
  rows.forEach(row => {
    row.addEventListener('click', () => {
      const idx = parseInt(row.dataset.index, 10);
      setFocusRow(idx);
    });
  });
}

function setFocusRow(index) {
  const rows = domainsBody.querySelectorAll('tr[data-index]');
  if (rows.length === 0) return;

  if (index < 0) index = 0;
  if (index >= rows.length) index = rows.length - 1;

  rows.forEach(r => r.classList.remove('row-focused'));
  focusedRowIndex = index;
  const target = rows[index];
  if (target) {
    target.classList.add('row-focused');
    target.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
  }
}

// Keyboard Navigation
function setupKeyboardNavigation() {
  window.addEventListener('keydown', (e) => {
    // If active element is input, only allow Escape
    if (document.activeElement === searchInput) {
      if (e.key === 'Escape') {
        searchInput.blur();
      }
      return;
    }

    if (e.key === '/' && document.activeElement !== searchInput) {
      e.preventDefault();
      searchInput.focus();
      return;
    }

    if (e.key === 'j' || e.key === 'ArrowDown') {
      e.preventDefault();
      setFocusRow(focusedRowIndex + 1);
    } else if (e.key === 'k' || e.key === 'ArrowUp') {
      e.preventDefault();
      setFocusRow(focusedRowIndex - 1);
    } else if (e.key === 'Enter') {
      const focusedRow = domainsBody.querySelector('tr.row-focused');
      if (focusedRow) {
        const domain = focusedRow.dataset.domain;
        if (domain) {
          window.open(`https://namecheap.pxf.io/c/tcha/${domain}`, '_blank');
        }
      }
    } else if (e.key === 'b' || e.key === 'B') {
      const focusedRow = domainsBody.querySelector('tr.row-focused');
      if (focusedRow) {
        const domain = focusedRow.dataset.domain;
        if (domain) toggleWatchlist(domain);
      }
    } else if (e.key === 'w' || e.key === 'W') {
      toggleWatchlistModal();
    }
  });
}

// Watchlist API
async function toggleWatchlist(domain, event) {
  if (event) event.stopPropagation();
  try {
    await fetch('/api/watchlist', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ domain_name: domain, max_bid: 50.0 })
    });
    fetchWatchlist();
  } catch (err) {
    console.error('Failed to bookmark domain:', err);
  }
}

async function fetchWatchlist() {
  try {
    const res = await fetch('/api/watchlist');
    const data = await res.json();
    const list = data.watchlist || [];
    watchlistCount.textContent = list.length;

    if (list.length === 0) {
      watchlistBody.innerHTML = `<tr><td colspan="4" class="empty-state">No domains bookmarked yet. Press B on any row.</td></tr>`;
      return;
    }

    watchlistBody.innerHTML = list.map(item => `
      <tr>
        <td class="domain-name">${item.domain_name}</td>
        <td>${item.target_registrar}</td>
        <td>$${item.max_bid_usd}</td>
        <td>
          <a href="https://namecheap.pxf.io/c/tcha/${item.domain_name}" target="_blank" class="btn-buy">Buy</a>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    console.error('Failed to load watchlist:', err);
  }
}

function toggleWatchlistModal() {
  watchlistModal.classList.toggle('hidden');
}

// Event Listeners
function setupEventListeners() {
  searchInput.addEventListener('input', () => {
    renderTable();
  });

  minScoreSlider.addEventListener('input', (e) => {
    minScoreLabel.textContent = e.target.value;
    fetchDrops();
  });

  maxLenSelect.addEventListener('change', () => {
    fetchDrops();
  });

  categoryPills.querySelectorAll('.pill').forEach(pill => {
    pill.addEventListener('click', () => {
      categoryPills.querySelectorAll('.pill').forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      activeCategory = pill.dataset.category;
      fetchDrops();
    });
  });

  btnWatchlistToggle.addEventListener('click', toggleWatchlistModal);
  btnCloseWatchlist.addEventListener('click', toggleWatchlistModal);
  watchlistModal.addEventListener('click', (e) => {
    if (e.target === watchlistModal) toggleWatchlistModal();
  });
}
