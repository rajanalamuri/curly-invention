"""Command-line interface for dataset manifest versioning."""

import json
import sys

import click

from .local_store import LocalStore
from .manifest import create_manifest
from .version_diff import diff_manifests, format_diff
from .checksums import verify_checksum


@click.group()
@click.option(
    "--registry",
    "-r",
    default=".dataver",
    envvar="DATAVER_REGISTRY",
    help="Path to local registry directory",
    show_default=True,
)
@click.pass_context
def main(ctx: click.Context, registry: str) -> None:
    """Dataset manifest versioning — local-first POC."""
    ctx.ensure_object(dict)
    ctx.obj["store"] = LocalStore(registry)


@main.command()
@click.option(
    "--version",
    "-v",
    required=True,
    help="Semantic version (e.g., dataset-v1.0.0)",
)
@click.option(
    "--output-location",
    "-o",
    required=True,
    help="Local path to dataset root",
)
@click.option(
    "--source-batch",
    "-b",
    multiple=True,
    required=True,
    help="Source batch path (repeatable)",
)
@click.option(
    "--transform",
    "-t",
    multiple=True,
    help="Transformation description (repeatable)",
)
@click.option(
    "--train-split",
    type=float,
    default=0.75,
    show_default=True,
)
@click.option(
    "--val-split",
    type=float,
    default=0.15,
    show_default=True,
)
@click.option(
    "--test-split",
    type=float,
    default=0.10,
    show_default=True,
)
@click.option(
    "--previous-version",
    help="Previous version for lineage",
)
@click.option(
    "--reason",
    help="Reason for this update",
)
@click.pass_context
def create(
    ctx: click.Context,
    version: str,
    output_location: str,
    source_batch: tuple,
    transform: tuple,
    train_split: float,
    val_split: float,
    test_split: float,
    previous_version: str,
    reason: str,
) -> None:
    """Create and register a new dataset version."""
    store = ctx.obj["store"]

    lineage = None
    if previous_version:
        lineage = {"previous_version": previous_version}
        if reason:
            lineage["reason_for_update"] = reason

    try:
        manifest = create_manifest(
            version=version,
            source_batches=list(source_batch),
            transformations=list(transform) if transform else [],
            output_location=output_location,
            train_split=train_split,
            val_split=val_split,
            test_split=test_split,
            lineage=lineage,
            store=store,
        )
        click.echo(
            click.style("✓ Created ", fg="green")
            + f"{version} ({manifest['metadata']['total_frames']} frames, "
            + f"{manifest['metadata']['total_size_gb']} GB)"
        )
    except FileExistsError as e:
        click.echo(click.style("✗ Error: ", fg="red") + str(e), err=True)
        sys.exit(1)
    except ValueError as e:
        click.echo(click.style("✗ Error: ", fg="red") + str(e), err=True)
        sys.exit(1)


@main.command()
@click.argument("version")
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output raw JSON",
)
@click.pass_context
def inspect(ctx: click.Context, version: str, as_json: bool) -> None:
    """Show manifest details for VERSION."""
    store = ctx.obj["store"]

    try:
        manifest = store.load_manifest(version)
    except KeyError as e:
        click.echo(click.style("✗ Error: ", fg="red") + str(e), err=True)
        sys.exit(1)

    if as_json:
        click.echo(json.dumps(manifest, indent=2))
    else:
        click.echo(f"Version: {manifest['version']}")
        click.echo(f"Created: {manifest['created_at']}")
        click.echo(f"Source batches: {len(manifest['source_batches'])}")
        for batch in manifest["source_batches"]:
            click.echo(f"  - {batch}")
        click.echo(f"Transformations: {len(manifest['transformations'])}")
        for trans in manifest["transformations"]:
            click.echo(f"  - {trans}")
        click.echo(f"Output: {manifest['output_location']}")
        click.echo("")

        meta = manifest.get("metadata", {})
        click.echo(f"Frames: {meta.get('total_frames', 0)}")
        click.echo(f"Size: {meta.get('total_size_gb', 0)} GB")
        click.echo("Splits:")
        splits = meta.get("split", {})
        click.echo(f"  Train: {splits.get('train', 0):.2%}")
        click.echo(f"  Val:   {splits.get('val', 0):.2%}")
        click.echo(f"  Test:  {splits.get('test', 0):.2%}")
        click.echo("Class distribution:")
        for cls, dist in meta.get("class_distribution", {}).items():
            click.echo(f"  {cls}: {dist:.4f}")


@main.command(name="list")
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output raw JSON",
)
@click.pass_context
def list_versions(ctx: click.Context, as_json: bool) -> None:
    """List all registered dataset versions."""
    store = ctx.obj["store"]
    versions = store.list_versions()

    if not versions:
        click.echo("No versions registered.")
        return

    if as_json:
        click.echo(json.dumps(versions, indent=2))
    else:
        click.echo(f"Registered versions ({len(versions)}):")
        for version in versions:
            try:
                manifest = store.load_manifest(version)
                frames = manifest.get("metadata", {}).get("total_frames", 0)
                size = manifest.get("metadata", {}).get("total_size_gb", 0)
                created = manifest.get("created_at", "")[:10]
                click.echo(f"  {version:25} | {frames:6d} frames | {size:8.2f} GB | {created}")
            except KeyError:
                click.echo(f"  {version} (error loading)")


@main.command()
@click.argument("version_a")
@click.argument("version_b")
@click.option(
    "--no-color",
    is_flag=True,
    help="Disable colored output",
)
@click.pass_context
def diff(ctx: click.Context, version_a: str, version_b: str, no_color: bool) -> None:
    """Show what changed between VERSION_A and VERSION_B."""
    store = ctx.obj["store"]

    try:
        manifest_a = store.load_manifest(version_a)
        manifest_b = store.load_manifest(version_b)
    except KeyError as e:
        click.echo(click.style("✗ Error: ", fg="red") + str(e), err=True)
        sys.exit(1)

    diff_result = diff_manifests(manifest_a, manifest_b)
    output = format_diff(diff_result, color=not no_color)
    click.echo(output)


@main.command()
@click.argument("version")
@click.pass_context
def verify(ctx: click.Context, version: str) -> None:
    """Verify data integrity checksums for VERSION."""
    store = ctx.obj["store"]

    try:
        manifest = store.load_manifest(version)
    except KeyError as e:
        click.echo(click.style("✗ Error: ", fg="red") + str(e), err=True)
        sys.exit(1)

    output_location = manifest.get("output_location")
    checksums = manifest.get("checksums", {})
    all_pass = True

    for split_name, checksum_str in checksums.items():
        split_dir = f"{output_location}/{split_name.replace('_split', '')}/"
        try:
            verify_checksum(split_dir, checksum_str)
            status = click.style("✓ PASS", fg="green")
            click.echo(f"{split_name:15} {status}")
        except Exception:
            status = click.style("✗ FAIL", fg="red")
            click.echo(f"{split_name:15} {status}", err=True)
            all_pass = False

    if not all_pass:
        sys.exit(1)


@main.command()
@click.argument("version")
@click.confirmation_option(
    prompt="This will permanently remove the version. Are you sure?"
)
@click.pass_context
def delete(ctx: click.Context, version: str) -> None:
    """Remove a version from the registry."""
    store = ctx.obj["store"]

    try:
        store.delete_manifest(version)
        click.echo(click.style("✓ Deleted ", fg="green") + version)
    except KeyError as e:
        click.echo(click.style("✗ Error: ", fg="red") + str(e), err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
