"""
TchaDomains Email Alert Dispatcher
Generates and delivers dark-mode, responsive HTML domain drop dispatches (The Daily Tcha).
"""

import os
import smtplib
import logging
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import List, Dict, Optional, Any

logger = logging.getLogger("tchadomains.email")

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

def _render_domain_rows(domains: List[Dict[str, Any]]) -> str:
    """Renders HTML table rows for domain items."""
    if not domains:
        return """
        <tr>
            <td colspan="5" style="padding: 16px; text-align: center; color: #64748b; font-size: 13px;">
                No high-conviction drops meeting alpha threshold in this cluster today.
            </td>
        </tr>
        """

    rows = []
    for i, d in enumerate(domains, 1):
        name = d.get("domain_name", "")
        score = d.get("alpha_score", 0.0)
        chars = d.get("char_length", len(name.split(".")[0]))
        words = d.get("detected_words", "")
        if isinstance(words, list):
            words = " + ".join(words)
        elif not words:
            words = "—"
        else:
            words = words.replace(",", " + ")

        lookup_url = f"https://www.namecheap.com/domains/registration/results/?domain={name}"

        # High score styling
        score_color = "#a3e635" if score >= 85.0 else "#38bdf8"
        score_bg = "rgba(163, 230, 53, 0.12)" if score >= 85.0 else "rgba(56, 189, 248, 0.12)"
        score_border = "rgba(163, 230, 53, 0.3)" if score >= 85.0 else "rgba(56, 189, 248, 0.3)"

        row_html = f"""
        <tr style="border-bottom: 1px solid #1e2633;">
            <td style="padding: 12px 14px; font-weight: 600; font-family: 'JetBrains Mono', monospace; font-size: 14px; color: #ffffff;">
                {name}
            </td>
            <td style="padding: 12px 14px; font-size: 13px; color: #94a3b8; text-align: center;">
                {chars}c
            </td>
            <td style="padding: 12px 14px; font-size: 12px; color: #cbd5e1; font-style: italic;">
                {words}
            </td>
            <td style="padding: 12px 14px; text-align: center;">
                <span style="display: inline-block; padding: 3px 8px; border-radius: 9999px; font-size: 12px; font-weight: 700; font-family: monospace; color: {score_color}; background-color: {score_bg}; border: 1px solid {score_border};">
                    {score:.1f}
                </span>
            </td>
            <td style="padding: 12px 14px; text-align: right;">
                <a href="{lookup_url}" target="_blank" style="display: inline-block; padding: 6px 12px; background: #a3e635; color: #080a0d; font-size: 11px; font-weight: 700; text-decoration: none; border-radius: 6px; text-transform: uppercase; letter-spacing: 0.5px;">
                    Bid &rarr;
                </a>
            </td>
        </tr>
        """
        rows.append(row_html)

    return "\n".join(rows)

def generate_html_newsletter(
    ai_domains: List[Dict[str, Any]],
    fintech_domains: List[Dict[str, Any]],
    drop_date: Optional[str] = None
) -> str:
    """
    Renders an email newsletter matching the Obsidian dark-mode palette.
    """
    drop_date_str = drop_date or str(date.today())
    total_count = len(ai_domains) + len(fintech_domains)

    ai_rows = _render_domain_rows(ai_domains)
    fintech_rows = _render_domain_rows(fintech_domains)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TchaDomains • Daily Alpha Drops Dispatch</title>
