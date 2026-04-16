"""
Daily scheduler — runs the full Bloodhound pipeline once per day at 06:00 local time.
Usage: python scheduler.py
"""
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


def run_pipeline():
    log.info("Starting daily Bloodhound pipeline...")
    from cli_entry import cli
    from click.testing import CliRunner
    runner = CliRunner()
    result = runner.invoke(cli, ["run"])
    if result.exit_code != 0:
        log.error(f"Pipeline failed: {result.output}")
    else:
        log.info("Pipeline complete.")
        log.info(result.output)


if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(run_pipeline, CronTrigger(hour=6, minute=0))
    log.info("Bloodhound scheduler started — running daily at 06:00")
    log.info("Press Ctrl+C to stop.")
    try:
        scheduler.start()
    except KeyboardInterrupt:
        log.info("Scheduler stopped.")
