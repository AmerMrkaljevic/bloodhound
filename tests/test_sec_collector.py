# tests/test_sec_collector.py
import pytest
import responses as resp_mock
from collectors.sec import SecCollector, parse_form4_xml

SAMPLE_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <title>4 - APPLE INC (0000320193) (Issuer)</title>
    <link href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000320193&type=4"/>
    <summary>Filed: 2024-01-15 AccNo: 0000320193-24-000001 Size: 5KB</summary>
    <updated>2024-01-15T10:00:00-05:00</updated>
  </entry>
</feed>"""

SAMPLE_FORM4_XML = """<?xml version="1.0"?>
<ownershipDocument>
  <issuer>
    <issuerCik>0000320193</issuerCik>
    <issuerName>APPLE INC</issuerName>
    <issuerTradingSymbol>AAPL</issuerTradingSymbol>
  </issuer>
  <reportingOwner>
    <reportingOwnerId>
      <rptOwnerCik>0000123456</rptOwnerCik>
      <rptOwnerName>Cook Timothy D</rptOwnerName>
    </reportingOwnerId>
    <reportingOwnerRelationship>
      <isOfficer>1</isOfficer>
      <officerTitle>CEO</officerTitle>
    </reportingOwnerRelationship>
  </reportingOwner>
  <nonDerivativeTable>
    <nonDerivativeTransaction>
      <securityTitle><value>Common Stock</value></securityTitle>
      <transactionDate><value>2024-01-10</value></transactionDate>
      <transactionAmounts>
        <transactionShares><value>1000</value></transactionShares>
        <transactionPricePerShare><value>185.50</value></transactionPricePerShare>
        <transactionAcquiredDisposedCode><value>A</value></transactionAcquiredDisposedCode>
      </transactionAmounts>
    </nonDerivativeTransaction>
  </nonDerivativeTable>
</ownershipDocument>"""


def test_parse_form4_xml_returns_trade_data():
    result = parse_form4_xml(SAMPLE_FORM4_XML, "https://sec.gov/test.xml")
    assert result["issuer_name"] == "APPLE INC"
    assert result["ticker"] == "AAPL"
    assert result["owner_name"] == "Cook Timothy D"
    assert result["trade_date"].isoformat() == "2024-01-10"
    assert result["trade_type"] == "buy"
    assert result["shares"] == 1000.0
    assert result["price"] == 185.50


def test_parse_form4_xml_sell_transaction():
    xml = SAMPLE_FORM4_XML.replace("<value>A</value>", "<value>D</value>")
    result = parse_form4_xml(xml, "https://sec.gov/test.xml")
    assert result["trade_type"] == "sell"


def test_parse_form4_xml_missing_price_returns_none():
    xml = SAMPLE_FORM4_XML.replace("<value>185.50</value>", "<value></value>")
    result = parse_form4_xml(xml, "https://sec.gov/test.xml")
    assert result["price"] is None


@resp_mock.activate
def test_sec_collector_fetches_recent_filings():
    resp_mock.add(
        resp_mock.GET,
        "https://www.sec.gov/cgi-bin/browse-edgar",
        body=SAMPLE_RSS,
        content_type="application/atom+xml",
    )
    collector = SecCollector()
    entries = collector.fetch_recent_form4_entries(count=40)
    assert len(entries) == 1
    assert "APPLE INC" in entries[0]["title"]
