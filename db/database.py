# db/database.py
from __future__ import annotations
from datetime import date, datetime
from typing import Optional
from sqlalchemy import create_engine, String, Integer, Float, Date, DateTime, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
import os

DATABASE_URL = os.environ.get("BLOODHOUND_DB", "sqlite:///bloodhound.db")


class Base(DeclarativeBase):
    pass


class Trader(Base):
    __tablename__ = "traders"
    id: Mapped[int] = mapped_column(primary_key=True)
    canonical_name: Mapped[str] = mapped_column(String, nullable=False)
    aliases: Mapped[list] = mapped_column(JSON, default=list)
    roles: Mapped[list] = mapped_column(JSON, default=list)
    country: Mapped[Optional[str]] = mapped_column(String)


class Company(Base):
    __tablename__ = "companies"
    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[Optional[str]] = mapped_column(String)
    name: Mapped[str] = mapped_column(String, nullable=False)
    exchange: Mapped[Optional[str]] = mapped_column(String)
    sector: Mapped[Optional[str]] = mapped_column(String)


class Trade(Base):
    __tablename__ = "trades"
    id: Mapped[int] = mapped_column(primary_key=True)
    trader_id: Mapped[int] = mapped_column(Integer)
    company_id: Mapped[int] = mapped_column(Integer)
    trade_date: Mapped[Optional[date]] = mapped_column(Date)
    trade_type: Mapped[Optional[str]] = mapped_column(String)  # buy/sell
    shares: Mapped[Optional[float]] = mapped_column(Float)
    price: Mapped[Optional[float]] = mapped_column(Float)
    value_usd: Mapped[Optional[float]] = mapped_column(Float)
    source: Mapped[Optional[str]] = mapped_column(String)
    raw_filing_url: Mapped[Optional[str]] = mapped_column(String)


class NewsEvent(Base):
    __tablename__ = "news_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(Integer)
    event_date: Mapped[Optional[date]] = mapped_column(Date)
    headline: Mapped[Optional[str]] = mapped_column(String)
    event_type: Mapped[Optional[str]] = mapped_column(String)
    source_url: Mapped[Optional[str]] = mapped_column(String)


class Relationship(Base):
    __tablename__ = "relationships"
    id: Mapped[int] = mapped_column(primary_key=True)
    trader_a_id: Mapped[int] = mapped_column(Integer)
    trader_b_id: Mapped[int] = mapped_column(Integer)
    relation_type: Mapped[Optional[str]] = mapped_column(String)
    source: Mapped[Optional[str]] = mapped_column(String)


class Alert(Base):
    __tablename__ = "alerts"
    id: Mapped[int] = mapped_column(primary_key=True)
    trader_id: Mapped[int] = mapped_column(Integer)
    company_id: Mapped[int] = mapped_column(Integer)
    trade_id: Mapped[int] = mapped_column(Integer)
    news_event_id: Mapped[int] = mapped_column(Integer)
    days_before_news: Mapped[Optional[int]] = mapped_column(Integer)
    price_change_pct: Mapped[Optional[float]] = mapped_column(Float)
    timing_score: Mapped[Optional[float]] = mapped_column(Float)
    network_score: Mapped[Optional[float]] = mapped_column(Float)
    total_score: Mapped[Optional[float]] = mapped_column(Float)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime)


def get_engine(url: str = DATABASE_URL):
    return create_engine(url)


def get_session_factory(engine):
    return sessionmaker(bind=engine)


def init_db(url: str = DATABASE_URL):
    engine = get_engine(url)
    Base.metadata.create_all(engine)
    return engine
