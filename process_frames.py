#!/usr/bin/env python3
"""Entrypoint for processing device frame assets."""

import sys
from pathlib import Path

from frame_processor import find_and_process_frames, generate_index_file
from frame_processor.common import logger


def main() -> int:
    workspace_root = Path(__file__).parent
    frames_input = workspace_root / "device-frames-raw"
    frames_output = workspace_root / "device-frames-output"

    if not frames_input.exists():
        logger.error(f"Input directory not found: {frames_input}")
        return 1

    logger.info(f"Processing frames from: {frames_input}")
    logger.info(f"Output directory: {frames_output}")

    had_changes_or_failures = find_and_process_frames(frames_input, frames_output)

    if had_changes_or_failures or not (frames_output / "index.json").exists():
        generate_index_file(frames_output)
    else:
        logger.info("Skipping index generation: no frame changes detected")

    return 0


if __name__ == "__main__":
    sys.exit(main())
