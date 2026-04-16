# Bloodhound

> Follow the money.

Detects suspicious insider trading patterns by correlating public filings with news events.

## Install

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Full pipeline (collect → analyze → report)
python cli_entry.py run

# Individual steps
python cli_entry.py collect --source sec
python cli_entry.py analyze
python cli_entry.py report --min-score 50

# Daily scheduler (runs at 06:00)
python scheduler.py
```

## Alert levels

| Score | Level |
|---|---|
| 80–100 | 🔴 High suspicion |
| 50–79 | 🟡 Medium |
| 20–49 | 🟢 Low / watch |
| 0–19 | ⚪ No signal |

## Data sources (v1)

- SEC EDGAR Form 4 (US insider transactions)
- SEC 8-K filings + Yahoo Finance RSS (news events)
- yfinance (historical prices)

EU collectors, web dashboard, and backtesting: Plan 2.
