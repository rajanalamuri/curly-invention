# Dataset Manifest Versioning

A lightweight approach to data versioning for ML pipelines without the overhead of specialized tools.

## Overview

Instead of versioning the data itself, version a manifest file that describes the data. This approach provides reproducibility, auditability, and operational simplicity.

## Quick Start

```bash
pip install boto3
python create_manifest.py --version dataset-v1.0.0 --output-location s3://my-bucket/datasets/
```

## Features

- **Simple**: One JSON file per dataset version
- **Reproducible**: Know exactly which data trained which model
- **Auditable**: All versioning decisions recorded in Git
- **Automated**: Manifest creation integrates into your CI/CD pipeline
- **Vendor-independent**: No proprietary format or lock-in

## Project Structure

```
.
├── manifest_versioning/
│   ├── __init__.py
│   ├── manifest.py          # Core manifest creation
│   ├── s3_utils.py          # S3 integration
│   └── checksums.py         # Checksum utilities
├── examples/
│   ├── create_manifest.py   # Example: Create a manifest
│   ├── train_model.py       # Example: Train with versioned data
│   └── manifest-example.json # Example manifest structure
├── tests/
│   └── test_manifest.py
├── .gitlab-ci.yml           # CI/CD pipeline example
└── README.md
```

## Usage

### 1. Create a Dataset Manifest

```python
from manifest_versioning.manifest import create_manifest

manifest = create_manifest(
    version="dataset-v1.0.0",
    source_batches=["raw-data/batch-2026-05-01/", "raw-data/batch-2026-05-02/"],
    transformations=[
        "removed frames with timestamp gaps > 5s",
        "filtered out frames with <3 modalities"
    ],
    output_location="s3://my-bucket/datasets/training/dataset-v1.0.0/",
    train_split=0.75,
    val_split=0.15,
    test_split=0.10
)
```

### 2. Train a Model with Versioned Data

```python
import json
import boto3
from manifest_versioning.s3_utils import load_manifest

s3 = boto3.client("s3")
manifest = load_manifest("my-bucket", "training/dataset-v1.0.0/manifest.json")

# Train your model
model = train_model(
    train_data=f"{manifest['output_location']}/train/",
    val_data=f"{manifest['output_location']}/val/"
)

# Record which dataset version was used
model_metadata = {
    "model_version": "model-v1.0.0",
    "dataset_version": manifest["version"],
    "dataset_manifest": manifest
}
```

### 3. Automate with CI/CD

See `.gitlab-ci.yml` for an example CI/CD pipeline that automatically creates manifests.

## Manifest Structure

```json
{
  "version": "dataset-v1.0.0",
  "created_at": "2026-05-12T10:30:00Z",
  "source_batches": [
    "raw-data/batch-2026-05-08/",
    "raw-data/batch-2026-05-09/"
  ],
  "transformations": [
    "removed frames with timestamp gaps > 5s",
    "filtered out frames with <3 modalities"
  ],
  "output_location": "s3://my-bucket/datasets/training/dataset-v1.0.0/",
  "metadata": {
    "total_frames": 45000,
    "total_size_gb": 247,
    "class_distribution": {
      "class_a": 0.42,
      "class_b": 0.31,
      "class_c": 0.27
    },
    "split": {
      "train": 0.75,
      "val": 0.15,
      "test": 0.10
    }
  },
  "checksums": {
    "train_split": "sha256:abc123...",
    "val_split": "sha256:def456...",
    "test_split": "sha256:ghi789..."
  },
  "lineage": {
    "previous_version": "dataset-v0.9.0",
    "reason_for_update": "added 2 new batches, filtered corrupt frames"
  }
}
```

## When to Graduate to Specialized Tools

This approach works well until:
- You have 50+ concurrent dataset versions
- Your data lineage becomes too complex to reason about manually
- You need collaborative features (simultaneous labeling, peer review)
- You require automatic deduplication across versions

At that point, consider DVC or MLflow.

## Next Steps (B2B SaaS Roadmap)

### Phase 1: Cloud & Collaboration
- [ ] **Web UI** — Dashboard for browsing versions, comparing diffs, managing lineage
- [ ] **GitHub Actions / CI/CD** — Auto-test on pushes, lint manifests, verify checksums
- [ ] **Cloud Storage Backends** — GCS, Azure Blob Storage alongside S3
- [ ] **Role-Based Access Control** — Teams, projects, permissions

### Phase 2: Enterprise Features
- [ ] **Audit Logging** — Who accessed/modified which versions, when
- [ ] **Webhooks** — Trigger ML pipelines on version creation
- [ ] **Data Retention Policies** — Auto-cleanup old versions
- [ ] **Cost Tracking** — Storage/compute usage per dataset version
- [ ] **Compliance** — SOC 2, HIPAA-ready, data residency controls

### Phase 3: Intelligence & Optimization
- [ ] **ML Insights** — Correlation between dataset changes and model performance
- [ ] **Automatic Anomaly Detection** — Flag unusual class distributions or drift
- [ ] **Dataset Recommendations** — Suggest which version to train on based on recent changes
- [ ] **Deduplication** — Identify and merge near-identical frames across versions

### Target Customers
- **Autonomous vehicles** (Tesla, Waymo competitors) — need reproducible training data
- **Robotics companies** — managing sensor data across fleet
- **Medical imaging** — regulatory/compliance-heavy, audit trail critical
- **Computer vision startups** — MVPs that will grow into multi-team orgs

## License

This software is licensed under the **Business Source License 1.1 (BSL 1.1)**.

**Key terms:**
- ✓ **Free to use** for individuals, academic research, and internal non-commercial use
- ✓ **Study and modify** the source code for your own purposes
- ✗ **Cannot redistribute** the software or derivatives as a competing product
- ✗ **Cannot use commercially** 

For commercial use, licensing inquiries, or to discuss custom terms, contact: rajanalamuri@gmail.com

### What This Means
You can use this code in your internal ML pipelines. You cannot:
- Offer this as a SaaS to other companies
- Resell or redistribute this software
- Build a competing product with substantially similar code

See [LICENSE](LICENSE) for full terms.
