from pathlib import Path

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


def find_and_process_frames(root_dir: Path, output_root: Path) -> bool:
    """Recursively find and process all PNG frames."""

    found_png_count = 0
    processed_count = 0
    skipped_count = 0
    failed_count = 0

    for png_path in sorted(root_dir.rglob("*.png")):
        found_png_count += 1

        relative_path = png_path.relative_to(root_dir)
        output_dir = output_root / relative_path.parent / relative_path.stem

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

    logger.info(f"\n{'='*60}")
    logger.info(
        f"Summary: {found_png_count} found, {processed_count} processed, "
        f"{skipped_count} skipped, {failed_count} failed"
    )
    logger.info(f"{'='*60}")

    return processed_count > 0 or failed_count > 0
