"""Scheduler process that periodically enqueues background tasks.

This module uses RQ's built-in scheduler to schedule recurring tasks. When
executed as the main module it ensures that each job is scheduled exactly
once on startup. It can safely be restarted without duplicating jobs.
"""

import os
from redis import Redis
from rq import Queue
from rq.scheduler import Scheduler
from datetime import timedelta
import logging

import tasks  # relative import works because scheduler.py is in the same package


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connect to Redis
redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
redis_conn = Redis.from_url(redis_url)

queue = Queue(connection=redis_conn)
scheduler = Scheduler(queue=queue, connection=redis_conn)


def ensure(job_id: str, func, interval_seconds: int) -> None:
    """Ensure a repeating job exists and reschedule if necessary."""
    # Cancel existing jobs with same id
    for job in scheduler.get_jobs():
        if job.id == job_id:
            scheduler.cancel(job)
    scheduler.schedule(
        scheduled_time=None,  # run immediately
        func=func,
        interval=interval_seconds,
        repeat=None,
        id=job_id,
    )
    logger.info("Scheduled %s every %s seconds", job_id, interval_seconds)


def main() -> None:
    # Schedule tasks: minute sync every 60 seconds
    ensure("minute_sync", tasks.minute_sync, 60)
    # Media parser once per day (24h)
    ensure("media_parser", tasks.media_parser, 24 * 3600)
    # Tender parser twice per day (12h)
    ensure("tender_parser", tasks.tender_parser, 12 * 3600)
    # This scheduler process should stay alive, otherwise RQ cancels scheduled jobs
    import time
    while True:
        time.sleep(3600)


if __name__ == "__main__":
    main()
