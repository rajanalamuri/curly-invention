"""
Example: Train a model with versioned data.

This example demonstrates how to load a dataset manifest and use it
to train a model while recording which dataset version was used.
"""

import json
from datetime import datetime, timezone
from manifest_versioning import load_manifest


def train_model(train_data: str, val_data: str):
    """Placeholder training function."""
    print(f"Training on: {train_data}")
    print(f"Validating on: {val_data}")
    return {"model": "trained"}


# Load the manifest
manifest = load_manifest("my-bucket", "training/dataset-v1.0.0/manifest.json")

print(f"Using dataset version: {manifest['version']}")
print(f"Dataset contains {manifest['metadata']['total_frames']} frames")
print(f"Class distribution: {manifest['metadata']['class_distribution']}")

# Train your model
model = train_model(
    train_data=f"{manifest['output_location']}/train/",
    val_data=f"{manifest['output_location']}/val/"
)

# Record which dataset version was used
model_metadata = {
    "model_version": "model-v1.0.0",
    "training_date": datetime.now(timezone.utc).isoformat(),
    "dataset_version": manifest["version"],
    "dataset_manifest": manifest
}

print("\nModel metadata:")
print(json.dumps(model_metadata, indent=2))

# In production, you would save this with your model artifact
# save_model_metadata(model_metadata)
