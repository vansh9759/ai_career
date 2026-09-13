import concurrent.futures
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("background_tasks")

class BackgroundTaskRunner:
    """Non-blocking background job queue using ThreadPoolExecutor for heavy operations."""
    _executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

    @classmethod
    def submit(cls, fn, *args, **kwargs):
        """Dispatches heavy function to background thread pool."""
        try:
            future = cls._executor.submit(fn, *args, **kwargs)
            logger.info(f"Submitted background task {fn.__name__} to ThreadPoolExecutor.")
            return future
        except Exception as e:
            logger.error(f"Failed to submit background task: {e}")
            return None
