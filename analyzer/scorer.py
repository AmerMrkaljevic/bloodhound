# analyzer/scorer.py
from __future__ import annotations
from datetime import datetime, UTC
from typing import Optional
from sqlalchemy.orm import Session

from db.database import Trade, NewsEvent, Alert
from analyzer.timing import TimingAnalyzer
from analyzer.network import NetworkAnalyzer


class Scorer:
    """Combines timing and network signals into an Alert row."""

    def __init__(self, session: Session):
        self._session = session
        self._timing = TimingAnalyzer()
        self._network = NetworkAnalyzer()

    def score_pair(
        self,
        trade: Trade,
        news_event: NewsEvent,
        days_before: int,
        price_change_pct: Optional[float],
    ) -> Alert:
        timing_score = self._timing.compute_score(
            days_before=days_before,
            price_change_pct=price_change_pct,
            trade_type=trade.trade_type,
        )
        network_score = self._network.compute_score(
            self._session, trade.trader_id, trade.company_id
        )
        total = round(timing_score + network_score, 2)

        alert = Alert(
            trader_id=trade.trader_id,
            company_id=trade.company_id,
            trade_id=trade.id,
            news_event_id=news_event.id,
            days_before_news=days_before,
            price_change_pct=price_change_pct,
            timing_score=timing_score,
            network_score=network_score,
            total_score=total,
            created_at=datetime.now(UTC),
        )
        self._session.add(alert)
        self._session.flush()
        return alert

    def run(self, lookback_days: int = 30) -> list[Alert]:
        """Find all trade-news pairs and score them. Returns new Alert objects."""
        timing = TimingAnalyzer()
        pairs = timing.find_trade_news_pairs(self._session, lookback_days=lookback_days)
        alerts = []
        for days_before, trade, event in pairs:
            alert = self.score_pair(trade, event, days_before, price_change_pct=None)
            alerts.append(alert)
        self._session.commit()
        return alerts
