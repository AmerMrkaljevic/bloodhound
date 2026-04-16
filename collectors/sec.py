# collectors/sec.py
from __future__ import annotations
import xml.etree.ElementTree as ET
from datetime import date
from typing import Any, Optional
import requests
import feedparser

from collectors.base import BaseCollector

EDGAR_RSS_URL = (
    "https://www.sec.gov/cgi-bin/browse-edgar"
    "?action=getcurrent&type=4&dateb=&owner=include&count={count}&output=atom"
)
HEADERS = {"User-Agent": "Bloodhound/1.0 research@bloodhound.local"}


def _text(el: Optional[ET.Element]) -> Optional[str]:
    """Safely get text from an XML element."""
    if el is None:
        return None
    t = el.text
    return t.strip() if t and t.strip() else None


def parse_form4_xml(xml_str: str, filing_url: str) -> dict[str, Any]:
    """Parse Form 4 XML and return a normalized dict."""
    root = ET.fromstring(xml_str)

    issuer_name = _text(root.find(".//issuerName"))
    ticker = _text(root.find(".//issuerTradingSymbol"))
    owner_name = _text(root.find(".//rptOwnerName"))

    txn = root.find(".//nonDerivativeTransaction")
    trade_date = None
    trade_type = None
    shares = None
    price = None

    if txn is not None:
        date_str = _text(txn.find(".//transactionDate/value"))
        if date_str:
            trade_date = date.fromisoformat(date_str)

        code = _text(txn.find(".//transactionAcquiredDisposedCode/value"))
        trade_type = "buy" if code == "A" else "sell"

        shares_str = _text(txn.find(".//transactionShares/value"))
        if shares_str:
            try:
                shares = float(shares_str)
            except ValueError:
                shares = None

        price_str = _text(txn.find(".//transactionPricePerShare/value"))
        if price_str:
            try:
                price = float(price_str)
            except ValueError:
                price = None

    return {
        "issuer_name": issuer_name,
        "ticker": ticker,
        "owner_name": owner_name,
        "trade_date": trade_date,
        "trade_type": trade_type,
        "shares": shares,
        "price": price,
        "value_usd": (shares * price) if shares and price else None,
        "source": "sec",
        "raw_filing_url": filing_url,
    }


class SecCollector(BaseCollector):
    """Collects Form 4 insider transaction filings from SEC EDGAR."""

    def fetch_recent_form4_entries(self, count: int = 40) -> list[dict]:
        url = EDGAR_RSS_URL.format(count=count)
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        feed = feedparser.parse(resp.text)
        return [
            {"title": e.get("title", ""), "link": e.get("link", ""), "updated": e.get("updated", "")}
            for e in feed.entries
        ]

    def fetch_filing_xml(self, filing_url: str) -> str:
        resp = requests.get(filing_url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        return resp.text

    def collect(self, count: int = 40) -> list[dict[str, Any]]:
        """Fetch and parse recent Form 4 filings. Returns list of trade dicts."""
        entries = self.fetch_recent_form4_entries(count=count)
        results = []
        for entry in entries:
            try:
                xml_str = self.fetch_filing_xml(entry["link"])
                trade = parse_form4_xml(xml_str, entry["link"])
                results.append(trade)
            except Exception:
                continue
        return results
