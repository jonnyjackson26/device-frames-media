#!/usr/bin/env python3
"""Process only changed device frame files from git diff.

This script detects which files have been added, modified, or deleted in the
current commit and processes only those files. This is much faster than
scanning all files when most are unchanged.

Usage:
    python scripts/process_changed_files.py added_file1.png added_file2.png ... \\
                                             --deleted deleted_file1.png deleted_file2.png ...
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Set, Tuple

# Add parent directory to path so we can import frame_processor
sys.path.insert(0, str(Path(__file__).parent.parent))

from frame_processor import generate_index_file
from frame_processor.common import logger
from frame_processor.processor import DeviceFrameProcessor


def get_git_renames() -> dict[str, str]:
    """Detect file renames using git, returns mapping of old_path -> new_path.
    
    Returns empty dict if git command fails or no renames detected.
    """
    try:
        result = subprocess.run(
            ["git", "diff", "HEAD~1", "--name-status", "--find-renames=50%"],
            capture_output=True,
            text=True,
            check=True,
        )
        renames: dict[str, str] = {}
        for line in result.stdout.strip().split("\n"):
            if not line.startswith("R"):
                continue
            parts = line.split("\t")
            if len(parts) == 3:
                old_path, new_path = parts[1], parts[2]
                renames[old_path] = new_path
        return renames
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.warning("Could not detect renames via git")
        return {}


def process_changed_files(
    workspace_root: Path,
    changed_files: list[str],
    deleted_files: list[str],
) -> Tuple[int, int, int]:
    """Process only the specified changed files.
    
    Args:
        workspace_root: Root directory of the project
        changed_files: List of added/modified file paths (relative to repo root)
        deleted_files: List of deleted file paths (relative to repo root)
    
    Returns:
        Tuple of (processed_count, deleted_count, failed_count)
    """
    frames_raw = workspace_root / "device-frames-raw"
    frames_output = workspace_root / "device-frames-output"

    processed_count = 0
    deleted_count = 0
    failed_count = 0
    
    # Get rename mappings to handle deletions of renamed files
    renames = get_git_renames()

    # Process added and modified files
    for file_path in changed_files:
        raw_file = workspace_root / file_path
        
        # Skip if not a PNG or not in device-frames-raw
        if raw_file.suffix.lower() != ".png" or "device-frames-raw" not in str(raw_file):
            continue
        
        if not raw_file.exists():
            logger.warning(f"Changed file no longer exists: {file_path}")
            failed_count += 1
            continue
        
        # Calculate output directory
        relative_path = raw_file.relative_to(frames_raw)
        output_dir = frames_output / relative_path.parent / relative_path.stem
        
        logger.info(f"\nProcessing: {relative_path}")
        processor = DeviceFrameProcessor(raw_file, output_dir)
        
        if processor.process():
            processed_count += 1
        else:
            failed_count += 1
    
    # Process deleted files
    for file_path in deleted_files:
        # Check if this is a rename (old path of a rename)
        if file_path in renames:
            # For renames, delete old outputs and process new file
            logger.info(f"Detected rename: {file_path} -> {renames[file_path]}")
            # Process as deletion of old path
            old_relative_path = Path(file_path).relative_to(Path("device-frames-raw"))
            old_output_dir = frames_output / old_relative_path.parent / old_relative_path.stem
            if old_output_dir.exists():
                import shutil
                shutil.rmtree(old_output_dir)
                logger.info(f"Removed old output: {old_relative_path.parent / old_relative_path.stem}")
                deleted_count += 1
            # The new file should already be in changed_files, so it will be processed above
            continue
        
        # Regular deletion
        if "device-frames-raw" not in file_path:
            continue
        
        relative_path = Path(file_path).relative_to("device-frames-raw")
        output_dir = frames_output / relative_path.parent / relative_path.stem
        
        if output_dir.exists():
            shutil.rmtree(output_dir)
            logger.info(f"Removed output for deleted file: {relative_path.parent / relative_path.stem}")
            deleted_count += 1
            
            # Clean up empty parent directories
            parent = output_dir.parent
            while parent != frames_output and parent.exists():
                try:
                    if not any(parent.iterdir()):
                        parent.rmdir()
                        parent = parent.parent
                    else:
                        break
                except OSError:
                    break

    logger.info(f"\n{'='*60}")
    logger.info(
        f"Summary: {processed_count} processed, {deleted_count} deleted, {failed_count} failed"
    )
    logger.info(f"{'='*60}")

    return processed_count, deleted_count, failed_count


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Process only changed device frame files from git diff."
    )
    parser.add_argument(
        "--changed",
        default=None,
        help="Newline-separated list of changed files (from CHANGED_FILES env var)",
    )
    parser.add_argument(
        "--deleted",
        default=None,
        help="Newline-separated list of deleted files (from DELETED_FILES env var)",
    )

    args = parser.parse_args()

    workspace_root = Path(__file__).parent.parent
    
    # Read from environment variables if not provided as arguments
    changed_input = args.changed or os.environ.get("CHANGED_FILES", "")
    deleted_input = args.deleted or os.environ.get("DELETED_FILES", "")
    
    # Parse newline-separated lists
    changed_files = [f.strip() for f in changed_input.split("\n") if f.strip()]
    deleted_files = [f.strip() for f in deleted_input.split("\n") if f.strip()]
    
    if not changed_files and not deleted_files:
        logger.info("No changed files detected")
        return 0

    processed, deleted, failed = process_changed_files(
        workspace_root,
        changed_files,
        deleted_files,
    )

    # Regenerate index if any frames were processed or deleted
    if processed > 0 or deleted > 0:
        frames_output = workspace_root / "device-frames-output"
        generate_index_file(frames_output)

    # Return non-zero if there were processing failures (but not if just deletions/no changes)
    return 1 if failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
