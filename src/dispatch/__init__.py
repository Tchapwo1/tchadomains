"""
TchaDomains Alert Dispatch System
Dual-channel automated notification pipeline for Telegram and Responsive Email.
"""

from src.dispatch.telegram_notifier import format_telegram_message, send_telegram_alert
from src.dispatch.email_dispatcher import generate_html_newsletter, send_email_dispatch

__all__ = [
    "format_telegram_message",
    "send_telegram_alert",
    "generate_html_newsletter",
    "send_email_dispatch"
]
