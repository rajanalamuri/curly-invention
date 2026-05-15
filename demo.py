#!/usr/bin/env python3
"""
End-to-end demo of dataset versioning POC.

Generates synthetic CV data, creates versioned datasets, and demonstrates
the full lifecycle: create, list, inspect, diff, verify.
"""

import os
import shutil
import tempfile
from pathlib import Path

from manifest_versioning import LocalStore, create_manifest, diff_manifests, format_diff
from manifest_versioning.checksums import verify_checksum


# Minimal JPEG header (10 bytes) to avoid creating real image files
JPEG_HEADER = bytes([0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46])


def write_fake_image(filepath: str) -> None:
    """Write a minimal fake JPEG file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "wb") as f:
        f.write(JPEG_HEADER + bytes(100))  # 110 bytes total


def create_dataset_v1(dataset_dir: str) -> None:
    """Create v1.0.0 dataset structure."""
    print("  Generating v1.0.0 data structure...")

    # Train split
    for i in range(150):
        write_fake_image(f"{dataset_dir}/train/car/frame_{i:04d}.jpg")
    for i in range(100):
        write_fake_image(f"{dataset_dir}/train/truck/frame_{i:04d}.jpg")
    for i in range(50):
        write_fake_image(f"{dataset_dir}/train/person/frame_{i:04d}.jpg")

    # Val split (15% of train)
    for i in range(34):
        write_fake_image(f"{dataset_dir}/val/car/frame_{i:04d}.jpg")
    for i in range(22):
        write_fake_image(f"{dataset_dir}/val/truck/frame_{i:04d}.jpg")
    for i in range(11):
        write_fake_image(f"{dataset_dir}/val/person/frame_{i:04d}.jpg")

    # Test split (10% of train)
    for i in range(23):
        write_fake_image(f"{dataset_dir}/test/car/frame_{i:04d}.jpg")
    for i in range(15):
        write_fake_image(f"{dataset_dir}/test/truck/frame_{i:04d}.jpg")
    for i in range(8):
        write_fake_image(f"{dataset_dir}/test/person/frame_{i:04d}.jpg")


def create_dataset_v2(dataset_dir: str) -> None:
    """Create v1.1.0 dataset (v1.0.0 + new cyclist class + more cars)."""
    print("  Extending dataset to v1.1.0...")

    # Add new cyclist class (v1.0.0 + v1.1.0)
    for i in range(30):
        write_fake_image(f"{dataset_dir}/train/cyclist/frame_{i:04d}.jpg")
    for i in range(7):
        write_fake_image(f"{dataset_dir}/val/cyclist/frame_{i:04d}.jpg")
    for i in range(4):
        write_fake_image(f"{dataset_dir}/test/cyclist/frame_{i:04d}.jpg")

    # Add more car images (new batch)
    for i in range(150, 170):
        write_fake_image(f"{dataset_dir}/train/car/frame_{i:04d}.jpg")
    for i in range(34, 38):
        write_fake_image(f"{dataset_dir}/val/car/frame_{i:04d}.jpg")
    for i in range(23, 26):
        write_fake_image(f"{dataset_dir}/test/car/frame_{i:04d}.jpg")


def main() -> None:
    """Run the full demonstration."""
    print("\n" + "=" * 70)
    print("DATASET VERSIONING POC - END-TO-END DEMO")
    print("=" * 70 + "\n")

    # Create temporary dataset directory
    with tempfile.TemporaryDirectory(prefix="gtv_demo_") as temp_dir:
        dataset_dir = os.path.join(temp_dir, "dataset")
        print(f"Step 0: Setup")
        print(f"  Dataset directory: {dataset_dir}\n")

        # Step 1: Create v1.0.0 data
        print(f"Step 1: Generate fake CV data for v1.0.0")
        create_dataset_v1(dataset_dir)
        print(f"  ✓ Generated 300 frames (car, truck, person)\n")

        # Step 2: Create manifest for v1.0.0
        print(f"Step 2: CREATE v1.0.0")
        store = LocalStore(".dataver")
        manifest_v1 = create_manifest(
            version="dataset-v1.0.0",
            source_batches=["raw-data/batch-2026-05-01/"],
            transformations=["image_resize", "normalize"],
            output_location=dataset_dir,
            train_split=0.75,
            val_split=0.15,
            test_split=0.10,
            store=store,
        )
        print(
            f"  ✓ Created dataset-v1.0.0: "
            f"{manifest_v1['metadata']['total_frames']} frames, "
            f"{manifest_v1['metadata']['total_size_gb']:.3f} GB\n"
        )

        # Step 3: List versions
        print(f"Step 3: LIST versions")
        versions = store.list_versions()
        print(f"  Registered versions ({len(versions)}):")
        for v in versions:
            m = store.load_manifest(v)
            frames = m["metadata"]["total_frames"]
            size = m["metadata"]["total_size_gb"]
            print(f"    {v:25} | {frames:4d} frames | {size:.3f} GB")
        print()

        # Step 4: Add v1.1.0 data
        print(f"Step 4: Generate additional data for v1.1.0")
        create_dataset_v2(dataset_dir)
        print(f"  ✓ Added cyclist class (+30 train, +7 val, +4 test)")
        print(f"  ✓ Added 20 new car images (new batch)\n")

        # Step 5: Create manifest for v1.1.0 with lineage
        print(f"Step 5: CREATE v1.1.0 with lineage")
        manifest_v2 = create_manifest(
            version="dataset-v1.1.0",
            source_batches=[
                "raw-data/batch-2026-05-01/",
                "raw-data/batch-2026-05-03/",
            ],
            transformations=[
                "image_resize",
                "normalize",
                "added cyclist class from manual annotation",
            ],
            output_location=dataset_dir,
            train_split=0.75,
            val_split=0.15,
            test_split=0.10,
            lineage={
                "previous_version": "dataset-v1.0.0",
                "reason_for_update": "Added new object class and expanded training set"
            },
            store=store,
        )
        print(
            f"  ✓ Created dataset-v1.1.0: "
            f"{manifest_v2['metadata']['total_frames']} frames, "
            f"{manifest_v2['metadata']['total_size_gb']:.3f} GB\n"
        )

        # Step 6: Inspect v1.1.0
        print(f"Step 6: INSPECT v1.1.0")
        print(f"  Version: {manifest_v2['version']}")
        print(f"  Created: {manifest_v2['created_at'][:10]}")
        print(f"  Source batches: {len(manifest_v2['source_batches'])}")
        for batch in manifest_v2["source_batches"]:
            print(f"    - {batch}")
        print(f"  Transformations: {len(manifest_v2['transformations'])}")
        for trans in manifest_v2["transformations"]:
            print(f"    - {trans}")
        meta = manifest_v2["metadata"]
        print(f"  Class distribution:")
        for cls, dist in meta["class_distribution"].items():
            print(f"    {cls:10} {dist:.4f}")
        print()

        # Step 7: Diff v1.0.0 → v1.1.0
        print(f"Step 7: DIFF v1.0.0 → v1.1.0")
        diff_result = diff_manifests(manifest_v1, manifest_v2)
        diff_output = format_diff(diff_result, color=False)
        for line in diff_output.split("\n"):
            print(f"  {line}")
        print()

        # Step 8: Verify v1.0.0 integrity
        print(f"Step 8: VERIFY v1.0.0 checksums")
        for split_name, checksum_str in manifest_v1["checksums"].items():
            split_dir = f"{dataset_dir}/{split_name.replace('_split', '')}/"
            try:
                verify_checksum(split_dir, checksum_str)
                print(f"  {split_name:15} ✓ PASS")
            except Exception as e:
                print(f"  {split_name:15} ✗ FAIL - {e}")
        print()

        # Step 9: List all versions (final)
        print(f"Step 9: FINAL - LIST all versions")
        versions = store.list_versions()
        print(f"  Total registered: {len(versions)}")
        for v in versions:
            m = store.load_manifest(v)
            frames = m["metadata"]["total_frames"]
            size = m["metadata"]["total_size_gb"]
            print(f"    {v:25} | {frames:4d} frames | {size:.3f} GB")
        print()

    # Show registry location
    print("=" * 70)
    print(f"✓ Demo complete!")
    print(f"✓ Registry saved to: .dataver/")
    print(f"  Contents:")
    for f in sorted(os.listdir(".dataver")):
        filepath = os.path.join(".dataver", f)
        size = os.path.getsize(filepath)
        print(f"    {f:30} ({size} bytes)")
    print()
    print("Next steps:")
    print("  - Inspect the registry: cat .dataver/registry.json")
    print("  - View a manifest: cat .dataver/dataset-v1.0.0.json")
    print("  - Use the CLI: pip install -e . && manifest-versioning list")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
