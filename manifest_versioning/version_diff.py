"""Compare and diff dataset manifests."""

from typing import Dict, Any


def diff_manifests(manifest_a: Dict, manifest_b: Dict) -> Dict:
    """
    Compare two manifests and return structured diff.

    Args:
        manifest_a: "Before" manifest (older version)
        manifest_b: "After" manifest (newer version)

    Returns:
        Dict with diff details including:
        - version_from, version_to
        - source_batches_added, source_batches_removed
        - transformations_added, transformations_removed
        - frame_count_delta, size_gb_delta
        - class_distribution_changes
        - checksum_changes
        - lineage (if present in manifest_b)
        - summary (human-readable one-liner)
    """
    version_a = manifest_a.get("version", "unknown")
    version_b = manifest_b.get("version", "unknown")

    # Source batches diff
    batches_a = set(manifest_a.get("source_batches", []))
    batches_b = set(manifest_b.get("source_batches", []))
    batches_added = sorted(batches_b - batches_a)
    batches_removed = sorted(batches_a - batches_b)

    # Transformations diff (preserve order as lists)
    trans_a = manifest_a.get("transformations", [])
    trans_b = manifest_b.get("transformations", [])
    trans_added = [t for t in trans_b if t not in trans_a]
    trans_removed = [t for t in trans_a if t not in trans_b]

    # Frame and size diffs
    frames_a = manifest_a.get("metadata", {}).get("total_frames", 0)
    frames_b = manifest_b.get("metadata", {}).get("total_frames", 0)
    frame_delta = frames_b - frames_a

    size_a = manifest_a.get("metadata", {}).get("total_size_gb", 0)
    size_b = manifest_b.get("metadata", {}).get("total_size_gb", 0)
    size_delta = round(size_b - size_a, 2)

    # Class distribution changes
    dist_a = manifest_a.get("metadata", {}).get("class_distribution", {})
    dist_b = manifest_b.get("metadata", {}).get("class_distribution", {})

    all_classes = set(dist_a.keys()) | set(dist_b.keys())
    class_changes = {}
    for cls in sorted(all_classes):
        from_val = dist_a.get(cls, 0)
        to_val = dist_b.get(cls, 0)
        if abs(from_val - to_val) > 0.0001:
            class_changes[cls] = {
                "from": round(from_val, 4),
                "to": round(to_val, 4),
                "delta": round(to_val - from_val, 4)
            }

    # Checksum changes
    checksums_a = manifest_a.get("checksums", {})
    checksums_b = manifest_b.get("checksums", {})
    checksum_changes = {}
    for split in ["train_split", "val_split", "test_split"]:
        check_a = checksums_a.get(split)
        check_b = checksums_b.get(split)
        if check_a != check_b:
            checksum_changes[split] = {
                "from": check_a,
                "to": check_b,
                "changed": True
            }

    # Lineage
    lineage = manifest_b.get("lineage")

    # Summary string
    summary_parts = []
    if batches_added:
        summary_parts.append(f"+{len(batches_added)} batch{'es' if len(batches_added) > 1 else ''}")
    if batches_removed:
        summary_parts.append(f"-{len(batches_removed)} batch{'es' if len(batches_removed) > 1 else ''}")
    if trans_added:
        summary_parts.append(f"+{len(trans_added)} transform{'s' if len(trans_added) > 1 else ''}")
    if frame_delta != 0:
        summary_parts.append(f"{'+' if frame_delta > 0 else ''}{frame_delta} frames")
    if size_delta != 0:
        summary_parts.append(f"{'+' if size_delta > 0 else ''}{size_delta} GB")

    summary = f"{version_a} → {version_b}: " + ", ".join(summary_parts) if summary_parts else f"{version_a} → {version_b}: no changes"

    return {
        "version_from": version_a,
        "version_to": version_b,
        "created_at_from": manifest_a.get("created_at"),
        "created_at_to": manifest_b.get("created_at"),
        "source_batches_added": batches_added,
        "source_batches_removed": batches_removed,
        "transformations_added": trans_added,
        "transformations_removed": trans_removed,
        "frame_count_delta": frame_delta,
        "size_gb_delta": size_delta,
        "class_distribution_changes": class_changes,
        "checksum_changes": checksum_changes,
        "lineage": lineage,
        "summary": summary
    }


def format_diff(diff: Dict, color: bool = True) -> str:
    """
    Render a diff dict as human-readable multi-line string for CLI output.

    Args:
        diff: Diff dict from diff_manifests()
        color: Use ANSI color codes (green for +, red for -)

    Returns:
        Multi-line formatted string
    """
    lines = []

    # Summary
    lines.append(diff["summary"])
    lines.append("")

    # Source batches
    if diff["source_batches_added"]:
        for batch in diff["source_batches_added"]:
            colored = f"\033[32m+ {batch}\033[0m" if color else f"+ {batch}"
            lines.append(f"  Source batch added: {colored}")
    if diff["source_batches_removed"]:
        for batch in diff["source_batches_removed"]:
            colored = f"\033[31m- {batch}\033[0m" if color else f"- {batch}"
            lines.append(f"  Source batch removed: {colored}")

    # Transformations
    if diff["transformations_added"]:
        for trans in diff["transformations_added"]:
            colored = f"\033[32m+ {trans}\033[0m" if color else f"+ {trans}"
            lines.append(f"  Transform added: {colored}")
    if diff["transformations_removed"]:
        for trans in diff["transformations_removed"]:
            colored = f"\033[31m- {trans}\033[0m" if color else f"- {trans}"
            lines.append(f"  Transform removed: {colored}")

    # Metrics
    if diff["frame_count_delta"] != 0:
        arrow = "→" if diff["frame_count_delta"] > 0 else "←"
        lines.append(f"  Frame count: {arrow} {abs(diff['frame_count_delta'])} ({diff['frame_count_delta']:+d})")
    if diff["size_gb_delta"] != 0:
        arrow = "→" if diff["size_gb_delta"] > 0 else "←"
        lines.append(f"  Dataset size: {arrow} {abs(diff['size_gb_delta'])} GB ({diff['size_gb_delta']:+.2f})")

    # Class distribution
    if diff["class_distribution_changes"]:
        lines.append("  Class distribution changes:")
        for cls, changes in diff["class_distribution_changes"].items():
            delta_str = f"{changes['delta']:+.4f}"
            colored = f"\033[32m{delta_str}\033[0m" if color and changes['delta'] > 0 else (f"\033[31m{delta_str}\033[0m" if color else delta_str)
            lines.append(f"    {cls}: {changes['from']:.4f} → {changes['to']:.4f} ({colored})")

    # Checksums
    if diff["checksum_changes"]:
        lines.append("  Checksum changes (data modified):")
        for split, changes in diff["checksum_changes"].items():
            split_name = split.replace("_split", "").title()
            lines.append(f"    {split_name}: {changes['from'][:16]}... → {changes['to'][:16]}...")

    # Lineage
    if diff["lineage"]:
        lines.append("  Lineage:")
        if diff["lineage"].get("reason_for_update"):
            lines.append(f"    Reason: {diff['lineage']['reason_for_update']}")

    return "\n".join(lines)
