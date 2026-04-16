# tests/test_database.py
from datetime import date, datetime
from db.database import Trader, Company, Trade, NewsEvent, Relationship, Alert


def test_trader_stores_aliases(session):
    t = Trader(canonical_name="Jane Doe", aliases=["J. Doe"], country="US")
    session.add(t)
    session.commit()
    loaded = session.get(Trader, t.id)
    assert loaded.canonical_name == "Jane Doe"
    assert "J. Doe" in loaded.aliases


def test_trade_stores_all_fields(session, sample_trader, sample_company):
    trade = Trade(
        trader_id=sample_trader.id,
        company_id=sample_company.id,
        trade_date=date(2024, 3, 1),
        trade_type="sell",
        shares=500,
        price=190.0,
        value_usd=95000.0,
        source="sec",
        raw_filing_url="https://example.com/filing.xml",
    )
    session.add(trade)
    session.commit()
    loaded = session.get(Trade, trade.id)
    assert loaded.trade_type == "sell"
    assert loaded.value_usd == 95000.0


def test_alert_stores_scores(session, sample_trader, sample_company, sample_trade, sample_news_event):
    alert = Alert(
        trader_id=sample_trader.id,
        company_id=sample_company.id,
        trade_id=sample_trade.id,
        news_event_id=sample_news_event.id,
        days_before_news=5,
        price_change_pct=12.5,
        timing_score=40.0,
        network_score=20.0,
        total_score=60.0,
        created_at=datetime(2024, 1, 16),
    )
    session.add(alert)
    session.commit()
    loaded = session.get(Alert, alert.id)
    assert loaded.total_score == 60.0
    assert loaded.days_before_news == 5


def test_relationship_stores_type(session, sample_trader):
    t2 = Trader(canonical_name="Bob Jones", country="US")
    session.add(t2)
    session.commit()
    r = Relationship(
        trader_a_id=sample_trader.id,
        trader_b_id=t2.id,
        relation_type="board",
        source="sec_filing",
    )
    session.add(r)
    session.commit()
    loaded = session.get(Relationship, r.id)
    assert loaded.relation_type == "board"
