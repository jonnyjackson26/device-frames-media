#!/usr/bin/env python3
"""Entrypoint for processing device frame assets.

This script scans device-frames-raw for unprocessed or outdated frames
and generates output PNGs and metadata.
"""

import sys
from pathlib import Path

from frame_processor import discover_unprocessed_frames, process_frame_list, generate_index_file
from frame_processor.common import logger


def main() -> int:
    workspace_root = Path(__file__).parent
    frames_input = workspace_root / "device-frames-raw"
    frames_output = workspace_root / "device-frames-output"

    if not frames_input.exists():
        logger.error(f"Input directory not found: {frames_input}")
        return 1

    logger.info(f"Scanning frames from: {frames_input}")
    logger.info(f"Output directory: {frames_output}")

    # Discover frames that need processing
    png_paths = discover_unprocessed_frames(frames_input, frames_output)
    
    if not png_paths:
        logger.info("No frames need processing")
        return 0

    logger.info(f"Found {len(png_paths)} frame(s) to process")

    # Process the frames
    processed_count, failed_count = process_frame_list(png_paths, frames_output)

    # Regenerate index
    logger.info("Generating index.json")
    generate_index_file(frames_output)

    logger.info(f"\n{'='*60}")
    logger.info(f"Summary: {processed_count} processed, {failed_count} failed")
    logger.info(f"{'='*60}")

    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
