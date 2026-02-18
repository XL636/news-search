"""Base collector interface with retry support."""

import abc
import asyncio
import logging

from src.models.schemas import RawItem

logger = logging.getLogger(__name__)


class BaseCollector(abc.ABC):
    """Abstract base class for all data collectors.

    Subclasses implement `collect()`. Call `collect_with_retry()` for
    automatic retries with exponential backoff.
    """

    name: str = "base"
    max_retries: int = 3
    base_delay: float = 1.0  # seconds, doubles each retry

    @abc.abstractmethod
    async def collect(self) -> list[RawItem]:
        """Collect items from the data source. Returns list of RawItem."""
        ...

    async def collect_with_retry(self) -> list[RawItem]:
        """Wrapper that retries `collect()` on failure with exponential backoff."""
        last_exc: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                return await self.collect()
            except Exception as e:
                last_exc = e
                if attempt < self.max_retries:
                    delay = self.base_delay * (2 ** (attempt - 1))
                    logger.warning(
                        "%s: attempt %d/%d failed (%s), retrying in %.1fs...",
                        self.name, attempt, self.max_retries, e, delay,
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        "%s: all %d attempts failed. Last error: %s",
                        self.name, self.max_retries, e,
                    )
        raise last_exc  # type: ignore[misc]

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"
