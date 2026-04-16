# analyzer/timing.py
from __future__ import annotations
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.database import Trade, NewsEvent


class TimingAnalyzer:
    """Scores trades based on proximity to news events."""

    def base_score(self, days_before: int) -> float:
        if days_before <= 0:
            return 0
        if days_before <= 3:
            return 50
        if days_before <= 7:
            return 40
        if days_before <= 14:
            return 25
        if days_before <= 30:
            return 10
        return 0

    def compute_score(
        self,
        days_before: int,
        price_change_pct: Optional[float],
        trade_type: Optional[str],
    ) -> float:
        score = self.base_score(days_before)
        if score == 0:
            return 0.0
        has_large_move = price_change_pct and abs(price_change_pct) > 10
        if has_large_move:
            score *= 1.5
        if trade_type == "buy" and price_change_pct and price_change_pct > 0:
            score *= 1.3
        if has_large_move:
            score = min(50.0, score)
        return round(score, 2)

    def find_trade_news_pairs(
        self,
        session: Session,
        lookback_days: int = 30,
    ) -> list[tuple[int, Trade, NewsEvent]]:
        trades = session.execute(select(Trade)).scalars().all()
        news = session.execute(select(NewsEvent)).scalars().all()
        pairs = []
        for trade in trades:
            if not trade.trade_date:
                continue
            for event in news:
                if event.company_id != trade.company_id:
                    continue
                if not event.event_date:
                    continue
                days_before = (event.event_date - trade.trade_date).days
                if 1 <= days_before <= lookback_days:
                    pairs.append((days_before, trade, event))
        return pairs
