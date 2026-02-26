import json
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np
from PIL import Image
from scipy import ndimage

from .common import (
    ALPHA_CLEAR,
    MAX_MASK_COVERAGE,
    MAX_SCREEN_RATIO,
    MIN_MASK_COVERAGE,
    MIN_REGION_AREA,
    MIN_SCREEN_RATIO,
    logger,
)
from .models import FrameTemplate, ScreenBounds


class DeviceFrameProcessor:
    """Process device frame PNGs to extract screen regions."""

    def __init__(self, input_path: Path, output_path: Path):
        self.input_path = input_path
        self.output_path = output_path
        self.output_path.mkdir(parents=True, exist_ok=True)

    def process(self) -> bool:
        """Process frame and generate outputs."""
        try:
            image_array, alpha = self._load_and_normalize()
            frame_width, frame_height = alpha.shape[1], alpha.shape[0]

            logger.info(f"Loaded frame: {frame_width}x{frame_height}")

            transparent_mask = alpha <= ALPHA_CLEAR
            labeled_array, num_features = ndimage.label(transparent_mask)
            logger.info(f"Found {num_features} transparent regions")

            screen_label = self._select_screen_candidate(
                labeled_array, frame_width, frame_height
            )

            if screen_label is None:
                logger.warning("No valid screen region found")
                return False

            screen_mask_binary = (labeled_array == screen_label).astype(np.uint8)

            bounds = self._extract_bounds(screen_mask_binary)
            logger.info(f"Screen bounds: {bounds}")

            final_mask = self._generate_screen_mask(
                labeled_array, screen_label, frame_width, frame_height
            )

            if not self._validate(final_mask, frame_width, frame_height, bounds):
                logger.warning("Validation failed - frame may need manual review")
                return False

            self._save_outputs(image_array, final_mask, bounds, frame_width, frame_height)

            logger.info(f"✓ Successfully processed {self.input_path.name}")
            return True

        except Exception as error:
            logger.error(
                f"Failed to process {self.input_path.name}: {error}",
                exc_info=True,
            )
            return False

    def _load_and_normalize(self) -> Tuple[np.ndarray, np.ndarray]:
        """Load PNG, convert to RGBA, extract alpha channel."""
        image = Image.open(self.input_path)

        if image.mode != "RGBA":
            image = image.convert("RGBA")

        image_array = np.array(image)

        alpha = image_array[:, :, 3].astype(np.float32)
        alpha = np.clip(
            alpha * 255 / alpha.max() if alpha.max() > 0 else alpha,
            0,
            255,
        ).astype(np.uint8)

        return image_array, alpha

    def _select_screen_candidate(
        self,
        labeled_array: np.ndarray,
        frame_width: int,
        frame_height: int,
    ) -> Optional[int]:
        """Select the largest valid transparent region as screen."""

        _ = frame_width, frame_height
        candidates = []

        for label in np.unique(labeled_array):
            if label == 0:
                continue

            region_mask = labeled_array == label

            if (
                region_mask[0, :].any()
                or region_mask[-1, :].any()
                or region_mask[:, 0].any()
                or region_mask[:, -1].any()
            ):
                continue

            area = np.count_nonzero(region_mask)
            if area < MIN_REGION_AREA:
                continue

            rows, cols = np.where(region_mask)
            if len(rows) == 0:
                continue

            min_row, max_row = rows.min(), rows.max()
            min_col, max_col = cols.min(), cols.max()

            region_height = max_row - min_row + 1
            region_width = max_col - min_col + 1

            if region_height == 0 or region_width == 0:
                continue

            aspect_ratio = max(region_height, region_width) / min(
                region_height,
                region_width,
            )

            if MIN_SCREEN_RATIO <= aspect_ratio <= MAX_SCREEN_RATIO:
                candidates.append((label, area, aspect_ratio))

        if not candidates:
            logger.warning("No candidates found matching aspect ratio constraints")
            return None

        candidates.sort(key=lambda item: item[1], reverse=True)

        selected_label, selected_area, selected_ratio = candidates[0]
        logger.info(
            "Selected region: "
            f"label={selected_label}, area={selected_area}, ratio={selected_ratio:.2f}"
        )

        return selected_label

    def _extract_bounds(self, region_mask: np.ndarray) -> ScreenBounds:
        """Extract bounding box from region mask."""
        rows, cols = np.where(region_mask > 0)

        min_x = int(cols.min())
        max_x = int(cols.max())
        min_y = int(rows.min())
        max_y = int(rows.max())

        return ScreenBounds(
            x=min_x,
            y=min_y,
            width=max_x - min_x + 1,
            height=max_y - min_y + 1,
        )

    def _generate_screen_mask(
        self,
        labeled_array: np.ndarray,
        screen_label: int,
        frame_width: int,
        frame_height: int,
    ) -> np.ndarray:
        """Generate binary screen mask with contour."""
        from scipy.ndimage import binary_dilation, binary_erosion

        screen_binary = labeled_array == screen_label

        eroded = binary_erosion(screen_binary, iterations=1)
        dilated = binary_dilation(eroded, iterations=1)

        mask = np.zeros((frame_height, frame_width), dtype=np.uint8)
        mask[dilated] = 255

        return mask

    def _validate(
        self,
        mask: np.ndarray,
        frame_width: int,
        frame_height: int,
        bounds: ScreenBounds,
    ) -> bool:
        """Validate generated mask."""

        frame_area = frame_width * frame_height
        mask_area = np.count_nonzero(mask)
        coverage = mask_area / frame_area

        if not (MIN_MASK_COVERAGE <= coverage <= MAX_MASK_COVERAGE):
            logger.warning(f"Coverage out of range: {coverage:.2f}")
            return False

        if (
            mask[0, :].any()
            or mask[-1, :].any()
            or mask[:, 0].any()
            or mask[:, -1].any()
        ):
            logger.warning("Mask touches image edges")
            return False

        if mask_area == 0:
            logger.warning("Mask is empty")
            return False

        mask_rows, mask_cols = np.where(mask > 0)
        if len(mask_rows) > 0:
            mask_min_x = int(mask_cols.min())
            mask_max_x = int(mask_cols.max())
            mask_min_y = int(mask_rows.min())
            mask_max_y = int(mask_rows.max())

            if not (
                bounds.x <= mask_min_x
                and mask_max_x <= bounds.x + bounds.width
                and bounds.y <= mask_min_y
                and mask_max_y <= bounds.y + bounds.height
            ):
                logger.warning("Bounding box doesn't enclose mask fully")
                return False

        logger.info(f"Validation passed: coverage={coverage:.2f}")
        return True

    def _save_outputs(
        self,
        image_array: np.ndarray,
        mask: np.ndarray,
        bounds: ScreenBounds,
        frame_width: int,
        frame_height: int,
    ) -> None:
        """Save frame.png, mask.png, and template.json."""

        frame_image = Image.fromarray(image_array, "RGBA")
        frame_path = self.output_path / "frame.png"
        frame_image.save(frame_path, "PNG")
        logger.info(f"Saved: {frame_path}")

        mask_image = Image.fromarray(mask, "L")
        mask_path = self.output_path / "mask.png"
        mask_image.save(mask_path, "PNG")
        logger.info(f"Saved: {mask_path}")

        template = FrameTemplate(
            frame="frame.png",
            mask="mask.png",
            screen=bounds.to_dict(),
            frameSize={"width": frame_width, "height": frame_height},
        )

        template_path = self.output_path / "template.json"
        with open(template_path, "w") as file_handle:
            json.dump(template.to_dict(), file_handle, indent=2)
        logger.info(f"Saved: {template_path}")
