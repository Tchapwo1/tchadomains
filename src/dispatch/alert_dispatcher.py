"""
TchaDomains Alert Dispatch Coordinator
Extracts top 5 AI and top 5 Fintech drops from DuckDB, formats alerts,
and dispatches across Telegram Bot and Responsive HTML Email channels.
"""

import os
import sys
import argparse
import time
from datetime import date
from pathlib import Path
from typing import Dict, Any, Optional, List

# Reconfigure stdout for UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from src.db.storage import DomainStore
from src.core.ingest import IngestPipeline
from src.dispatch.telegram_notifier import (
    format_telegram_message,
    build_inline_keyboard,
    send_telegram_alert
)
from src.dispatch.email_dispatcher import generate_html_newsletter, send_email_dispatch

def ensure_candidate_inventory(store: DomainStore, min_required: int = 5) -> None:
    """
    Checks if DuckDB contains enough AI and Fintech candidates.
    If database is fresh or empty, ingests a high-alpha benchmark feed.
    """
    ai_candidates = store.query_top_alpha(limit=min_required, category="AI", min_score=60.0)
    fintech_candidates = store.query_top_alpha(limit=min_required, category="Fintech", min_score=60.0)

    if len(ai_candidates) < min_required or len(fintech_candidates) < min_required:
        print("[AlertDispatcher] Insufficient AI/Fintech candidates in storage. Ingesting benchmark stream...")
        pipeline = IngestPipeline(store=store)
        benchmark_stream = pipeline.generate_benchmark_feed(count=3000)
        pipeline.process_domain_list(benchmark_stream, drop_date=date.today())

def run_daily_dispatch(
    channel: str = "both",
    dry_run: bool = False,
    export_html: Optional[str] = None,
    drop_date: Optional[str] = None,
    store: Optional[DomainStore] = None
) -> Dict[str, Any]:
    """
    Executes the Daily Alpha Drops dispatch routine:
    1. Extracts top 5 AI drops.
    2. Extracts top 5 Fintech drops.
    3. Builds Telegram and Email payloads.
    4. Delivers across requested channels.
    """
    start_time = time.time()
    active_store = store or DomainStore()

    # Ensure we have quality data to dispatch
    ensure_candidate_inventory(active_store, min_required=5)

    # 1. Fetch Top 5 AI Drops
    top_ai = active_store.query_top_alpha(
        limit=5,
        min_score=60.0,
        max_length=12,
        category="AI"
    )

    # 2. Fetch Top 5 Fintech Drops
    top_fintech = active_store.query_top_alpha(
        limit=5,
        min_score=60.0,
        max_length=12,
        category="Fintech"
    )

    date_str = drop_date or str(date.today())
    results: Dict[str, Any] = {
        "status": "success",
        "drop_date": date_str,
        "ai_count": len(top_ai),
        "fintech_count": len(top_fintech),
        "total_dispatched": len(top_ai) + len(top_fintech),
        "channels": {}
    }

    # 3. Generate Payloads
    telegram_msg = format_telegram_message(top_ai, top_fintech, drop_date=date_str)
    html_content = generate_html_newsletter(top_ai, top_fintech, drop_date=date_str)

    # Export preview HTML if requested
    if export_html:
        export_path = Path(export_html)
        export_path.parent.mkdir(parents=True, exist_ok=True)
        export_path.write_text(html_content, encoding="utf-8")
        results["exported_html_path"] = str(export_path.resolve())
        print(f"[AlertDispatcher] HTML newsletter exported to {export_path}")

    # 4. Dispatch Telegram
    if channel in ("both", "telegram"):
        keyboard = build_inline_keyboard(top_ai, top_fintech)
        tg_res = send_telegram_alert(
            message=telegram_msg,
            reply_markup=keyboard,
            dry_run=dry_run
        )
        results["channels"]["telegram"] = tg_res
        sim_badge = " [SIMULATED]" if tg_res.get("simulated") else ""
        print(f"[AlertDispatcher] Telegram dispatch: {'SUCCESS' if tg_res.get('delivered') else 'FAILED'}{sim_badge}")

    # 5. Dispatch Email
    if channel in ("both", "email"):
        subject = f"The Daily Tcha • Top {len(top_ai) + len(top_fintech)} AI & Fintech Drops ({date_str})"
        email_res = send_email_dispatch(
            subject=subject,
            html_content=html_content,
            dry_run=dry_run
        )
        results["channels"]["email"] = email_res
        sim_badge = " [SIMULATED]" if email_res.get("simulated") else ""
        print(f"[AlertDispatcher] Email dispatch: {'SUCCESS' if email_res.get('delivered') else 'FAILED'}{sim_badge}")

    results["duration_ms"] = round((time.time() - start_time) * 1000)
    return results

def main():
    parser = argparse.ArgumentParser(
        description="TchaDomains Automated Daily Alpha Drops Dispatcher (Telegram & Email)"
    )
    parser.add_argument(
        "--channel",
        choices=["both", "telegram", "email"],
        default="both",
        help="Notification delivery channels (default: both)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without hitting real external API/SMTP networks"
    )
    parser.add_argument(
        "--export-html",
        type=str,
        default=None,
        help="Path to export the rendered HTML newsletter file"
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="Target drop date (YYYY-MM-DD)"
    )

    args = parser.parse_args()

    print(f"\n=======================================================")
    print(f"⚡ TchaDomains Daily Alpha Dispatcher")
    print(f"=======================================================")
    print(f"Channel:  {args.channel}")
    print(f"Dry-run:  {args.dry_run}")
    print(f"Export:   {args.export_html or 'None'}")
    print(f"-------------------------------------------------------")

    outcome = run_daily_dispatch(
        channel=args.channel,
        dry_run=args.dry_run,
        export_html=args.export_html,
        drop_date=args.date
    )

    print(f"-------------------------------------------------------")
    print(f"Dispatched Top {outcome['total_dispatched']} domains in {outcome['duration_ms']}ms.")
    print(f"=======================================================\n")

if __name__ == "__main__":
    main()
