from pathlib import Path
import shutil

from .common import logger
from .processor import DeviceFrameProcessor


def _is_output_up_to_date(input_path: Path, output_dir: Path) -> bool:
    """Return True when expected outputs exist and are newer than source PNG."""
    required_outputs = [
        output_dir / "frame.png",
        output_dir / "mask.png",
        output_dir / "template.json",
    ]

    if not all(path.exists() for path in required_outputs):
        return False

    input_mtime = input_path.stat().st_mtime
    oldest_output_mtime = min(path.stat().st_mtime for path in required_outputs)

    return oldest_output_mtime >= input_mtime


def _collect_existing_output_dirs(output_root: Path) -> set[Path]:
    """Return output-relative variant directories currently present in output."""
    existing_dirs: set[Path] = set()

    for marker_name in ("template.json", "frame.png", "mask.png"):
        for marker_path in output_root.rglob(marker_name):
            existing_dirs.add(marker_path.parent.relative_to(output_root))

    return existing_dirs


def _prune_stale_outputs(output_root: Path, expected_output_dirs: set[Path]) -> int:
    """Delete output variant directories that no longer have corresponding raw PNGs."""
    if not output_root.exists():
        return 0

    existing_output_dirs = _collect_existing_output_dirs(output_root)
    stale_output_dirs = sorted(existing_output_dirs - expected_output_dirs)

    removed_count = 0
    for relative_dir in stale_output_dirs:
        stale_dir = output_root / relative_dir
        if stale_dir.exists():
            shutil.rmtree(stale_dir)
            logger.info(f"Pruned stale output: {relative_dir}")
            removed_count += 1

    for directory in sorted(output_root.rglob("*"), key=lambda item: len(item.parts), reverse=True):
        if not directory.is_dir():
            continue
        if directory == output_root:
            continue
        if any(directory.iterdir()):
            continue
        directory.rmdir()

    return removed_count


def find_and_process_frames(root_dir: Path, output_root: Path) -> bool:
    """Recursively find and process all PNG frames."""

    found_png_count = 0
    processed_count = 0
    skipped_count = 0
    failed_count = 0
    expected_output_dirs: set[Path] = set()

    for png_path in sorted(root_dir.rglob("*.png")):
        found_png_count += 1

        relative_path = png_path.relative_to(root_dir)
        output_dir = output_root / relative_path.parent / relative_path.stem
        expected_output_dirs.add(relative_path.parent / relative_path.stem)

        if _is_output_up_to_date(png_path, output_dir):
            skipped_count += 1
            logger.info(f"Skipping unchanged: {relative_path}")
            continue

        logger.info(f"\nProcessing: {relative_path}")

        processor = DeviceFrameProcessor(png_path, output_dir)
        if processor.process():
            processed_count += 1
        else:
            failed_count += 1

    pruned_count = _prune_stale_outputs(output_root, expected_output_dirs)

    logger.info(f"\n{'='*60}")
    logger.info(
        f"Summary: {found_png_count} found, {processed_count} processed, "
        f"{skipped_count} skipped, {failed_count} failed, {pruned_count} pruned"
    )
    logger.info(f"{'='*60}")

    return processed_count > 0 or failed_count > 0 or pruned_count > 0
