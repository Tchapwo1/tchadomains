"""
TchaDomains Interactive Telegram Bot Daemon
Listens for user commands (/top, /watchlist, /radar) and inline button callbacks
(⭐ Save to Watchlist, 🔄 Refresh) with instant DuckDB persistence.
"""

import os
import sys
import time
import logging
from typing import Dict, Any, Optional
import httpx

# Reconfigure stdout for UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from src.db.storage import DomainStore
from src.dispatch.telegram_notifier import (
    load_env_file,
    format_telegram_message,
    build_inline_keyboard,
    send_telegram_alert
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("tchadomains.bot_daemon")

class TelegramBotDaemon:
    def __init__(self, token: Optional[str] = None):
        load_env_file()
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.offset = 0
        self.running = False

        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN is required to run the bot daemon.")

        self.api_url = f"https://api.telegram.org/bot{self.token}"

    def get_store(self, read_only: bool = True) -> DomainStore:
        """Returns a store instance."""
        return DomainStore(read_only=read_only)

    def send_message(self, chat_id: int, text: str, reply_markup: Optional[Dict] = None) -> None:
        """Sends a message to a specific chat."""
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup

        try:
            with httpx.Client(timeout=10.0) as client:
                client.post(f"{self.api_url}/sendMessage", json=payload)
        except Exception as e:
            logger.error(f"Failed to send message: {e}")

    def answer_callback(self, callback_id: str, text: str, show_alert: bool = False) -> None:
        """Acknowledges a button click with a toast notification."""
        try:
            with httpx.Client(timeout=10.0) as client:
                client.post(
                    f"{self.api_url}/answerCallbackQuery",
                    json={"callback_query_id": callback_id, "text": text, "show_alert": show_alert}
                )
        except Exception as e:
            logger.error(f"Failed to answer callback: {e}")

    def handle_command_top(self, chat_id: int) -> None:
        """Handles /top or refresh button."""
        store = self.get_store(read_only=True)
        top_ai = store.query_top_alpha(limit=5, category="AI", min_score=60.0)
        top_fintech = store.query_top_alpha(limit=5, category="Fintech", min_score=60.0)

        msg = format_telegram_message(top_ai, top_fintech)
        kb = build_inline_keyboard(top_ai, top_fintech)
        self.send_message(chat_id, msg, reply_markup=kb)

    def handle_command_watchlist(self, chat_id: int) -> None:
        """Handles /watchlist."""
        store = self.get_store(read_only=True)
        items = store.get_watchlist()
        if not items:
            self.send_message(
                chat_id,
                "📋 *Your Watchlist is Empty*\n\nTap `⭐ Save` under any dropping domain to bookmark it here!"
            )
            return

        lines = [
            f"📋 *Your Tactical Watchlist ({len(items)} saved)*",
            "━━━━━━━━━━━━━━━━━━━━━━"
        ]
        for i, item in enumerate(items, 1):
            domain = item["domain_name"]
            max_bid = item.get("max_bid_usd", 50.0)
            target = item.get("target_registrar", "Namecheap")
            url = f"https://www.namecheap.com/domains/registration/results/?domain={domain}"
            lines.append(f"*{i}.* `{domain}` — Max: `${max_bid:.0f}` via `{target}`")
            lines.append(f"   ↳ [Open in Namecheap]({url})")
            lines.append("")

        lines.append("━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("⚡ Managed locally inside DuckDB.")
        self.send_message(chat_id, "\n".join(lines))

    def handle_command_start(self, chat_id: int) -> None:
        """Handles /start or /help."""
        msg = (
            "⚡ *Welcome to TchaDomains Tactical Bot*\n"
            "Autonomous domain intelligence front-running dropping AI & Fintech assets.\n\n"
            "*Available Commands:*\n"
            "• `/top` — Instant Top 10 AI & Fintech Drops\n"
            "• `/watchlist` — View all your saved target domains\n"
            "• `/help` — Display this command menu\n\n"
            "💡 _Tip: Tap '⭐ Save' under any drop in the dispatch to instantly add it to your DuckDB watchlist._"
        )
        self.send_message(chat_id, msg)

    def handle_callback_query(self, cb: Dict) -> None:
        """Processes inline button clicks."""
        cb_id = cb["id"]
        data = cb.get("data", "")
        chat_id = cb["message"]["chat"]["id"]

        if data.startswith("watch:"):
            domain = data.split("watch:", 1)[1]
            store = self.get_store(read_only=False)
            store.add_to_watchlist(
                domain_name=domain,
                notes="Bookmarked via Telegram Bot",
                max_bid=50.0
            )
            self.answer_callback(cb_id, f"⭐ {domain} saved to Watchlist!", show_alert=False)
            self.send_message(chat_id, f"✅ *Bookmarked:* `{domain}` is now saved to your radar watchlist.")

        elif data == "cmd:watchlist":
            self.answer_callback(cb_id, "Loading watchlist...")
            self.handle_command_watchlist(chat_id)

        elif data == "cmd:refresh":
            self.answer_callback(cb_id, "Refreshing radar...")
            self.handle_command_top(chat_id)

    def process_update(self, update: Dict) -> None:
        """Routes messages and callback queries."""
        # Handle Callback Queries (Button Clicks)
        if "callback_query" in update:
            self.handle_callback_query(update["callback_query"])
            return

        # Handle Standard Chat Messages
        if "message" in update and "text" in update["message"]:
            msg = update["message"]
            text = msg["text"].strip()
            chat_id = msg["chat"]["id"]

            if text.startswith("/start") or text.startswith("/help"):
                self.handle_command_start(chat_id)
            elif text.startswith("/top") or text.lower() == "top":
                self.handle_command_top(chat_id)
            elif text.startswith("/watchlist") or text.lower() == "watchlist":
                self.handle_command_watchlist(chat_id)
            else:
                self.send_message(
                    chat_id,
                    f"Unknown command `{text}`. Send `/top` for drops or `/watchlist` for saved targets."
                )

    def poll_once(self) -> int:
        """Fetches and processes pending updates once (useful for tests and single cycles)."""
        try:
            with httpx.Client(timeout=15.0) as client:
                res = client.get(
                    f"{self.api_url}/getUpdates",
                    params={"offset": self.offset, "timeout": 2}
                )
                if res.status_code != 200:
                    return 0

                updates = res.json().get("result", [])
                for u in updates:
                    self.offset = u["update_id"] + 1
                    self.process_update(u)

                return len(updates)
        except Exception as e:
            logger.error(f"Error polling updates: {e}")
            return 0

    def run_forever(self) -> None:
        """Continuous polling loop."""
        self.running = True
        logger.info("⚡ TchaDomains Telegram Bot Daemon active. Listening for user interactions...")
        while self.running:
            self.poll_once()
            time.sleep(1.0)

if __name__ == "__main__":
    daemon = TelegramBotDaemon()
    daemon.run_forever()
