import json
import os
from typing import Dict, List
from loguru import logger
from pathlib import Path

class MemoryManager:
    """JSON-backed memory store for processed race segments."""

    def __init__(self, store_path: str | Path) -> None:
        self.store_path = Path(store_path)
        self._memories: Dict[str, Dict] = {}
        self._load()

    def segment_processed(self, segment_id: str) -> bool:
        """Return True if we already stored commentary for *segment_id*."""
        return segment_id in self._memories

    def save_segment(self, segment_id: str, start: int, end: int, commentary: str) -> None:
        """Persist commentary for a segment."""
        self._memories[segment_id] = {
            "segment_id": segment_id,
            "start": start,
            "end": end,
            "commentary": commentary,
        }
        self._flush()

    def get_context(self, upto_start: int, window: int = 5) -> str:
        """Retrieve recent commentary history as context for the next generation."""
        previous = [m for m in self._memories.values() if m["end"] < upto_start]
        previous.sort(key=lambda x: x["start"], reverse=True)
        recent = previous[:window]
        recent.sort(key=lambda x: x["start"])
        return "\n".join(m["commentary"] for m in recent)

    def _load(self) -> None:
        if self.store_path.exists():
            try:
                with open(self.store_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self._memories = data
            except (json.JSONDecodeError, Exception) as e:
                logger.error(f"Failed to load memory from {self.store_path}: {e}")
                backup_path = self.store_path.with_suffix(".bak")
                self.store_path.rename(backup_path)
                logger.info(f"Corrupted memory file backed up to {backup_path}")
        else:
            self.store_path.parent.mkdir(parents=True, exist_ok=True)

    def _flush(self) -> None:
        with open(self.store_path, "w", encoding="utf-8") as f:
            json.dump(self._memories, f, ensure_ascii=False, indent=2)
