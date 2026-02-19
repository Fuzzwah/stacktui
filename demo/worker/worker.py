"""Fake background worker for the StackTUI demo.

Logs simulated job processing to both stdout (Docker logs) and a log file.
"""

import logging
import os
import random
import time

LOG_FILE = os.environ.get("LOG_FILE", "/app/logs/worker.log")

handlers = [logging.StreamHandler()]
log_dir = os.path.dirname(LOG_FILE)
if log_dir:
    os.makedirs(log_dir, exist_ok=True)
handlers.append(logging.FileHandler(LOG_FILE))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [worker] %(levelname)s %(message)s",
    handlers=handlers,
)
log = logging.getLogger(__name__)

JOBS = [
    "send_email",
    "resize_image",
    "sync_inventory",
    "generate_report",
    "process_payment",
    "update_cache",
    "send_notification",
]

STATUSES = ["ok", "ok", "ok", "ok", "ok", "ok", "ok", "slow", "retry"]

log.info("Worker started — processing jobs every 5 seconds")

while True:
    job = random.choice(JOBS)
    duration = round(random.uniform(0.05, 3.0), 2)
    status = random.choice(STATUSES)
    log.info("job=%s duration=%.2fs status=%s", job, duration, status)
    if status == "slow":
        log.warning("job=%s took %.2fs (slow threshold exceeded)", job, duration)
    time.sleep(5)
