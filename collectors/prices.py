# collectors/prices.py
from __future__ import annotations
from datetime import date, timedelta
from typing import Optional
import yfinance as yf

from collectors.base import BaseCollector


class PriceCollector(BaseCollector):
    """Fetches historical stock prices via yfinance."""

    def price_change_on_date(self, ticker: str, event_date: date) -> Optional[float]:
        """Return percentage price change on event_date for ticker. None if unavailable."""
        start = event_date - timedelta(days=1)
        end = event_date + timedelta(days=2)
        try:
            hist = yf.Ticker(ticker).history(start=str(start), end=str(end))
            if hist.empty or len(hist) < 2:
                return None
            prev_close = hist["Close"].iloc[0]
            close = hist["Close"].iloc[1]
            if prev_close == 0:
                return None
            return round((close - prev_close) / prev_close * 100, 2)
        except Exception:
            return None

    def collect(self, tickers: list[str], start: date, end: date) -> list[dict]:
        results = []
        for ticker in tickers:
            try:
                hist = yf.Ticker(ticker).history(start=str(start), end=str(end))
                for idx, row in hist.iterrows():
                    results.append({
                        "ticker": ticker,
                        "price_date": idx.date(),
                        "close": row["Close"],
                        "volume": row["Volume"],
                    })
            except Exception:
                continue
        return results
