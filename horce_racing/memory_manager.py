import json
import os
from typing import List, Dict, Optional, Tuple


class MemoryManager:
    """Simple JSON-backed memory store for processed race segments.

    Each memory item has the structure::
        {
            "segment_id": "<video_name>",  # e.g. race1_00_01
            "start": 0,
            "end": 60,
            "commentary": "... generated commentary ..."
        }

    The file grows linearly and is loaded entirely into memory on init. This is OK
    for <1000 segments. For larger scales you should switch to a DB or vector
    store as demonstrated in memory-template, but this keeps dependencies light.
    """

    def __init__(self, store_path: str ) -> None:
        self.store_path = store_path
        self._memories: Dict[str, Dict] = {}
        self._load()

    # ---------------------------------------------------------------------
    # Public helpers
    # ---------------------------------------------------------------------
    def segment_processed(self, segment_id: str) -> bool:
        """Return True if we already stored commentary for *segment_id*."""
        return segment_id in self._memories

    def save_segment(self, segment_id: str, start: int, end: int, commentary: str) -> None:
        """Persist commentary for a segment. Overwrites if exists (rare)."""
        self._memories[segment_id] = {
            "segment_id": segment_id,
            "start": start,
            "end": end,
            "commentary": commentary,
        }
        self._flush()

    def get_context(self, upto_start: int, window: int = 5) -> str:
        previous = [m for m in self._memories.values() if m["end"] < upto_start]
        previous.sort(key=lambda x: x["start"], reverse=True)
        recent = previous[:window]
        recent.sort(key=lambda x: x["start"])
        return "\n".join(m["commentary"] for m in recent)


    def _load(self) -> None:
        if os.path.exists(self.store_path):
            with open(self.store_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self._memories = data
                except json.JSONDecodeError:
                    # Corrupted file -> start fresh but keep backup
                    os.rename(self.store_path, self.store_path + ".bak")
        else:
            # Ensure directory exists
            directory = os.path.dirname(self.store_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

    def _flush(self) -> None:
        with open(self.store_path, "w", encoding="utf-8") as f:
            json.dump(self._memories, f, ensure_ascii=False, indent=2)
