"""Tests for manifest versioning."""

import json
import tempfile
from pathlib import Path

import pytest

from manifest_versioning import create_manifest
from manifest_versioning.checksums import compute_checksum, verify_checksum


def test_create_manifest_basic():
    """Test basic manifest creation."""
    manifest = create_manifest(
        version="dataset-v1.0.0",
        source_batches=["raw-data/batch-1/"],
        transformations=["filtered corrupt frames"],
        output_location="/tmp/test-dataset/",
        train_split=0.75,
        val_split=0.15,
        test_split=0.10
    )

    assert manifest["version"] == "dataset-v1.0.0"
    assert manifest["source_batches"] == ["raw-data/batch-1/"]
    assert manifest["transformations"] == ["filtered corrupt frames"]
    assert "created_at" in manifest
    assert manifest["metadata"]["split"]["train"] == 0.75


def test_create_manifest_invalid_splits():
    """Test that invalid splits raise error."""
    with pytest.raises(ValueError):
        create_manifest(
            version="dataset-v1.0.0",
            source_batches=["raw-data/batch-1/"],
            transformations=["filtered"],
            output_location="/tmp/test/",
            train_split=0.7,
            val_split=0.2,
            test_split=0.2
        )


def test_manifest_with_lineage():
    """Test manifest creation with lineage information."""
    lineage = {
        "previous_version": "dataset-v0.9.0",
        "reason_for_update": "added new batch"
    }
    manifest = create_manifest(
        version="dataset-v1.0.0",
        source_batches=["raw-data/batch-1/"],
        transformations=["filtered"],
        output_location="/tmp/test/",
        lineage=lineage
    )

    assert manifest["lineage"] == lineage


def test_compute_checksum():
    """Test checksum computation on temporary directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.txt"
        test_file.write_text("test content")

        checksum = compute_checksum(tmpdir)
        assert checksum.startswith("sha256:")
        assert len(checksum.split(":")[1]) == 64


def test_verify_checksum():
    """Test checksum verification."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.txt"
        test_file.write_text("test content")

        correct_checksum = compute_checksum(tmpdir)
        assert verify_checksum(tmpdir, correct_checksum)

        wrong_checksum = "sha256:0000000000000000000000000000000000000000000000000000000000000000"
        assert not verify_checksum(tmpdir, wrong_checksum)


def test_manifest_has_required_fields():
    """Test that all required fields are in manifest."""
    manifest = create_manifest(
        version="dataset-v1.0.0",
        source_batches=["raw-data/batch-1/"],
        transformations=["filtered"],
        output_location="/tmp/test/"
    )

    required_fields = ["version", "created_at", "source_batches", "transformations",
                       "output_location", "metadata", "checksums"]
    for field in required_fields:
        assert field in manifest

    assert "split" in manifest["metadata"]
    assert "train" in manifest["metadata"]["split"]
    assert "val" in manifest["metadata"]["split"]
    assert "test" in manifest["metadata"]["split"]
