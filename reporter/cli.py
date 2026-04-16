# reporter/cli.py
from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.database import Alert, Trader, Company, NewsEvent

LEVEL_ICONS = {
    (80, 100): "🔴",
    (50, 79): "🟡",
    (20, 49): "🟢",
    (0, 19): "⚪",
}


def score_icon(score: float) -> str:
    for (low, high), icon in LEVEL_ICONS.items():
        if low <= score <= high:
            return icon
    return "⚪"


def format_alert(alert: Alert, session: Session) -> str:
    trader = session.get(Trader, alert.trader_id)
    company = session.get(Company, alert.company_id)
    event = session.get(NewsEvent, alert.news_event_id)

    trader_name = trader.canonical_name if trader else "Unknown"
    company_name = f"{company.ticker} ({company.name})" if company else "Unknown"
    headline = event.headline[:60] if event and event.headline else "Unknown event"

    return (
        f"{score_icon(alert.total_score)} Score: {alert.total_score:5.1f}  "
        f"{company_name:<25}  {trader_name:<25}  "
        f"{alert.days_before_news}d before  \"{headline}\""
    )


def print_alerts(session: Session, min_score: float = 0.0) -> list[Alert]:
    alerts = session.execute(
        select(Alert).where(Alert.total_score >= min_score).order_by(Alert.total_score.desc())
    ).scalars().all()

    if not alerts:
        print("No alerts found.")
        return []

    print(f"\n{'─' * 90}")
    print(f"  BLOODHOUND — {len(alerts)} alert(s) with score >= {min_score}")
    print(f"{'─' * 90}")
    for alert in alerts:
        print(f"  {format_alert(alert, session)}")
    print(f"{'─' * 90}\n")
    return alerts
