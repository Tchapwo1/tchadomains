"""
Unit Tests for TchaDomains Dispatcher (Telegram & Responsive Email)
"""

import pytest
import os
from pathlib import Path
from datetime import date
import duckdb

from src.db.storage import DomainStore
from src.dispatch.telegram_notifier import format_telegram_message, send_telegram_alert
from src.dispatch.email_dispatcher import generate_html_newsletter, send_email_dispatch
from src.dispatch.alert_dispatcher import run_daily_dispatch

@pytest.fixture
def sample_ai_domains():
    return [
        {
            "domain_name": "agentflow.com",
            "sld": "agentflow",
            "tld": "com",
            "char_length": 9,
            "syllable_count": 3,
            "detected_words": ["agent", "flow"],
            "primary_category": "AI",
            "commercial_multiplier": 1.4,
            "alpha_score": 93.5,
            "status": "DROPPING",
            "drop_date": date.today()
        },
        {
            "domain_name": "braincore.com",
            "sld": "braincore",
            "tld": "com",
            "char_length": 9,
            "syllable_count": 2,
            "detected_words": ["brain", "core"],
            "primary_category": "AI",
            "commercial_multiplier": 1.4,
            "alpha_score": 91.2,
            "status": "DROPPING",
            "drop_date": date.today()
        }
    ]

@pytest.fixture
def sample_fintech_domains():
    return [
        {
            "domain_name": "payvault.com",
            "sld": "payvault",
            "tld": "com",
            "char_length": 8,
            "syllable_count": 2,
            "detected_words": ["pay", "vault"],
            "primary_category": "Fintech",
            "commercial_multiplier": 1.35,
            "alpha_score": 94.0,
            "status": "DROPPING",
            "drop_date": date.today()
        },
        {
            "domain_name": "tokenyield.com",
            "sld": "tokenyield",
            "tld": "com",
            "char_length": 10,
            "syllable_count": 3,
            "detected_words": ["token", "yield"],
            "primary_category": "Fintech",
            "commercial_multiplier": 1.35,
            "alpha_score": 88.5,
            "status": "DROPPING",
            "drop_date": date.today()
        }
    ]

@pytest.fixture
def temp_store(tmp_path):
    db_file = tmp_path / "test_dispatch.duckdb"
    store = DomainStore(db_path=db_file)
    yield store
    store.close()

def test_telegram_message_formatting(sample_ai_domains, sample_fintech_domains):
    msg = format_telegram_message(sample_ai_domains, sample_fintech_domains, drop_date="2026-10-20")

    # Verify headers and branding
    assert "TchaDomains • Daily Alpha Drops Dispatch" in msg
    assert "2026-10-20" in msg
    assert "TOP AI & AGENT INFRASTRUCTURE DROPS" in msg
    assert "TOP FINTECH & FINANCIAL RAILS DROPS" in msg

    # Verify domain names and alpha badges
    assert "`agentflow.com`" in msg
    assert "[93.5/100]" in msg
    assert "`payvault.com`" in msg
    assert "[94.0/100]" in msg

    # Verify affiliate quick bid links
    assert "namecheap.com/domains/registration/results/?domain=agentflow.com" in msg
    assert "dynadot.com/domain/search.html?domain=payvault.com" in msg

    # Verify Pillar 5 Due Diligence audit links
    assert "web.archive.org/web/*/agentflow.com" in msg
    assert "google.com/search?q=site:payvault.com" in msg

def test_telegram_send_dry_run():
    res = send_telegram_alert("Test alert message", dry_run=True)
    assert res["channel"] == "telegram"
    assert res["delivered"] is True
    assert res["simulated"] is True
    assert "Test alert message" in res["preview"]

def test_email_html_generation(sample_ai_domains, sample_fintech_domains):
    html = generate_html_newsletter(sample_ai_domains, sample_fintech_domains, drop_date="2026-10-20")

    # Verify obsidian dark-mode palette styling
    assert "#080a0d" in html  # Outer background
    assert "#11151b" in html  # Container background
    assert "#a3e635" in html  # Signal lime accent
    assert "#38bdf8" in html  # Cyan AI accent

    # Verify data content
    assert "agentflow.com" in html
    assert "payvault.com" in html
    assert "93.5" in html
    assert "94.0" in html

    # Verify CTA buttons
    assert "namecheap.com/domains/registration/results/?domain=payvault.com" in html
    assert "Bid &rarr;" in html

def test_email_send_dry_run():
    res = send_email_dispatch(
        subject="The Daily Tcha Test",
        html_content="<h1>Test Newsletter</h1>",
        dry_run=True
    )
    assert res["channel"] == "email"
    assert res["delivered"] is True
    assert res["simulated"] is True
    assert res["subject"] == "The Daily Tcha Test"

def test_alert_dispatcher_orchestration(temp_store, sample_ai_domains, sample_fintech_domains, tmp_path):
    # Insert test batch into clean store
    temp_store.insert_batch(sample_ai_domains + sample_fintech_domains, drop_date=date.today())

    export_file = tmp_path / "test_newsletter.html"
    res = run_daily_dispatch(
        channel="both",
        dry_run=True,
        export_html=str(export_file),
        store=temp_store
    )

    assert res["status"] == "success"
    assert "telegram" in res["channels"]
    assert "email" in res["channels"]
    assert res["channels"]["telegram"]["delivered"] is True
    assert res["channels"]["email"]["delivered"] is True

    # Verify HTML was written to the export destination
    assert export_file.exists()
    assert "The Daily Tcha" in export_file.read_text(encoding="utf-8")
