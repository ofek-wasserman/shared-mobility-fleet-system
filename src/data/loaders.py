from __future__ import annotations

import csv
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class DataLoader(ABC):
    """Abstract base class for CSV data loaders.

    Subclasses implement ``_parse_row`` to convert a raw CSV row
    (dict of strings) into a ``(primary_key, domain_object)`` pair.
    """

    def __init__(self, csv_path: str | Path) -> None:
        self.csv_path = Path(csv_path)

    def create_objects(self) -> dict[Any, Any]:
        """Load all rows and return a keyed dict of parsed objects."""
        rows = self._load_rows()
        return dict(self._parse_row(row) for row in rows)

    def _load_rows(self) -> list[dict[str, str]]:
        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV not found: {self.csv_path}")
        with self.csv_path.open(newline="", encoding="utf-8") as fh:
            return list(csv.DictReader(fh))

    @abstractmethod
    def _parse_row(self, row: dict[str, str]) -> tuple[Any, Any]:
        """Return (primary_key, domain_object) for a single CSV row."""
