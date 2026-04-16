# cli_entry.py
import click
from sqlalchemy.orm import Session
from db.database import init_db, get_engine, get_session_factory, DATABASE_URL


@click.group()
def cli():
    """Bloodhound — insider trading pattern detector."""
    pass


@cli.command()
@click.option("--source", default="all", help="Collector to run: sec, news, prices, all")
@click.option("--db", default=DATABASE_URL, help="Database URL")
def collect(source, db):
    """Fetch fresh data from external sources."""
    engine = init_db(db)

    from collectors.sec import SecCollector
    from collectors.news import NewsCollector
    from normalizer.normalizer import Normalizer

    with Session(engine) as session:
        norm = Normalizer(session)

        if source in ("sec", "all"):
            click.echo("Collecting SEC Form 4 filings...")
            records = SecCollector().collect(count=40)
            for r in records:
                try:
                    norm.ingest_trade(r)
                except Exception as e:
                    click.echo(f"  skip: {e}")
            click.echo(f"  Ingested {len(records)} SEC records.")

        if source in ("news", "all"):
            click.echo("Collecting news events...")
            events = NewsCollector().collect()
            for e in events:
                try:
                    norm.ingest_news_event(e)
                except Exception:
                    pass
            click.echo(f"  Ingested {len(events)} news events.")


@cli.command()
@click.option("--min-score", default=0.0, type=float, help="Minimum alert score to show")
@click.option("--db", default=DATABASE_URL, help="Database URL")
def report(min_score, db):
    """Print scored alerts."""
    engine = init_db(db)
    with Session(engine) as session:
        from reporter.cli import print_alerts
        print_alerts(session, min_score=min_score)


@cli.command()
@click.option("--db", default=DATABASE_URL, help="Database URL")
def analyze(db):
    """Score all trade-news pairs and generate alerts."""
    engine = init_db(db)
    with Session(engine) as session:
        from analyzer.scorer import Scorer
        scorer = Scorer(session)
        alerts = scorer.run(lookback_days=30)
        click.echo(f"Generated {len(alerts)} alert(s).")


@cli.command()
@click.option("--db", default=DATABASE_URL, help="Database URL")
def run(db):
    """Run full pipeline: collect → analyze → report."""
    ctx = click.get_current_context()
    ctx.invoke(collect, source="all", db=db)
    ctx.invoke(analyze, db=db)
    ctx.invoke(report, min_score=0.0, db=db)


if __name__ == "__main__":
    cli()
