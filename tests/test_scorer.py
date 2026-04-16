# tests/test_scorer.py
import pytest
from datetime import date, datetime
from analyzer.scorer import Scorer
from db.database import Alert


def test_scorer_creates_alert(session, sample_trader, sample_company, sample_trade, sample_news_event):
    scorer = Scorer(session)
    alert = scorer.score_pair(
        trade=sample_trade,
        news_event=sample_news_event,
        days_before=5,
        price_change_pct=12.0,
    )
    assert alert.total_score > 0
    assert alert.total_score <= 100
    assert alert.timing_score + alert.network_score == pytest.approx(alert.total_score, abs=0.01)


def test_scorer_persists_alert(session, sample_trader, sample_company, sample_trade, sample_news_event):
    scorer = Scorer(session)
    alert = scorer.score_pair(
        trade=sample_trade,
        news_event=sample_news_event,
        days_before=5,
        price_change_pct=8.0,
    )
    session.commit()
    loaded = session.get(Alert, alert.id)
    assert loaded is not None


def test_scorer_high_score_for_board_member_3_day_trade(
    session, sample_trader, sample_company, sample_trade, sample_news_event
):
    from db.database import Relationship
    rel = Relationship(
        trader_a_id=sample_trader.id,
        trader_b_id=sample_company.id,
        relation_type="board",
        source="test",
    )
    session.add(rel)
    session.commit()
    scorer = Scorer(session)
    alert = scorer.score_pair(
        trade=sample_trade,
        news_event=sample_news_event,
        days_before=3,
        price_change_pct=15.0,
    )
    assert alert.total_score >= 70
