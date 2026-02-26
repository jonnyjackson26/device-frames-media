import json
import re
from pathlib import Path
from typing import Dict
from urllib.parse import quote

from .common import GITHUB_PAGES_BASE_URL, logger


def _slugify(value: str) -> str:
    """Convert display names to stable kebab-case keys."""
    slug = value.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def _build_asset_url(base_url: str, relative_path: Path, filename: str) -> str:
    """Build a URL-safe asset link from an output-relative path and filename."""
    url_parts = [quote(part, safe="") for part in relative_path.parts]
    return f"{base_url.rstrip('/')}/{'/'.join(url_parts)}/{filename}"


def generate_index_file(
    output_root: Path,
    base_url: str = GITHUB_PAGES_BASE_URL,
) -> None:
    """Generate index.json for all processed frame variants."""
    index: Dict[str, Dict] = {}

    template_paths = sorted(output_root.rglob("template.json"))
    for template_path in template_paths:
        relative_dir = template_path.parent.relative_to(output_root)

        if len(relative_dir.parts) < 3:
            logger.warning(f"Skipping unexpected template path: {template_path}")
            continue

        device_type, device_model, variant = relative_dir.parts[:3]

        with open(template_path, "r") as file_handle:
            template_data = json.load(file_handle)

        type_key = _slugify(device_type)
        model_key = _slugify(device_model)
        variant_key = _slugify(variant)

        index.setdefault(type_key, {})
        index[type_key].setdefault(model_key, {})
        index[type_key][model_key][variant_key] = {
            "frame": _build_asset_url(base_url, relative_dir, "frame.png"),
            "mask": _build_asset_url(base_url, relative_dir, "mask.png"),
            "screen": template_data.get("screen", {}),
            "frameSize": template_data.get("frameSize", {}),
        }

    index_path = output_root / "index.json"
    with open(index_path, "w") as file_handle:
        json.dump(index, file_handle, indent=2)

    logger.info(f"Saved index: {index_path}")
    logger.info(f"Indexed templates: {len(template_paths)}")
