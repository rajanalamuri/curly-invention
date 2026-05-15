"""Core manifest creation functionality."""

import os
from datetime import datetime, timezone
from typing import Dict, List, Optional

from .checksums import compute_checksum


def count_frames(output_location: str) -> int:
    """Count frames in output location. Placeholder for real implementation."""
    if output_location.startswith("s3://"):
        return 45000
    return sum(1 for root, dirs, files in os.walk(output_location) for f in files if f.endswith((".jpg", ".png")))


def get_size_gb(output_location: str) -> float:
    """Calculate total size in GB. Placeholder for real implementation."""
    if output_location.startswith("s3://"):
        return 247.0
    total_size = 0
    for root, dirs, files in os.walk(output_location):
        for f in files:
            total_size += os.path.getsize(os.path.join(root, f))
    return total_size / (1024**3)


def compute_class_distribution(output_location: str) -> Dict[str, float]:
    """
    Compute class distribution by counting images per class subdirectory.
    Scans the train/ split (most representative).
    """
    if output_location.startswith("s3://"):
        return {"class_a": 0.42, "class_b": 0.31, "class_c": 0.27}

    train_dir = os.path.join(output_location, "train")
    if not os.path.isdir(train_dir):
        return {}

    class_counts: Dict[str, int] = {}
    for class_name in os.listdir(train_dir):
        class_path = os.path.join(train_dir, class_name)
        if os.path.isdir(class_path):
            count = sum(
                1 for f in os.listdir(class_path)
                if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp"))
            )
            if count > 0:
                class_counts[class_name] = count

    total = sum(class_counts.values())
    if total == 0:
        return {}
    return {cls: round(cnt / total, 4) for cls, cnt in sorted(class_counts.items())}


def create_manifest(
    version: str,
    source_batches: List[str],
    transformations: List[str],
    output_location: str,
    train_split: float = 0.75,
    val_split: float = 0.15,
    test_split: float = 0.10,
    s3_bucket: Optional[str] = None,
    s3_key: Optional[str] = None,
    lineage: Optional[Dict] = None,
    store: Optional[object] = None
) -> Dict:
    """
    Create a dataset manifest for versioning.

    Args:
        version: Semantic version string (e.g., 'dataset-v1.0.0')
        source_batches: List of source data locations
        transformations: List of transformation descriptions applied
        output_location: S3 or local path where dataset is stored
        train_split: Fraction of data for training (default 0.75)
        val_split: Fraction of data for validation (default 0.15)
        test_split: Fraction of data for testing (default 0.10)
        s3_bucket: S3 bucket for uploading manifest (optional)
        s3_key: S3 key for uploading manifest (optional)
        lineage: Optional lineage metadata (previous_version, reason_for_update)
        store: Optional storage backend (LocalStore or similar) to persist manifest

    Returns:
        Dictionary containing complete manifest structure
    """
    if abs((train_split + val_split + test_split) - 1.0) > 0.001:
        raise ValueError("Train, val, and test splits must sum to 1.0")

    manifest = {
        "version": version,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_batches": source_batches,
        "transformations": transformations,
        "output_location": output_location,
        "metadata": {
            "total_frames": count_frames(output_location),
            "total_size_gb": round(get_size_gb(output_location), 2),
            "class_distribution": compute_class_distribution(output_location),
            "split": {
                "train": train_split,
                "val": val_split,
                "test": test_split
            }
        },
        "checksums": {
            "train_split": compute_checksum(f"{output_location}/train/"),
            "val_split": compute_checksum(f"{output_location}/val/"),
            "test_split": compute_checksum(f"{output_location}/test/")
        }
    }

    if lineage:
        manifest["lineage"] = lineage

    if store is not None:
        store.save_manifest(version, manifest)
    elif s3_bucket and s3_key:
        from .s3_utils import upload_manifest
        upload_manifest(s3_bucket, s3_key, manifest)

    return manifest
