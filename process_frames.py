#!/usr/bin/env python3
"""Process device frame assets and update the README device list.

Usage
-----
# Process only frames whose raw files have changed (default):
    python process_frames.py

# Reprocess every frame regardless of modification time:
    python process_frames.py --all

# Process specific files (used by GitHub Actions via CHANGED_FILES env var
# or explicit args):
    python process_frames.py "device-frames-raw/Apple iPhone/16/Black.png" ...
    CHANGED_FILES="file1.png file2.png" python process_frames.py
"""

import argparse
import os
import shutil
import sys
from pathlib import Path

from frame_processor import (
    discover_unprocessed_frames,
    generate_index_file,
    process_frame_list,
    update_readme,
)
from frame_processor.common import logger

WORKSPACE_ROOT = Path(__file__).resolve().parent
FRAMES_INPUT = WORKSPACE_ROOT / "device-frames-raw"
FRAMES_OUTPUT = WORKSPACE_ROOT / "device-frames-output"
README_PATH = WORKSPACE_ROOT / "README.md"


def _resolve_explicit_files(file_list: list[str]) -> list[Path]:
    """Validate and resolve a list of file path strings to absolute Paths."""
    png_paths: list[Path] = []
    for file_path in file_list:
        abs_path = (WORKSPACE_ROOT / file_path).resolve()
        if not abs_path.exists():
            logger.warning(f"File not found: {abs_path}")
            continue
        if abs_path.suffix.lower() != ".png":
            logger.warning(f"Skipping non-PNG file: {file_path}")
            continue
        if "device-frames-raw" not in abs_path.parts:
            logger.warning(f"Skipping file outside device-frames-raw: {file_path}")
            continue
        png_paths.append(abs_path)
    return png_paths


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "files",
        nargs="*",
        metavar="FILE",
        help="Explicit PNG files to process (disables auto-discovery).",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        dest="force_all",
        help="Reprocess all frames, ignoring modification times.",
    )
    args = parser.parse_args()

    if not FRAMES_INPUT.exists():
        logger.error(f"Input directory not found: {FRAMES_INPUT}")
        return 1

    # ── Determine which files to process ────────────────────────────────────
    if args.files:
        # Explicit files from CLI args
        png_paths = _resolve_explicit_files(args.files)
        mode_label = f"{len(png_paths)} explicit file(s)"
    else:
        # Check CHANGED_FILES env var (set by GitHub Actions).
        # Use `get` with sentinel to distinguish "not set" from "set but empty":
        #   None  → local dev, fall back to mtime-based discovery
        #   ""    → CI run where no raw files changed; process nothing
        #   "..." → CI run with specific changed files
        env_value = os.environ.get("CHANGED_FILES")  # None if var is absent
        if env_value is not None and not args.force_all:
            file_list = [f.strip() for f in env_value.splitlines() if f.strip()]
            png_paths = _resolve_explicit_files(file_list)
            mode_label = f"{len(png_paths)} file(s) from CHANGED_FILES"
        else:
            # Local dev: mtime-based discovery (or --all to skip mtime check)
            png_paths = discover_unprocessed_frames(FRAMES_INPUT, FRAMES_OUTPUT, force=args.force_all)
            mode_label = "all frames" if args.force_all else "changed frames (mtime)"

    logger.info(f"Mode: {mode_label}")

    # ── Handle deleted / renamed raw frames ─────────────────────────────────
    # DELETED_FILES is set by GitHub Actions to include genuinely deleted files
    # AND the old paths of any renamed files so their output dirs get removed.
    deleted_env = os.environ.get("DELETED_FILES")
    deleted_count = 0
    if deleted_env:
        deleted_list = [f.strip() for f in deleted_env.splitlines() if f.strip()]
        for file_path in deleted_list:
            abs_path = (WORKSPACE_ROOT / file_path).resolve()
            try:
                rel = abs_path.relative_to(FRAMES_INPUT)
            except ValueError:
                logger.warning(f"Skipping deleted file outside device-frames-raw: {file_path}")
                continue
            output_dir = FRAMES_OUTPUT / rel.parent / rel.stem
            if output_dir.exists():
                logger.info(f"Removing output for deleted/renamed frame: {rel}")
                shutil.rmtree(output_dir)
                deleted_count += 1
            else:
                logger.info(f"No output directory to remove for: {rel}")

    if not png_paths:
        logger.info("No frames need processing")
    else:
        logger.info(f"Processing {len(png_paths)} frame(s)")
        processed_count, failed_count = process_frame_list(png_paths, FRAMES_OUTPUT)

        logger.info(f"\n{'='*60}")
        logger.info(f"Summary: {processed_count} processed, {failed_count} failed")
        logger.info(f"{'='*60}")

        if failed_count > 0:
            return 1

    logger.info("Generating index.json")
    generate_index_file(FRAMES_OUTPUT)

    # ── Update README ────────────────────────────────────────────────────────
    update_readme(FRAMES_OUTPUT, README_PATH)

    return 0


if __name__ == "__main__":
    sys.exit(main())

