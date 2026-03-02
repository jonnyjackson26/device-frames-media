#!/usr/bin/env python3
from pathlib import Path
import re
from urllib.parse import quote

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
README_PATH = WORKSPACE_ROOT / "README.md"
OUTPUT_ROOT = WORKSPACE_ROOT / "device-frames-output"

GITHUB_REPO_BASE = "https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output"

START_HEADINGS = [
    "# List of Devices and Varations",
    "# List of Devices and Variations",
]

CATEGORY_ORDER = [
    ("iOS", "iOS"),
    ("iPad", "iPad"),
    ("android-phone", "Android Phones"),
    ("android-tablet", "Android Tablets"),
]


def natural_sort_key(value: str):
    parts = re.split(r"(\d+)", value.lower())
    return [int(part) if part.isdigit() else part for part in parts]


def generate_device_list_section() -> str:
    lines = ["# List of Devices and Variations"]

    for directory_name, display_name in CATEGORY_ORDER:
        category_path = OUTPUT_ROOT / directory_name
        if not category_path.exists() or not category_path.is_dir():
            continue

        lines.append(f"**{display_name}:**")
        lines.append("")

        device_models = sorted(
            [path for path in category_path.iterdir() if path.is_dir()],
            key=lambda path: natural_sort_key(path.name),
        )

        for model_path in device_models:
            variant_paths = sorted(
                [path for path in model_path.iterdir() if path.is_dir()],
                key=lambda path: natural_sort_key(path.name),
            )

            if not variant_paths:
                continue

            # Create GitHub links for each variant
            variant_links = []
            for variant_path in variant_paths:
                github_path = f"{directory_name}/{model_path.name}/{variant_path.name}"
                github_url = f"{GITHUB_REPO_BASE}/{quote(github_path, safe='/')}"
                variant_links.append(f"[{variant_path.name}]({github_url})")
            
            lines.append(f" - {model_path.name}")
            lines.append(f"   - {', '.join(variant_links)}")

        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def update_readme_device_list() -> bool:
    readme_content = README_PATH.read_text(encoding="utf-8")
    lines = readme_content.splitlines()

    start_index = None
    for index, line in enumerate(lines):
        if line.strip() in START_HEADINGS:
            start_index = index
            break

    if start_index is None:
        raise ValueError("Could not find 'List of Devices and Variations' section in README.md")

    updated_content = "\n".join(lines[:start_index]).rstrip() + "\n\n" + generate_device_list_section()

    if updated_content != readme_content:
        README_PATH.write_text(updated_content, encoding="utf-8")
        return True

    return False


if __name__ == "__main__":
    changed = update_readme_device_list()
    print("README updated" if changed else "README already up to date")
