import logging

from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)


def retry_policy(
    attempts: int,
    exception_types: tuple[type[BaseException]] | type[BaseException] = Exception,
):
    return retry(
        stop=stop_after_attempt(attempts),
        retry=retry_if_exception_type(exception_types),
        wait=wait_exponential(multiplier=2, min=2, max=60),
        reraise=True,
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
