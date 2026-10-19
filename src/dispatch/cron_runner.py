"""
TchaDomains Daily Cron Runner Daemon
Runs continuously in the background, triggers the daily drop sync and dispatch
at a specified target hour (default 17:45 UTC / 18:45 CET).
"""

import sys
import time
import argparse
from datetime import datetime, time as dtime

# Reconfigure stdout for UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from src.core.ingest import IngestPipeline
from src.dispatch.alert_dispatcher import run_daily_dispatch

def run_daemon(target_hour: int = 18, target_minute: int = 0, channel: str = "telegram"):
    print(f"⚡ [TchaDaemon] Active. Scheduled to trigger daily at {target_hour:02d}:{target_minute:02d}...")
    last_triggered_date = None

    while True:
        now = datetime.now()
        current_date_str = now.strftime("%Y-%m-%d")

        if (now.hour == target_hour and now.minute >= target_minute) and (last_triggered_date != current_date_str):
            print(f"⚡ [TchaDaemon] Executing scheduled daily dispatch for {current_date_str}...")
            
            # 1. Sync fresh drop feed
            try:
                pipeline = IngestPipeline()
                sync_result = pipeline.sync_daily_drops(force_refresh=True)
                print(f"⚡ [TchaDaemon] Drops synced: {sync_result['candidates_count']} candidates.")
            except Exception as e:
                print(f"⚠️ [TchaDaemon] Drop sync warning: {e}")

            # 2. Run dispatch to Telegram and/or Email
            try:
                dispatch_res = run_daily_dispatch(channel=channel, dry_run=False)
                print(f"⚡ [TchaDaemon] Dispatched {dispatch_res['total_dispatched']} drops in {dispatch_res['duration_ms']}ms.")
                last_triggered_date = current_date_str
            except Exception as e:
                print(f"❌ [TchaDaemon] Dispatch failed: {e}")

        time.sleep(30)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TchaDomains Daily Scheduled Daemon")
    parser.add_argument("--hour", type=int, default=18, help="Target hour of the day (0-23, default 18)")
    parser.add_argument("--minute", type=int, default=0, help="Target minute of the hour (0-59, default 0)")
    parser.add_argument("--channel", choices=["both", "telegram", "email"], default="telegram", help="Dispatch channels")

    args = parser.parse_args()
    run_daemon(target_hour=args.hour, target_minute=args.minute, channel=args.channel)
