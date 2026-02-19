"""APScheduler-based automatic task scheduler for InsightRadar."""

import json
import logging
from datetime import datetime
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

SETTINGS_FILE = Path(__file__).parent.parent / "data" / "settings.json"

# Default schedule: 08:00 UTC collect, 08:30 UTC snapshot
DEFAULT_COLLECT_HOUR = 8
DEFAULT_COLLECT_MINUTE = 0
DEFAULT_SNAPSHOT_HOUR = 8
DEFAULT_SNAPSHOT_MINUTE = 30


def _load_schedule_settings() -> dict:
    """Load schedule times from data/settings.json."""
    if SETTINGS_FILE.exists():
        try:
            data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
            return {
                "collect_hour": data.get("schedule_collect_hour", DEFAULT_COLLECT_HOUR),
                "collect_minute": data.get("schedule_collect_minute", DEFAULT_COLLECT_MINUTE),
                "snapshot_hour": data.get("schedule_snapshot_hour", DEFAULT_SNAPSHOT_HOUR),
                "snapshot_minute": data.get("schedule_snapshot_minute", DEFAULT_SNAPSHOT_MINUTE),
            }
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "collect_hour": DEFAULT_COLLECT_HOUR,
        "collect_minute": DEFAULT_COLLECT_MINUTE,
        "snapshot_hour": DEFAULT_SNAPSHOT_HOUR,
        "snapshot_minute": DEFAULT_SNAPSHOT_MINUTE,
    }


_scheduler: AsyncIOScheduler | None = None
_last_collect_run: str | None = None
_last_snapshot_run: str | None = None


async def _job_collect():
    """Scheduled job: run data collection from all sources."""
    global _last_collect_run
    logger.info("Scheduled collect job starting...")
    try:
        from src.pipeline import cmd_collect
        result = await cmd_collect()
        _last_collect_run = datetime.utcnow().isoformat()
        logger.info("Scheduled collect completed: %s", result)
    except Exception as e:
        logger.exception("Scheduled collect failed: %s", e)


async def _job_snapshot():
    """Scheduled job: take daily heat snapshot."""
    global _last_snapshot_run
    logger.info("Scheduled snapshot job starting...")
    try:
        from src.storage.store import get_connection, take_daily_snapshot
        conn = get_connection()
        count = take_daily_snapshot(conn)
        conn.close()
        _last_snapshot_run = datetime.utcnow().isoformat()
        logger.info("Scheduled snapshot completed: %d items", count)
    except Exception as e:
        logger.exception("Scheduled snapshot failed: %s", e)


def start_scheduler() -> AsyncIOScheduler:
    """Create and start the scheduler with configured jobs."""
    global _scheduler

    settings = _load_schedule_settings()

    _scheduler = AsyncIOScheduler()

    _scheduler.add_job(
        _job_collect,
        CronTrigger(hour=settings["collect_hour"], minute=settings["collect_minute"]),
        id="daily_collect",
        name="Daily data collection",
        replace_existing=True,
    )

    _scheduler.add_job(
        _job_snapshot,
        CronTrigger(hour=settings["snapshot_hour"], minute=settings["snapshot_minute"]),
        id="daily_snapshot",
        name="Daily heat snapshot",
        replace_existing=True,
    )

    _scheduler.start()
    logger.info(
        "Scheduler started: collect at %02d:%02d UTC, snapshot at %02d:%02d UTC",
        settings["collect_hour"], settings["collect_minute"],
        settings["snapshot_hour"], settings["snapshot_minute"],
    )
    return _scheduler


def stop_scheduler():
    """Shut down the scheduler gracefully."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
        _scheduler = None


def get_scheduler_status() -> dict:
    """Return current scheduler status for the API."""
    if not _scheduler or not _scheduler.running:
        return {"running": False}

    jobs = []
    for job in _scheduler.get_jobs():
        next_run = job.next_run_time
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": next_run.isoformat() if next_run else None,
        })

    return {
        "running": True,
        "jobs": jobs,
        "last_collect": _last_collect_run,
        "last_snapshot": _last_snapshot_run,
    }
