"""Device frame processing package."""

from .indexer import generate_index_file
from .pipeline import find_and_process_frames

__all__ = ["find_and_process_frames", "generate_index_file"]
