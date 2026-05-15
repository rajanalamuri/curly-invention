"""
Example: Create a dataset manifest.

This example demonstrates how to create a manifest for a versioned dataset
and upload it to S3.
"""

import json
from manifest_versioning import create_manifest

# Create a manifest
manifest = create_manifest(
    version="dataset-v1.0.0",
    source_batches=[
        "raw-data/batch-2026-05-01/",
        "raw-data/batch-2026-05-02/"
    ],
    transformations=[
        "removed frames with timestamp gaps > 5s",
        "filtered out frames with <3 modalities"
    ],
    output_location="s3://my-bucket/datasets/training/dataset-v1.0.0/",
    train_split=0.75,
    val_split=0.15,
    test_split=0.10
)

print(json.dumps(manifest, indent=2))

# To upload to S3, uncomment:
# manifest = create_manifest(
#     version="dataset-v1.0.0",
#     source_batches=[...],
#     transformations=[...],
#     output_location="s3://my-bucket/datasets/training/dataset-v1.0.0/",
#     train_split=0.75,
#     val_split=0.15,
#     test_split=0.10,
#     s3_bucket="my-bucket",
#     s3_key="training/dataset-v1.0.0/manifest.json"
# )
