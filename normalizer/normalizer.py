# normalizer/normalizer.py
from __future__ import annotations
from typing import Any
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.database import Trader, Company, Trade, NewsEvent
from normalizer.entity_resolver import EntityResolver


class Normalizer:
    """Converts raw collector dicts → ORM objects, deduplicating traders and companies."""

    def __init__(self, session: Session):
        self._session = session
        self._trader_resolver = EntityResolver(self._all_trader_names())
        self._company_resolver = EntityResolver(self._all_company_tickers())

    def _all_trader_names(self) -> list[str]:
        return [t.canonical_name for t in self._session.execute(select(Trader)).scalars().all()]

    def _all_company_tickers(self) -> list[str]:
        return [c.ticker for c in self._session.execute(select(Company)).scalars().all() if c.ticker]

    def _get_or_create_trader(self, name: str) -> Trader:
        match = self._trader_resolver.resolve(name)
        if match:
            return self._session.execute(
                select(Trader).where(Trader.canonical_name == match)
            ).scalar_one()
        trader = Trader(canonical_name=name, aliases=[], roles=[], country="US")
        self._session.add(trader)
        self._session.flush()
        self._trader_resolver.add(name)
        return trader

    def _get_or_create_company(self, name: str, ticker: str) -> Company:
        if ticker:
            match = self._company_resolver.resolve(ticker, threshold=95)
            if match:
                return self._session.execute(
                    select(Company).where(Company.ticker == match)
                ).scalar_one()
        company = Company(ticker=ticker, name=name)
        self._session.add(company)
        self._session.flush()
        if ticker:
            self._company_resolver.add(ticker)
        return company

    def ingest_trade(self, record: dict[str, Any]) -> Trade:
        trader = self._get_or_create_trader(record["owner_name"])
        company = self._get_or_create_company(record["issuer_name"], record.get("ticker", ""))
        trade = Trade(
            trader_id=trader.id,
            company_id=company.id,
            trade_date=record.get("trade_date"),
            trade_type=record.get("trade_type"),
            shares=record.get("shares"),
            price=record.get("price"),
            value_usd=record.get("value_usd"),
            source=record.get("source"),
            raw_filing_url=record.get("raw_filing_url"),
        )
        self._session.add(trade)
        self._session.commit()
        return trade

    def ingest_news_event(self, record: dict[str, Any]) -> NewsEvent:
        ticker = record.get("ticker")
        company = None
        if ticker:
            company = self._session.execute(
                select(Company).where(Company.ticker == ticker)
            ).scalar_one_or_none()
        if company is None:
            company = self._get_or_create_company(ticker or "Unknown", ticker or "")
        event = NewsEvent(
            company_id=company.id,
            event_date=record.get("event_date"),
            headline=record.get("headline"),
            event_type=record.get("event_type"),
            source_url=record.get("source_url"),
        )
        self._session.add(event)
        self._session.commit()
        return event
