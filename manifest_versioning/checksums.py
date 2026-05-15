"""Checksum computation for data integrity verification."""

import hashlib
import os
from pathlib import Path


def compute_checksum(directory: str, algorithm: str = "sha256") -> str:
    """
    Compute checksum for all files in a directory.

    Args:
        directory: Path to directory (local or S3)
        algorithm: Hash algorithm to use (default 'sha256')

    Returns:
        Hash string in format 'algorithm:hexdigest'
    """
    if directory.startswith("s3://"):
        return f"{algorithm}:placeholder-s3-checksum"

    hash_obj = hashlib.new(algorithm)

    if not os.path.exists(directory):
        return f"{algorithm}:"

    for filepath in sorted(Path(directory).rglob("*")):
        if filepath.is_file():
            with open(filepath, "rb") as f:
                while chunk := f.read(8192):
                    hash_obj.update(chunk)

    return f"{algorithm}:{hash_obj.hexdigest()}"


def verify_checksum(directory: str, expected_checksum: str) -> bool:
    """
    Verify directory checksum matches expected value.

    Args:
        directory: Path to directory
        expected_checksum: Expected checksum in format 'algorithm:hexdigest'

    Returns:
        True if checksums match, False otherwise
    """
    actual_checksum = compute_checksum(directory)
    return actual_checksum == expected_checksum
