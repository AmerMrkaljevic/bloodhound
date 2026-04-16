# collectors/news.py
from __future__ import annotations
from datetime import date
from email.utils import parsedate_to_datetime
from typing import Any, Optional
import feedparser
import requests

from collectors.base import BaseCollector

SEC_8K_RSS = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=8-K&dateb=&owner=include&count=40&output=atom"
YAHOO_FINANCE_RSS = "https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"

EARNINGS_KEYWORDS = ["earnings", "revenue", "profit", "q1", "q2", "q3", "q4", "quarterly", "annual results"]
MA_KEYWORDS = ["acqui", "merger", "takeover", "buyout", "deal", "transaction"]
FDA_KEYWORDS = ["fda", "approval", "clinical trial", "drug", "therapy"]
REGULATORY_KEYWORDS = ["sec charges", "doj", "investigation", "settlement", "fine", "penalty"]


class NewsCollector(BaseCollector):
    HEADERS = {"User-Agent": "Bloodhound/1.0 research@bloodhound.local"}

    def classify_event(self, headline: str) -> str:
        h = headline.lower()
        if any(k in h for k in EARNINGS_KEYWORDS):
            return "earnings"
        if any(k in h for k in MA_KEYWORDS):
            return "ma"
        if any(k in h for k in FDA_KEYWORDS):
            return "fda"
        if any(k in h for k in REGULATORY_KEYWORDS):
            return "regulatory"
        return "other"

    def fetch_feed(self, url: str) -> list[dict[str, Any]]:
        resp = requests.get(url, headers=self.HEADERS, timeout=30)
        resp.raise_for_status()
        feed = feedparser.parse(resp.text)
        events = []
        for entry in feed.entries:
            event_date = None
            if hasattr(entry, "published"):
                try:
                    event_date = parsedate_to_datetime(entry.published).date()
                except Exception:
                    pass
            headline = entry.get("title", "")
            events.append({
                "headline": headline,
                "event_date": event_date,
                "event_type": self.classify_event(headline),
                "source_url": entry.get("link", ""),
            })
        return events

    def collect(self, tickers: Optional[list[str]] = None) -> list[dict[str, Any]]:
        results = []
        results.extend(self.fetch_feed(SEC_8K_RSS))
        if tickers:
            for ticker in tickers:
                try:
                    url = YAHOO_FINANCE_RSS.format(ticker=ticker)
                    results.extend(self.fetch_feed(url))
                except Exception:
                    continue
        return results
