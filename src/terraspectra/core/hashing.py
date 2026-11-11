"""Cryptographic and deterministic hashing for artifacts and configurations."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def hash_file(file_path: str | Path, block_size: int = 65536) -> str:
    """Compute hex SHA-256 digest of a file on disk.

    Args:
        file_path: Path to the target file.
        block_size: Read buffer size in bytes.

    Returns:
        64-character lowercase hexadecimal hash string.
    """
    p = Path(file_path)
    hasher = hashlib.sha256()
    with open(p, "rb") as f:
        while block := f.read(block_size):
            hasher.update(block)
    return hasher.hexdigest()


def hash_dict(data: dict[str, Any]) -> str:
    """Compute deterministic SHA-256 digest of dictionary contents.

    Args:
        data: Arbitrary dictionary.

    Returns:
        Hexadecimal hash string.
    """
    canonical_json = json.dumps(data, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
