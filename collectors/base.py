# collectors/base.py
from abc import ABC, abstractmethod
from typing import Any


class BaseCollector(ABC):
    """Abstract base for all data collectors."""

    @abstractmethod
    def collect(self, **kwargs) -> list[dict[str, Any]]:
        """Fetch raw records and return as list of dicts."""
        ...
