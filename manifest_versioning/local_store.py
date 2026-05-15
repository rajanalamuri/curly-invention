"""Local file-based storage backend for dataset manifests."""

import json
import os
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional


class LocalStore:
    """
    File-based manifest registry using .dataver/ directory.

    Registry structure:
    .dataver/
    ├── registry.json       # index: {version: {path, created_at}}
    ├── dataset-v1.0.0.json
    └── dataset-v1.1.0.json
    """

    def __init__(self, registry_dir: str = ".dataver") -> None:
        """
        Initialize local store.

        Args:
            registry_dir: Path to registry directory (created if missing)
        """
        self.registry_dir = registry_dir
        os.makedirs(registry_dir, exist_ok=True)

    def save_manifest(self, version: str, manifest: Dict) -> str:
        """
        Persist manifest to JSON file and update registry.

        Args:
            version: Version string (e.g., 'dataset-v1.0.0')
            manifest: Manifest dictionary to save

        Returns:
            Path to saved manifest file

        Raises:
            FileExistsError: If version already registered
        """
        registry = self._load_registry()
        if version in registry:
            raise FileExistsError(f"Version {version} already exists")

        manifest_path = self._manifest_path(version)

        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        registry[version] = {
            "path": manifest_path,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        self._save_registry(registry)

        return manifest_path

    def load_manifest(self, version: str) -> Dict:
        """
        Load manifest for a specific version.

        Args:
            version: Version string

        Returns:
            Manifest dictionary

        Raises:
            KeyError: If version not found in registry
        """
        registry = self._load_registry()
        if version not in registry:
            raise KeyError(f"Version {version} not found in registry")

        manifest_path = self._manifest_path(version)
        with open(manifest_path) as f:
            return json.load(f)

    def list_versions(self) -> List[str]:
        """
        List all registered versions sorted by semantic versioning.

        Returns:
            List of version strings sorted by semver
        """
        registry = self._load_registry()
        versions = list(registry.keys())
        return sorted(versions, key=self._semver_key)

    def delete_manifest(self, version: str) -> None:
        """
        Remove a manifest version.

        Args:
            version: Version to delete

        Raises:
            KeyError: If version not found
        """
        registry = self._load_registry()
        if version not in registry:
            raise KeyError(f"Version {version} not found")

        manifest_path = self._manifest_path(version)
        if os.path.exists(manifest_path):
            os.remove(manifest_path)

        del registry[version]
        self._save_registry(registry)

    def _manifest_path(self, version: str) -> str:
        """Return absolute path for a version's manifest file."""
        return os.path.join(self.registry_dir, f"{version}.json")

    def _registry_path(self) -> str:
        """Return absolute path to registry.json."""
        return os.path.join(self.registry_dir, "registry.json")

    def _load_registry(self) -> Dict:
        """Load registry.json; return empty dict if missing."""
        registry_path = self._registry_path()
        if not os.path.exists(registry_path):
            return {}
        with open(registry_path) as f:
            return json.load(f)

    def _save_registry(self, registry: Dict) -> None:
        """Atomically write registry.json (write to .tmp then rename)."""
        registry_path = self._registry_path()
        tmp_path = registry_path + ".tmp"

        with open(tmp_path, "w") as f:
            json.dump(registry, f, indent=2)

        os.replace(tmp_path, registry_path)

    @staticmethod
    def _semver_key(version: str) -> tuple:
        """
        Extract semver tuple (major, minor, patch) from version string.
        Handles formats like 'dataset-v1.2.3' or '1.2.3'.
        """
        match = re.search(r"(\d+)\.(\d+)\.(\d+)", version)
        if match:
            return tuple(int(x) for x in match.groups())
        return (0, 0, 0)
