# tests/test_normalizer.py
from datetime import date
from normalizer.normalizer import Normalizer
from db.database import Trade, Trader, Company, NewsEvent


def test_normalizer_creates_trader_from_sec_record(session):
    norm = Normalizer(session)
    record = {
        "issuer_name": "APPLE INC",
        "ticker": "AAPL",
        "owner_name": "Cook Timothy D",
        "trade_date": date(2024, 1, 10),
        "trade_type": "buy",
        "shares": 1000.0,
        "price": 185.0,
        "value_usd": 185000.0,
        "source": "sec",
        "raw_filing_url": "https://sec.gov/test.xml",
    }
    trade = norm.ingest_trade(record)
    assert trade.id is not None
    assert trade.source == "sec"
    trader = session.get(Trader, trade.trader_id)
    assert trader.canonical_name == "Cook Timothy D"


def test_normalizer_reuses_existing_company(session):
    norm = Normalizer(session)
    record1 = {
        "issuer_name": "APPLE INC", "ticker": "AAPL", "owner_name": "Alice",
        "trade_date": date(2024, 1, 10), "trade_type": "buy",
        "shares": 100.0, "price": 185.0, "value_usd": 18500.0,
        "source": "sec", "raw_filing_url": "https://sec.gov/1.xml",
    }
    record2 = {**record1, "owner_name": "Bob", "raw_filing_url": "https://sec.gov/2.xml"}
    norm.ingest_trade(record1)
    norm.ingest_trade(record2)
    from sqlalchemy import select
    companies = session.execute(select(Company).where(Company.ticker == "AAPL")).scalars().all()
    assert len(companies) == 1


def test_normalizer_ingest_news_event(session, sample_company):
    norm = Normalizer(session)
    event_dict = {
        "headline": "Apple Q1 earnings beat",
        "event_date": date(2024, 1, 15),
        "event_type": "earnings",
        "source_url": "https://sec.gov/news/1",
        "ticker": "AAPL",
    }
    event = norm.ingest_news_event(event_dict)
    assert event.id is not None
    assert event.company_id == sample_company.id
