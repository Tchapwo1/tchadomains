"""
TchaDomains Terminal Tactical Radar (CLI)
Renders high-density, colorized alpha drop telemetry directly to the terminal.
"""

import argparse
from datetime import date
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from src.db.storage import DomainStore
from src.core.ingest import IngestPipeline
from src.dispatch.alert_dispatcher import run_daily_dispatch

import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

console = Console()

def format_score(score: float) -> Text:
    """Applies cyber-domainer color gradients based on alpha score."""
    if score >= 85.0:
        return Text(f"* {score:.1f}", style="bold yellow")
    elif score >= 75.0:
        return Text(f"+ {score:.1f}", style="bold green")
    else:
        return Text(f"  {score:.1f}", style="dim white")

def run_cli():
    parser = argparse.ArgumentParser(description="TchaDomains Tactical Radar CLI")
    parser.add_argument("--limit", type=int, default=25, help="Number of domains to display")
    parser.add_argument("--min-score", type=float, default=70.0, help="Minimum Alpha Score threshold")
    parser.add_argument("--max-len", type=int, default=10, help="Maximum SLD character length")
    parser.add_argument("--category", type=str, default="all", help="Filter by category (AI, Fintech, DevTools, all)")
    parser.add_argument("--seed-benchmark", action="store_true", help="Ingest a 50,000 domain test drop stream")
    parser.add_argument("--dispatch", choices=["both", "telegram", "email"], default=None, help="Trigger automated daily top 10 dispatch")
    parser.add_argument("--dry-run", action="store_true", help="Run dispatch without sending live API/SMTP requests")

    args = parser.parse_args()
    store = DomainStore()

    if args.seed_benchmark:
        console.print("[cyan]>> Ingesting 50,000 benchmark drop candidates...[/cyan]")
        pipeline = IngestPipeline(store=store)
        sample_drops = pipeline.generate_benchmark_feed(count=50000)
        metrics = pipeline.process_domain_list(sample_drops)
        
        console.print(Panel(
            f"[bold green][OK] Ingestion Complete in {metrics['total_duration_ms']}ms![/bold green]\n"
            f"- Raw Dropping Domains: [bold]{metrics['raw_count']:,}[/bold]\n"
            f"- Passed Filter: [bold]{metrics['candidates_count']:,}[/bold]\n"
            f"- Alpha Gems (Score >= 80): [bold yellow]{metrics['alpha_gems_count']:,}[/bold yellow]\n"
            f"- Throughput: [bold cyan]{metrics['throughput_domains_per_sec']:,} domains/sec[/bold cyan]",
            title="[bold yellow]TchaDomains Telemetry[/bold yellow]",
            border_style="yellow"
        ))

    if args.dispatch:
        console.print(f"[bold cyan]>> Triggering Automated Top 10 Drops Dispatch ({args.dispatch})...[/bold cyan]")
        res = run_daily_dispatch(
            channel=args.dispatch,
            dry_run=args.dry_run,
            store=store
        )
        sim_note = " (Simulated)" if args.dry_run else ""
        console.print(Panel(
            f"[bold green][OK] Dispatch Processed in {res['duration_ms']}ms!{sim_note}[/bold green]\n"
            f"- AI Drops: [bold]{res['ai_count']}[/bold]\n"
            f"- Fintech Drops: [bold]{res['fintech_count']}[/bold]\n"
            f"- Channels: [bold cyan]{', '.join(res['channels'].keys())}[/bold cyan]",
            title="[bold yellow]Tcha Alert Dispatcher[/bold yellow]",
            border_style="green"
        ))
        return

    results = store.query_top_alpha(
        limit=args.limit,
        min_score=args.min_score,
        max_length=args.max_len,
        category=args.category
    )

    if not results:
        console.print("[yellow]No domains match your filter criteria. Try running with --seed-benchmark or lowering --min-score.[/yellow]")
        return

    table = Table(
        title=f"TchaDomains Tactical Radar - Top {len(results)} Alpha Drops ({date.today()})",
        header_style="bold cyan",
        border_style="dim white",
        show_lines=False
    )

    table.add_column("#", justify="right", style="dim")
    table.add_column("Domain Name", style="bold white")
    table.add_column("Alpha Score", justify="center")
    table.add_column("Len", justify="right", style="dim")
    table.add_column("Niche Category", style="magenta")
    table.add_column("Decomposed Words", style="cyan")
    table.add_column("Quick Action", style="blue")

    for idx, r in enumerate(results, start=1):
        words = r["detected_words"] if r["detected_words"] else "-"
        table.add_row(
            str(idx),
            r["domain_name"],
            format_score(r["alpha_score"]),
            str(r["char_length"]),
            r["primary_category"],
            words,
            f"https://namecheap.pxf.io/c/tcha/{r['domain_name']}"
        )

    console.print(table)
    console.print(f"[dim]Tip: Launch the tactical web UI via: [bold]python -m src.ui.server[/bold][/dim]\n")

if __name__ == "__main__":
    run_cli()
