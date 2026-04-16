# tests/conftest.py
import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from db.database import Base, Trader, Company, Trade, NewsEvent, Relationship, Alert


@pytest.fixture
def engine():
    eng = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(eng)
    return eng


@pytest.fixture
def session(engine):
    with Session(engine) as s:
        yield s


@pytest.fixture
def sample_trader(session):
    t = Trader(canonical_name="John Smith", aliases=["J. Smith", "John A. Smith"], country="US")
    session.add(t)
    session.commit()
    return t


@pytest.fixture
def sample_company(session):
    c = Company(ticker="AAPL", name="Apple Inc.", exchange="NASDAQ", sector="Technology")
    session.add(c)
    session.commit()
    return c


@pytest.fixture
def sample_trade(session, sample_trader, sample_company):
    t = Trade(
        trader_id=sample_trader.id,
        company_id=sample_company.id,
        trade_date=date(2024, 1, 10),
        trade_type="buy",
        shares=1000,
        price=185.0,
        value_usd=185000.0,
        source="sec",
        raw_filing_url="https://www.sec.gov/Archives/edgar/data/123/000123.xml",
    )
    session.add(t)
    session.commit()
    return t


@pytest.fixture
def sample_news_event(session, sample_company):
    e = NewsEvent(
        company_id=sample_company.id,
        event_date=date(2024, 1, 15),
        headline="Apple reports record Q1 earnings",
        event_type="earnings",
        source_url="https://sec.gov/cgi-bin/browse-edgar?action=getcompany",
    )
    session.add(e)
    session.commit()
    return e
