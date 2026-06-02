import os
import time
import logging
from worker.celery_app import celery

logger = logging.getLogger(__name__)

TRYON_RESULTS_DIR = "/app/static/tryon_results"
DEFAULT_MAX_AGE_HOURS = 24


@celery.task(name="worker.tasks.cleanup.cleanup_old_tryon_results")
def cleanup_old_tryon_results(max_age_hours: int = DEFAULT_MAX_AGE_HOURS):
    """
    Удаляет файлы результатов примерки старше max_age_hours.
    """
    if not os.path.exists(TRYON_RESULTS_DIR):
        logger.info(f"Directory {TRYON_RESULTS_DIR} does not exist, skipping")
        return {"deleted": 0, "skipped": 0}

    now = time.time()
    max_age_seconds = max_age_hours * 3600
    deleted = 0
    skipped = 0
    errors = []

    for filename in os.listdir(TRYON_RESULTS_DIR):
        filepath = os.path.join(TRYON_RESULTS_DIR, filename)

        # Пропускаем директории
        if not os.path.isfile(filepath):
            skipped += 1
            continue

        try:
            file_age = now - os.path.getmtime(filepath)
            if file_age > max_age_seconds:
                os.remove(filepath)
                deleted += 1
                logger.info(f"Deleted old try-on result: {filename}")
        except Exception as e:
            error_msg = f"Error deleting {filename}: {e}"
            logger.error(error_msg)
            errors.append(error_msg)

    result = {
        "deleted": deleted,
        "skipped": skipped,
        "errors": errors,
        "max_age_hours": max_age_hours,
    }
    logger.info(f"Cleanup completed: {result}")
    return result
