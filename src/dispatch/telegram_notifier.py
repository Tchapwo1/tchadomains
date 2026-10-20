"""
TchaDomains Telegram Alert Notifier
Formats and dispatches high-priority domain drop alerts via Telegram Bot API.
"""

import os
import logging
from datetime import date
from typing import List, Dict, Optional, Any
from pathlib import Path
import httpx

logger = logging.getLogger("tchadomains.telegram")

def load_env_file():
    """Reads .env file from project root if present."""
    env_path = Path(".env")
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = val

def build_registrar_links(domain: str) -> str:
    """Generates direct 1-click registration/lookup links."""
    namecheap_url = f"https://www.namecheap.com/domains/registration/results/?domain={domain}"
    dynadot_url = f"https://www.dynadot.com/domain/search.html?domain={domain}"
    return f"[Namecheap]({namecheap_url}) • [Dynadot]({dynadot_url})"

def build_due_diligence_links(domain: str) -> str:
    """Generates direct 1-click audit links for historical spam, Wayback archives, and Google Index status."""
    wayback_url = f"https://web.archive.org/web/*/{domain}"
    google_url = f"https://www.google.com/search?q=site:{domain}"
    return f"[Wayback Archive]({wayback_url}) • [Google Index]({google_url})"

def build_inline_keyboard(
    ai_domains: List[Dict[str, Any]],
    fintech_domains: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Constructs Telegram inline buttons for 1-click bidding and 1-tap DuckDB watchlisting.
    """
    keyboard = []

    # Top AI #1
    if ai_domains:
        d = ai_domains[0]
        name = d.get("domain_name", "")
        bid_url = f"https://www.namecheap.com/domains/registration/results/?domain={name}"
        keyboard.append([
            {"text": f"⚡ Bid {name}", "url": bid_url},
            {"text": f"⭐ Save {name}", "callback_data": f"watch:{name}"}
        ])

    # Top Fintech #1
    if fintech_domains:
        d = fintech_domains[0]
        name = d.get("domain_name", "")
        bid_url = f"https://www.namecheap.com/domains/registration/results/?domain={name}"
        keyboard.append([
            {"text": f"💳 Bid {name}", "url": bid_url},
            {"text": f"⭐ Save {name}", "callback_data": f"watch:{name}"}
        ])

    # Top AI #2
    if len(ai_domains) > 1:
        d = ai_domains[1]
        name = d.get("domain_name", "")
        bid_url = f"https://www.namecheap.com/domains/registration/results/?domain={name}"
        keyboard.append([
            {"text": f"🤖 Bid {name}", "url": bid_url},
            {"text": f"⭐ Save {name}", "callback_data": f"watch:{name}"}
        ])

    # Top Fintech #2
    if len(fintech_domains) > 1:
        d = fintech_domains[1]
        name = d.get("domain_name", "")
        bid_url = f"https://www.namecheap.com/domains/registration/results/?domain={name}"
        keyboard.append([
            {"text": f"💎 Bid {name}", "url": bid_url},
            {"text": f"⭐ Save {name}", "callback_data": f"watch:{name}"}
        ])

    # Universal actions
    keyboard.append([
        {"text": "📋 My Watchlist", "callback_data": "cmd:watchlist"},
        {"text": "🔄 Refresh Top 10", "callback_data": "cmd:refresh"}
    ])

    return {"inline_keyboard": keyboard}

def format_telegram_message(
    ai_domains: List[Dict[str, Any]],
    fintech_domains: List[Dict[str, Any]],
    drop_date: Optional[str] = None
) -> str:
    """
    Constructs a scannable, rich Markdown alert for Telegram.
    Separates drops into AI and Fintech clusters with score badges and 1-click links.
    """
    drop_date_str = drop_date or str(date.today())
    total_count = len(ai_domains) + len(fintech_domains)

    lines = [
        "⚡ *TchaDomains • Daily Alpha Drops Dispatch*",
        f"📅 *Drop Date:* `{drop_date_str}` | *Top {total_count} Opportunities*",
        "Proprietary Alpha Score (0–100) based on syllable harmony, high-CPC buyer intent & TLD prestige.",
        "",
        "━━━━━━━━━━━━━━━━━━━━━━",
        "🤖 *TOP AI & AGENT INFRASTRUCTURE DROPS*",
        "━━━━━━━━━━━━━━━━━━━━━━"
    ]

    if not ai_domains:
        lines.append("_(No high-conviction AI drops meeting alpha threshold today)_")
    else:
        for i, d in enumerate(ai_domains, 1):
            name = d.get("domain_name", "")
            score = d.get("alpha_score", 0.0)
            chars = d.get("char_length", len(name.split(".")[0]))
            words = d.get("detected_words", "")
            if isinstance(words, list):
                words = " + ".join(words)
            elif not words:
                words = "single/brandable"
            else:
                words = words.replace(",", " + ")

            links = build_registrar_links(name)
            audit = build_due_diligence_links(name)
            lines.append(f"*{i}.* `{name}` — *[{score:.1f}/100]*")
            lines.append(f"   ↳ {chars} chars | Structure: _{words}_")
            lines.append(f"   ↳ Quick Bid: {links}")
            lines.append(f"   ↳ Audit: {audit}")
            lines.append("")

    lines.extend([
        "━━━━━━━━━━━━━━━━━━━━━━",
        "💳 *TOP FINTECH & FINANCIAL RAILS DROPS*",
        "━━━━━━━━━━━━━━━━━━━━━━"
    ])

    if not fintech_domains:
        lines.append("_(No high-conviction Fintech drops meeting alpha threshold today)_")
    else:
        for i, d in enumerate(fintech_domains, 1):
            name = d.get("domain_name", "")
            score = d.get("alpha_score", 0.0)
            chars = d.get("char_length", len(name.split(".")[0]))
            words = d.get("detected_words", "")
            if isinstance(words, list):
                words = " + ".join(words)
            elif not words:
                words = "single/brandable"
            else:
                words = words.replace(",", " + ")

            links = build_registrar_links(name)
            audit = build_due_diligence_links(name)
            lines.append(f"*{i}.* `{name}` — *[{score:.1f}/100]*")
            lines.append(f"   ↳ {chars} chars | Structure: _{words}_")
            lines.append(f"   ↳ Quick Bid: {links}")
            lines.append(f"   ↳ Audit: {audit}")
            lines.append("")

    lines.extend([
        "━━━━━━━━━━━━━━━━━━━━━━",
        "💡 *Tcha Tip:* Domains drop between 18:00–20:00 UTC (Verisign cycle).",
        "🔗 *Live Radar:* http://localhost:5520"
    ])

    return "\n".join(lines)

def send_telegram_alert(
    message: str,
    bot_token: Optional[str] = None,
    chat_id: Optional[str] = None,
    reply_markup: Optional[Dict[str, Any]] = None,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Dispatches alert to Telegram chat via Bot API.
    Supports dry-run testing, inline keyboards, and environment variable fallback.
    """
    load_env_file()
    token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
    chat = chat_id or os.getenv("TELEGRAM_CHAT_ID")

    if dry_run or not token or not chat:
        reason = "dry_run mode active" if dry_run else "missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID"
        logger.info(f"[Telegram Dispatch (Simulated)]: {reason}")
        return {
            "channel": "telegram",
            "delivered": True,
            "simulated": True,
            "reason": reason,
            "has_keyboard": bool(reply_markup),
            "message_length": len(message),
            "preview": message[:200] + "..." if len(message) > 200 else message
        }

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup

    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "channel": "telegram",
                    "delivered": True,
                    "simulated": False,
                    "message_id": data.get("result", {}).get("message_id")
                }
            else:
                return {
                    "channel": "telegram",
                    "delivered": False,
                    "simulated": False,
                    "status_code": resp.status_code,
                    "error": resp.text
                }
    except Exception as e:
        logger.error(f"Telegram dispatch failed: {str(e)}")
        return {
            "channel": "telegram",
            "delivered": False,
            "simulated": False,
            "error": str(e)
        }
