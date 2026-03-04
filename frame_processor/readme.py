"""Update the README device list section from the output directory."""

import re
from pathlib import Path
from urllib.parse import quote

from .common import logger

GITHUB_REPO_BASE = (
    "https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output"
)

START_HEADINGS = [
    "# List of Devices and Varations",
    "# List of Devices and Variations",
]

CATEGORY_ORDER = [
    ("Apple iPhone", "Apple iPhone"),
    ("Apple iPad", "Apple iPad"),
    ("Android Phone", "Android Phone"),
    ("Android Tablet", "Android Tablet"),
]


def _natural_sort_key(value: str):
    parts = re.split(r"(\d+)", value.lower())
    return [int(part) if part.isdigit() else part for part in parts]


def _generate_device_list_section(output_root: Path) -> str:
    lines = ["# List of Devices and Variations"]

    for directory_name, display_name in CATEGORY_ORDER:
        category_path = output_root / directory_name
        if not category_path.exists() or not category_path.is_dir():
            continue

        lines.append(f"**{display_name}:**")
        lines.append("")

        device_models = sorted(
            [path for path in category_path.iterdir() if path.is_dir()],
            key=lambda path: _natural_sort_key(path.name),
        )

        for model_path in device_models:
            variant_paths = sorted(
                [path for path in model_path.iterdir() if path.is_dir()],
                key=lambda path: _natural_sort_key(path.name),
            )

            if not variant_paths:
                continue

            variant_links = []
            for variant_path in variant_paths:
                github_path = f"{directory_name}/{model_path.name}/{variant_path.name}"
                github_url = f"{GITHUB_REPO_BASE}/{quote(github_path, safe='/')}"
                variant_links.append(f"[{variant_path.name}]({github_url})")

            lines.append(f" - {model_path.name}")
            lines.append(f"   - {', '.join(variant_links)}")

        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def update_readme(output_root: Path, readme_path: Path) -> bool:
    """Regenerate the device list section in README.md.

    Returns True if the file was changed.
    """
    readme_content = readme_path.read_text(encoding="utf-8")
    lines = readme_content.splitlines()

    start_index = None
    for index, line in enumerate(lines):
        if line.strip() in START_HEADINGS:
            start_index = index
            break

    if start_index is None:
        logger.warning("Could not find 'List of Devices and Variations' section in README.md — skipping")
        return False

    new_section = _generate_device_list_section(output_root)
    updated_content = "\n".join(lines[:start_index]).rstrip() + "\n\n" + new_section

    if updated_content != readme_content:
        readme_path.write_text(updated_content, encoding="utf-8")
        logger.info(f"Updated README: {readme_path}")
        return True

    logger.info("README already up to date")
    return False
