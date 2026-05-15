"""AWS S3 integration for manifest storage and retrieval."""

import json
from typing import Dict, Optional

try:
    import boto3
except ImportError:
    boto3 = None


def upload_manifest(bucket: str, key: str, manifest: Dict) -> None:
    """
    Upload manifest to S3.

    Args:
        bucket: S3 bucket name
        key: S3 object key (path)
        manifest: Manifest dictionary to upload
    """
    if not boto3:
        raise ImportError("boto3 is required for S3 operations. Install with: pip install boto3")

    s3 = boto3.client("s3")
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(manifest, indent=2),
        ContentType="application/json"
    )


def load_manifest(bucket: str, key: str) -> Dict:
    """
    Load manifest from S3.

    Args:
        bucket: S3 bucket name
        key: S3 object key (path)

    Returns:
        Parsed manifest dictionary
    """
    if not boto3:
        raise ImportError("boto3 is required for S3 operations. Install with: pip install boto3")

    s3 = boto3.client("s3")
    response = s3.get_object(Bucket=bucket, Key=key)
    manifest = json.load(response["Body"])
    return manifest


def list_manifest_versions(bucket: str, prefix: str = "training/") -> list:
    """
    List all dataset versions in S3.

    Args:
        bucket: S3 bucket name
        prefix: S3 prefix to search under (default 'training/')

    Returns:
        List of version strings found
    """
    if not boto3:
        raise ImportError("boto3 is required for S3 operations. Install with: pip install boto3")

    s3 = boto3.client("s3")
    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)

    versions = []
    for obj in response.get("Contents", []):
        if obj["Key"].endswith("manifest.json"):
            version = obj["Key"].split("/")[-2]
            versions.append(version)

    return sorted(versions)


def delete_manifest(bucket: str, key: str) -> None:
    """
    Delete manifest from S3.

    Args:
        bucket: S3 bucket name
        key: S3 object key (path)
    """
    if not boto3:
        raise ImportError("boto3 is required for S3 operations. Install with: pip install boto3")

    s3 = boto3.client("s3")
    s3.delete_object(Bucket=bucket, Key=key)
