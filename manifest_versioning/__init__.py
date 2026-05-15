"""Dataset manifest versioning for ML pipelines."""

from .manifest import create_manifest
from .local_store import LocalStore
from .version_diff import diff_manifests, format_diff
from .s3_utils import load_manifest, upload_manifest

__version__ = "0.1.0"
__all__ = [
    "create_manifest",
    "LocalStore",
    "diff_manifests",
    "format_diff",
    "load_manifest",
    "upload_manifest",
]
