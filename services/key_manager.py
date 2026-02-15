"""Key Manager for Bytez API key rotation and health tracking."""
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
import json


class KeyManager:
    """Manages multiple Bytez API keys with automatic rotation on failure."""

    def __init__(self):
        """Initialize KeyManager by loading keys from environment."""
        self.keys: List[str] = []
        self.current_key_index: int = 0
        self.failed_keys: set = set()
        self.usage_count: Dict[str, int] = {}
        self.error_count: Dict[str, int] = {}
        self.last_rotation_event: Optional[Dict[str, Any]] = None

        self._load_keys()

    def _load_keys(self) -> None:
        """Load keys from environment in order of preference."""
        # Try numbered keys first (BYTEZ_API_KEY_1, BYTEZ_API_KEY_2, ...)
        numbered_keys = []
        i = 1
        while True:
            key = os.getenv(f"BYTEZ_API_KEY_{i}")
            if not key:
                break
            numbered_keys.append(key)
            i += 1

        if numbered_keys:
            self.keys = numbered_keys
        else:
            # Try legacy comma-separated format
            comma_separated = os.getenv("BYTEZ_API_KEYS", "")
            if comma_separated:
                self.keys = [k.strip() for k in comma_separated.split(",") if k.strip()]
            else:
                # Try single key
                single_key = os.getenv("BYTEZ_API_KEY", "")
                if single_key:
                    self.keys = [single_key]

        if not self.keys:
            raise ValueError(
                "No Bytez API keys found. Set BYTEZ_API_KEY_1, BYTEZ_API_KEY_2, ... "
                "or BYTEZ_API_KEYS or BYTEZ_API_KEY"
            )

        # Initialize usage tracking
        for key in self.keys:
            self.usage_count[key] = 0
            self.error_count[key] = 0

    def get_current_key(self) -> str:
        """Get the currently active API key.

        Raises:
            RuntimeError: If current key is marked as failed or no healthy keys available.
        """
        if self.current_key_index >= len(self.keys):
            raise RuntimeError("All API keys exhausted")

        current_key = self.keys[self.current_key_index]

        if current_key in self.failed_keys:
            raise RuntimeError(
                f"Current key (index {self.current_key_index}) is marked as failed. "
                "Call rotate_key() to advance."
            )

        return current_key

    def mark_current_key_failed(self, reason: str = "Unknown error") -> None:
        """Mark the current key as failed and record the event.

        Args:
            reason: Description of why the key failed (e.g., "401 Unauthorized", "Rate limited")
        """
        current_key = self.keys[self.current_key_index]
        self.failed_keys.add(current_key)
        self.error_count[current_key] += 1

        self.last_rotation_event = {
            "type": "key_failed",
            "key_index": self.current_key_index,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
            "usage_count": self.usage_count[current_key],
            "error_count": self.error_count[current_key],
        }

    def rotate_key(self) -> bool:
        """Rotate to the next healthy key.

        Returns:
            True if a healthy key was found, False if all keys are exhausted.
        """
        start_index = self.current_key_index
        self.current_key_index += 1

        while self.current_key_index < len(self.keys):
            current_key = self.keys[self.current_key_index]
            if current_key not in self.failed_keys:
                self.last_rotation_event = {
                    "type": "key_rotated",
                    "from_index": start_index,
                    "to_index": self.current_key_index,
                    "timestamp": datetime.utcnow().isoformat(),
                }
                return True
            self.current_key_index += 1

        # All keys exhausted
        self.last_rotation_event = {
            "type": "all_keys_exhausted",
            "timestamp": datetime.utcnow().isoformat(),
            "total_keys": len(self.keys),
        }
        return False

    def record_success(self) -> None:
        """Record a successful API call for the current key."""
        current_key = self.keys[self.current_key_index]
        self.usage_count[current_key] += 1

    def get_and_clear_last_event(self) -> Optional[Dict[str, Any]]:
        """Get the last rotation/failure event and clear it.

        Returns:
            The last event dict, or None if no event has occurred.
        """
        event = self.last_rotation_event
        self.last_rotation_event = None
        return event

    def get_stats(self) -> Dict[str, Any]:
        """Get current key manager statistics."""
        return {
            "total_keys": len(self.keys),
            "current_key_index": self.current_key_index,
            "failed_keys_count": len(self.failed_keys),
            "usage_by_key": self.usage_count,
            "errors_by_key": self.error_count,
            "last_event": self.last_rotation_event,
        }


# Global singleton instance
_key_manager: Optional[KeyManager] = None


def get_key_manager() -> KeyManager:
    """Get or create the global KeyManager singleton."""
    global _key_manager
    if _key_manager is None:
        _key_manager = KeyManager()
    return _key_manager
