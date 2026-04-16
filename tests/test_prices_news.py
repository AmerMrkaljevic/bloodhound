# tests/test_prices_news.py
import pytest
from unittest.mock import patch, MagicMock
from datetime import date
from collectors.prices import PriceCollector
from collectors.news import NewsCollector


def test_price_collector_returns_price_change():
    mock_hist = MagicMock()
    mock_hist.empty = False
    mock_hist.__len__ = lambda self: 2
    mock_hist["Close"].iloc = MagicMock()
    mock_hist["Close"].iloc.__getitem__ = lambda self, i: 185.0 if i == 0 else 205.0

    with patch("collectors.prices.yf.Ticker") as mock_ticker:
        mock_ticker.return_value.history.return_value = mock_hist
        collector = PriceCollector()
        pct = collector.price_change_on_date("AAPL", date(2024, 1, 15))
        assert pct is not None


def test_price_collector_returns_none_on_missing_ticker():
    mock_hist = MagicMock()
    mock_hist.empty = True

    with patch("collectors.prices.yf.Ticker") as mock_ticker:
        mock_ticker.return_value.history.return_value = mock_hist
        collector = PriceCollector()
        pct = collector.price_change_on_date("INVALID_TICKER_XYZ", date(2024, 1, 15))
        assert pct is None


def test_news_collector_parse_rss_returns_events():
    sample_rss = """<?xml version="1.0"?>
    <rss version="2.0">
      <channel>
        <item>
          <title>Apple Q1 2024 Earnings Release</title>
          <link>https://sec.gov/news/1</link>
          <pubDate>Thu, 01 Feb 2024 16:00:00 GMT</pubDate>
          <description>AAPL reports record revenue</description>
        </item>
      </channel>
    </rss>"""

    with patch("collectors.news.requests.get") as mock_get:
        mock_get.return_value.text = sample_rss
        mock_get.return_value.raise_for_status = lambda: None
        collector = NewsCollector()
        events = collector.fetch_feed("https://example.com/rss")
        assert len(events) == 1
        assert "Apple" in events[0]["headline"]
        assert events[0]["event_date"] is not None


def test_news_collector_classifies_earnings():
    collector = NewsCollector()
    event_type = collector.classify_event("Apple Q1 2024 Earnings Release")
    assert event_type == "earnings"


def test_news_collector_classifies_ma():
    collector = NewsCollector()
    event_type = collector.classify_event("Microsoft acquires Activision Blizzard")
    assert event_type == "ma"


def test_news_collector_classifies_other():
    collector = NewsCollector()
    event_type = collector.classify_event("Some unrelated company news")
    assert event_type == "other"
