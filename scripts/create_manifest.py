#!/usr/bin/env python
"""
CLI script to create dataset manifests.

Used in CI/CD pipelines to automate manifest creation after data processing.
"""

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from manifest_versioning import create_manifest


def main():
    """Create a dataset manifest from command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Create a dataset manifest for data versioning"
    )
    parser.add_argument(
        "--version",
        required=True,
        help="Dataset version (e.g., dataset-v1.0.0)"
    )
    parser.add_argument(
        "--source-batches",
        nargs="+",
        required=True,
        help="Source data batch paths"
    )
    parser.add_argument(
        "--transformations",
        nargs="+",
        required=True,
        help="List of transformations applied"
    )
    parser.add_argument(
        "--output-location",
        required=True,
        help="S3 or local path where dataset is stored"
    )
    parser.add_argument(
        "--train-split",
        type=float,
        default=0.75,
        help="Training data fraction (default 0.75)"
    )
    parser.add_argument(
        "--val-split",
        type=float,
        default=0.15,
        help="Validation data fraction (default 0.15)"
    )
    parser.add_argument(
        "--test-split",
        type=float,
        default=0.10,
        help="Test data fraction (default 0.10)"
    )
    parser.add_argument(
        "--s3-bucket",
        help="S3 bucket for uploading manifest"
    )
    parser.add_argument(
        "--s3-key",
        help="S3 key for uploading manifest"
    )
    parser.add_argument(
        "--output-file",
        help="Local file to save manifest JSON"
    )

    args = parser.parse_args()

    # Create manifest
    manifest = create_manifest(
        version=args.version,
        source_batches=args.source_batches,
        transformations=args.transformations,
        output_location=args.output_location,
        train_split=args.train_split,
        val_split=args.val_split,
        test_split=args.test_split,
        s3_bucket=args.s3_bucket,
        s3_key=args.s3_key
    )

    # Output manifest
    print("Manifest created successfully:")
    print(json.dumps(manifest, indent=2))

    # Save to file if requested
    if args.output_file:
        with open(args.output_file, "w") as f:
            json.dump(manifest, f, indent=2)
        print(f"\nManifest saved to {args.output_file}")

    # Verify splits
    total = manifest["metadata"]["split"]["train"] + \
            manifest["metadata"]["split"]["val"] + \
            manifest["metadata"]["split"]["test"]
    print(f"\nDataset splits (sum={total:.2f}):")
    for split_name, split_value in manifest["metadata"]["split"].items():
        print(f"  {split_name}: {split_value:.1%}")


if __name__ == "__main__":
    main()
