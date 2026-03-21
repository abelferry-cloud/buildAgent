"""s07: File-based state persistence for TaskManager."""

import json
import os
from pathlib import Path
from typing import Any


class FileStore:
    """
    Simple file-based key-value store with JSON serialization.

    Each key maps to a JSON file in the store directory.
    """

    def __init__(self, state_dir: str):
        """Initialize the file store with a directory path."""
        self._dir = Path(state_dir)
        self._dir.mkdir(parents=True, exist_ok=True)

    def _file_path(self, key: str) -> Path:
        """Get the file path for a key."""
        return self._dir / f"{key}.json"

    def get(self, key: str) -> dict | None:
        """
        Get a value by key.

        Returns None if the key doesn't exist.
        """
        path = self._file_path(key)
        if not path.exists():
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def set(self, key: str, value: dict) -> None:
        """Set a value for a key."""
        path = self._file_path(key)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(value, f, indent=2)

    def delete(self, key: str) -> bool:
        """Delete a key. Returns True if it existed, False otherwise."""
        path = self._file_path(key)
        if path.exists():
            path.unlink()
            return True
        return False

    def list_keys(self) -> list[str]:
        """List all keys in the store."""
        return [p.stem for p in self._dir.glob("*.json")]

    def exists(self, key: str) -> bool:
        """Check if a key exists."""
        return self._file_path(key).exists()

    def clear(self) -> None:
        """Remove all entries from the store."""
        for path in self._dir.glob("*.json"):
            path.unlink()
