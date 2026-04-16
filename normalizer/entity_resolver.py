# normalizer/entity_resolver.py
from __future__ import annotations
from typing import Optional
from thefuzz import process


class EntityResolver:
    """Fuzzy-matches entity names against a known list to deduplicate."""

    def __init__(self, candidates: list[str]):
        self._candidates = candidates

    def resolve(self, name: str, threshold: int = 80) -> Optional[str]:
        """Return best matching candidate if score >= threshold, else None."""
        if not self._candidates:
            return None
        result = process.extractOne(name, self._candidates)
        if result is None:
            return None
        match, score = result[0], result[1]
        return match if score >= threshold else None

    def add(self, name: str):
        self._candidates.append(name)
