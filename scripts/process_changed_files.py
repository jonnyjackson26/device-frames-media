#!/usr/bin/env python3
"""Process specific frame files provided by GitHub Actions.

This script processes only the files specified as arguments, skipping the
discovery step. It's designed to be called by GitHub Actions workflows.

Usage:
    python scripts/process_changed_files.py file1.png file2.png ...
    
Or with environment variable:
    CHANGED_FILES="file1.png file2.png" python scripts/process_changed_files.py
"""

import os
import sys
from pathlib import Path

from frame_processor import process_frame_list, generate_index_file
from frame_processor.common import logger


def main() -> int:
    workspace_root = Path(__file__).resolve().parent.parent
    frames_output = workspace_root / "device-frames-output"

    # Get file list from arguments or environment variable
    file_list = sys.argv[1:] if len(sys.argv) > 1 else os.environ.get("CHANGED_FILES", "").split()
    file_list = [f for f in file_list if f.strip()]

    if not file_list:
        logger.warning("No files specified to process")
        return 0

    # Convert to absolute paths
    png_paths = []
    for file_path in file_list:
        abs_path = workspace_root / file_path
        if not abs_path.exists():
            logger.warning(f"File not found: {abs_path}")
            continue
        if abs_path.suffix.lower() != ".png":
            logger.warning(f"Skipping non-PNG file: {file_path}")
            continue
        if "device-frames-raw" not in str(abs_path):
            logger.warning(f"Skipping file outside device-frames-raw: {file_path}")
            continue
        png_paths.append(abs_path)

    if not png_paths:
        logger.error("No valid PNG files to process")
        return 1

    logger.info(f"Processing {len(png_paths)} file(s)")

    # Process the frames
    processed_count, failed_count = process_frame_list(png_paths, frames_output)

    # Always regenerate index after processing
    logger.info("Generating index.json")
    generate_index_file(frames_output)

    logger.info(f"\n{'='*60}")
    logger.info(f"Summary: {processed_count} processed, {failed_count} failed")
    logger.info(f"{'='*60}")

    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