</head>
<body style="margin: 0; padding: 24px 0; background-color: #080a0d; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #f1f5f9; -webkit-font-smoothing: antialiased;">
    <div style="max-width: 680px; margin: 0 auto; background: #11151b; border: 1px solid #1e2633; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
        
        <!-- Header -->
        <div style="padding: 28px 32px 20px 32px; border-bottom: 1px solid #1e2633; background: linear-gradient(180deg, #161c24 0%, #11151b 100%);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; color: #a3e635; letter-spacing: 1.5px; text-transform: uppercase;">
                    ⚡ TCHADOMAINS ALPHA RADAR
                </span>
                <span style="font-size: 12px; color: #64748b; font-family: monospace;">
                    {drop_date_str}
                </span>
            </div>
            <h1 style="margin: 12px 0 6px 0; font-size: 22px; font-weight: 800; color: #ffffff; letter-spacing: -0.5px;">
                The Daily Tcha: Top {total_count} AI & Fintech Drops
            </h1>
            <p style="margin: 0; font-size: 13px; color: #94a3b8; line-height: 1.5;">
                Proprietary Alpha Score (0–100) combining length penalties, linguistic harmony, syllable flow, and high-CPC buyer intent.
            </p>
        </div>

        <!-- AI Cluster -->
        <div style="padding: 24px 32px 16px 32px;">
            <div style="margin-bottom: 12px;">
                <h2 style="margin: 0 0 4px 0; font-size: 15px; font-weight: 700; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.5px;">
                    🤖 Top 5 AI & Autonomous Agents
                </h2>
                <p style="margin: 0; font-size: 12px; color: #64748b;">
                    High-value agentic, prompt, neural, and synth naming candidates.
                </p>
            </div>
            
            <table style="width: 100%; border-collapse: collapse; margin-top: 10px; background: #0c0f14; border-radius: 8px; overflow: hidden; border: 1px solid #1e2633;">
                <thead>
                    <tr style="border-bottom: 1px solid #1e2633; background: #141922; text-align: left; font-size: 11px; text-transform: uppercase; color: #64748b; letter-spacing: 0.5px;">
                        <th style="padding: 10px 14px;">Domain</th>
                        <th style="padding: 10px 14px; text-align: center;">Len</th>
                        <th style="padding: 10px 14px;">Structure</th>
                        <th style="padding: 10px 14px; text-align: center;">Alpha</th>
                        <th style="padding: 10px 14px; text-align: right;">Action</th>
                    </tr>
                </thead>
                <tbody>
                    {ai_rows}
                </tbody>
            </table>
        </div>

        <!-- Fintech Cluster -->
        <div style="padding: 16px 32px 24px 32px;">
            <div style="margin-bottom: 12px;">
                <h2 style="margin: 0 0 4px 0; font-size: 15px; font-weight: 700; color: #a3e635; text-transform: uppercase; letter-spacing: 0.5px;">
                    💳 Top 5 Fintech & Financial Rails
                </h2>
                <p style="margin: 0; font-size: 12px; color: #64748b;">
                    Commercial liquidity, pay, vault, and yield protocol naming drops.
                </p>
            </div>
            
            <table style="width: 100%; border-collapse: collapse; margin-top: 10px; background: #0c0f14; border-radius: 8px; overflow: hidden; border: 1px solid #1e2633;">
                <thead>
                    <tr style="border-bottom: 1px solid #1e2633; background: #141922; text-align: left; font-size: 11px; text-transform: uppercase; color: #64748b; letter-spacing: 0.5px;">
                        <th style="padding: 10px 14px;">Domain</th>
                        <th style="padding: 10px 14px; text-align: center;">Len</th>
                        <th style="padding: 10px 14px;">Structure</th>
                        <th style="padding: 10px 14px; text-align: center;">Alpha</th>
                        <th style="padding: 10px 14px; text-align: right;">Action</th>
                    </tr>
                </thead>
                <tbody>
                    {fintech_rows}
                </tbody>
            </table>
        </div>

        <!-- Footer -->
        <div style="padding: 20px 32px; border-top: 1px solid #1e2633; background: #0a0d12; text-align: center; font-size: 12px; color: #64748b;">
            <p style="margin: 0 0 8px 0;">
                💡 <strong>Verisign Drop Cycle:</strong> Daily releases finalize between 18:00 and 20:00 UTC.
            </p>
            <p style="margin: 0; font-family: monospace;">
                TchaDomains • Autonomous Domain Intelligence • <a href="http://localhost:5520" style="color: #a3e635; text-decoration: none;">View Live Radar</a>
            </p>
        </div>

    </div>
</body>
</html>"""

def send_email_dispatch(
    subject: str,
    html_content: str,
    text_content: Optional[str] = None,
    to_email: Optional[str] = None,
    from_email: Optional[str] = None,
    smtp_host: Optional[str] = None,
    smtp_port: Optional[int] = None,
    smtp_user: Optional[str] = None,
    smtp_pass: Optional[str] = None,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Sends the HTML newsletter via SMTP with fallback text part.
    Supports dry-run testing and environment variable configurations.
    """
    load_env_file()
    host = smtp_host or os.getenv("SMTP_HOST")
    port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
    user = smtp_user or os.getenv("SMTP_USER")
    password = smtp_pass or os.getenv("SMTP_PASS")
    recipient = to_email or os.getenv("DISPATCH_EMAIL_TO")
    sender = from_email or os.getenv("DISPATCH_EMAIL_FROM", "alerts@tcha.dev")

    if dry_run or not host or not recipient:
        reason = "dry_run mode active" if dry_run else "missing SMTP_HOST or DISPATCH_EMAIL_TO"
        logger.info(f"[Email Dispatch (Simulated)]: {reason}")
        return {
            "channel": "email",
            "delivered": True,
            "simulated": True,
            "reason": reason,
            "subject": subject,
            "recipient": recipient or "simulated@domain.com",
            "html_bytes": len(html_content.encode("utf-8"))
        }

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient

    # Fallback plain text part
    fallback_text = text_content or f"{subject}\n\nPlease view this email with an HTML-capable email client."
    part1 = MIMEText(fallback_text, "plain")
    part2 = MIMEText(html_content, "html")
    msg.attach(part1)
    msg.attach(part2)

    try:
        if port == 465:
            server = smtplib.SMTP_SSL(host, port, timeout=15.0)
        else:
            server = smtplib.SMTP(host, port, timeout=15.0)
            server.starttls()

        if user and password:
            server.login(user, password)

        server.sendmail(sender, [recipient], msg.as_string())
        server.quit()

        return {
            "channel": "email",
            "delivered": True,
            "simulated": False,
            "recipient": recipient,
            "subject": subject
        }
    except Exception as e:
        logger.error(f"Email dispatch failed: {str(e)}")
        return {
            "channel": "email",
            "delivered": False,
            "simulated": False,
            "error": str(e)
        }
