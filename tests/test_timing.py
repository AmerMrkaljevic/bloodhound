# tests/test_timing.py
from datetime import date
from analyzer.timing import TimingAnalyzer


def test_timing_1_to_3_days_scores_50():
    analyzer = TimingAnalyzer()
    score = analyzer.base_score(days_before=2)
    assert score == 50


def test_timing_4_to_7_days_scores_40():
    analyzer = TimingAnalyzer()
    assert analyzer.base_score(days_before=5) == 40


def test_timing_8_to_14_days_scores_25():
    analyzer = TimingAnalyzer()
    assert analyzer.base_score(days_before=10) == 25


def test_timing_15_to_30_days_scores_10():
    analyzer = TimingAnalyzer()
    assert analyzer.base_score(days_before=20) == 10


def test_timing_over_30_days_scores_0():
    analyzer = TimingAnalyzer()
    assert analyzer.base_score(days_before=31) == 0


def test_timing_negative_days_scores_0():
    analyzer = TimingAnalyzer()
    assert analyzer.base_score(days_before=-1) == 0


def test_timing_large_price_move_capped_at_50():
    analyzer = TimingAnalyzer()
    score = analyzer.compute_score(days_before=1, price_change_pct=20.0, trade_type="buy")
    assert score == 50


def test_timing_sell_before_positive_news_no_buy_multiplier():
    analyzer = TimingAnalyzer()
    score_buy = analyzer.compute_score(days_before=3, price_change_pct=5.0, trade_type="buy")
    score_sell = analyzer.compute_score(days_before=3, price_change_pct=5.0, trade_type="sell")
    assert score_buy > score_sell


def test_timing_finds_matching_events(session, sample_trade, sample_news_event):
    analyzer = TimingAnalyzer()
    matches = analyzer.find_trade_news_pairs(session, lookback_days=30)
    assert len(matches) == 1
    days, trade, event = matches[0]
    assert days == 5
    assert trade.id == sample_trade.id
