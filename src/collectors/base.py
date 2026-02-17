"""Base collector interface."""

import abc
import logging

from src.models.schemas import RawItem

logger = logging.getLogger(__name__)


class BaseCollector(abc.ABC):
    """Abstract base class for all data collectors."""

    name: str = "base"

    @abc.abstractmethod
    async def collect(self) -> list[RawItem]:
        """Collect items from the data source. Returns list of RawItem."""
        ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"
