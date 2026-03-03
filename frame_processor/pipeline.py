from pathlib import Path
import shutil

from .common import logger
from .processor import DeviceFrameProcessor


def _is_output_up_to_date(input_path: Path, output_dir: Path) -> bool:
    """Check if output files are up-to-date with source PNG.
    
    Returns True when all expected outputs exist and are newer than the source file.
    """
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


def discover_unprocessed_frames(input_root: Path, output_root: Path) -> list[Path]:
    """Find all PNG frames that need processing.
    
    Returns list of PNG paths that either have no output or stale output.
    """
    unprocessed_frames: list[Path] = []

    for png_path in sorted(input_root.rglob("*.png")):
        relative_path = png_path.relative_to(input_root)
        output_dir = output_root / relative_path.parent / relative_path.stem

        if not _is_output_up_to_date(png_path, output_dir):
            unprocessed_frames.append(png_path)

    return unprocessed_frames


def process_frame_list(png_paths: list[Path], output_root: Path) -> tuple[int, int]:
    """Process a list of PNG frames.
    
    Args:
        png_paths: List of absolute paths to PNG files to process
        output_root: Root output directory
    
    Returns:
        Tuple of (processed_count, failed_count)
    """
    processed_count = 0
    failed_count = 0

    for png_path in png_paths:
        # Infer input root from the PNG path structure
        # Assume path is like: /root/device-frames-raw/Category/Model/variant.png
        parts = png_path.parts
        raw_index = next((i for i, p in enumerate(parts) if p == "device-frames-raw"), None)
        
        if raw_index is None:
            logger.warning(f"Skipping {png_path}: not in device-frames-raw directory")
            failed_count += 1
            continue
        
        input_root = Path(*parts[:raw_index]) / "device-frames-raw"
        relative_path = png_path.relative_to(input_root)
        output_dir = output_root / relative_path.parent / relative_path.stem

        logger.info(f"\nProcessing: {relative_path}")

        processor = DeviceFrameProcessor(png_path, output_dir)
        if processor.process():
            processed_count += 1
        else:
            failed_count += 1

    return processed_count, failed_count

    return processed_count > 0 or failed_count > 0 or pruned_count > 0
