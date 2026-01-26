#!/usr/bin/env python3
"""
Device frame processor - Extract screen regions from device frames.

Processes PNG device frames to:
1. Normalize images and extract alpha channels
2. Classify pixels by opacity
3. Find the largest contiguous transparent region (screen)
4. Extract screen contour and generate masks
5. Output frame.png, mask.png, and template.json
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Tuple, List, Optional
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Alpha thresholds
ALPHA_CLEAR = 10      # Transparent threshold
ALPHA_SOLID = 245     # Solid threshold

# Constraints
# Aspect ratio bounds (portrait phones: 1.7-2.4, tablets: 1.3-1.6)
MIN_SCREEN_RATIO = 1.3    # Aspect ratio bounds
MAX_SCREEN_RATIO = 2.5
MIN_MASK_COVERAGE = 0.5   # Mask area / frame area
MAX_MASK_COVERAGE = 0.9
MIN_REGION_AREA = 5000    # Minimum region size (pixels)


@dataclass
class ScreenBounds:
    """Screen region bounding box."""
    x: int
    y: int
    width: int
    height: int
    
    def to_dict(self) -> Dict:
        return {
            "x": int(self.x),
            "y": int(self.y),
            "width": int(self.width),
            "height": int(self.height)
        }


@dataclass
class FrameTemplate:
    """Template data for a device frame."""
    frame: str
    mask: str
    screen: Dict
    frameSize: Dict
    
    def to_dict(self) -> Dict:
        return {
            "frame": self.frame,
            "mask": self.mask,
            "screen": self.screen,
            "frameSize": self.frameSize
        }


class DeviceFrameProcessor:
    """Process device frame PNGs to extract screen regions."""
    
    def __init__(self, input_path: Path, output_path: Path):
        self.input_path = input_path
        self.output_path = output_path
        self.output_path.mkdir(parents=True, exist_ok=True)
    
    def process(self) -> bool:
        """Process frame and generate outputs."""
        try:
            # Step 1: Load and normalize
            image_array, alpha = self._load_and_normalize()
            frame_width, frame_height = alpha.shape[1], alpha.shape[0]
            
            logger.info(f"Loaded frame: {frame_width}x{frame_height}")
            
            # Step 2-3: Classify pixels and create mask
            transparent_mask = alpha <= ALPHA_CLEAR
            
            # Step 3: Find contiguous transparent regions
            labeled_array, num_features = ndimage.label(transparent_mask)
            logger.info(f"Found {num_features} transparent regions")
            
            # Step 4: Select screen candidate
            screen_label = self._select_screen_candidate(
                labeled_array, transparent_mask, alpha, 
                frame_width, frame_height
            )
            
            if screen_label is None:
                logger.warning("No valid screen region found")
                return False
            
            # Extract screen region mask
            screen_mask_binary = (labeled_array == screen_label).astype(np.uint8)
            
            # Step 5: Extract bounding box
            bounds = self._extract_bounds(screen_mask_binary)
            logger.info(f"Screen bounds: {bounds}")
            
            # Step 6-7: Extract contour and generate mask
            final_mask = self._generate_screen_mask(
                image_array, alpha, labeled_array, screen_label,
                frame_width, frame_height
            )
            
            # Step 8: Validate
            if not self._validate(final_mask, frame_width, frame_height, bounds):
                logger.warning("Validation failed - frame may need manual review")
                return False
            
            # Save outputs
            self._save_outputs(image_array, final_mask, bounds, frame_width, frame_height)
            
            logger.info(f"✓ Successfully processed {self.input_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to process {self.input_path.name}: {e}", exc_info=True)
            return False
    
    def _load_and_normalize(self) -> Tuple[np.ndarray, np.ndarray]:
        """Load PNG, convert to RGBA, extract alpha channel."""
        image = Image.open(self.input_path)
        
        # Convert to RGBA
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Convert to numpy array
        image_array = np.array(image)
        
        # Extract alpha channel and normalize to [0-255]
        alpha = image_array[:, :, 3].astype(np.float32)
        alpha = np.clip(alpha * 255 / alpha.max() if alpha.max() > 0 else alpha, 0, 255).astype(np.uint8)
        
        return image_array, alpha
    
    def _select_screen_candidate(
        self,
        labeled_array: np.ndarray,
        transparent_mask: np.ndarray,
        alpha: np.ndarray,
        frame_width: int,
        frame_height: int
    ) -> Optional[int]:
        """Select the largest valid transparent region as screen."""
        
        height, width = labeled_array.shape
        candidates = []
        
        # Find regions not touching edges
        for label in np.unique(labeled_array):
            if label == 0:
                continue
            
            region_mask = (labeled_array == label)
            
            # Skip regions touching edges
            if (region_mask[0, :].any() or region_mask[-1, :].any() or
                region_mask[:, 0].any() or region_mask[:, -1].any()):
                continue
            
            # Calculate area
            area = np.count_nonzero(region_mask)
            
            # Skip tiny regions
            if area < MIN_REGION_AREA:
                continue
            
            # Calculate aspect ratio
            rows, cols = np.where(region_mask)
            if len(rows) == 0:
                continue
            
            min_row, max_row = rows.min(), rows.max()
            min_col, max_col = cols.min(), cols.max()
            
            region_height = max_row - min_row + 1
            region_width = max_col - min_col + 1
            
            if region_height == 0 or region_width == 0:
                continue
            
            aspect_ratio = max(region_height, region_width) / min(region_height, region_width)
            
            # Check aspect ratio (portrait/landscape screens)
            if MIN_SCREEN_RATIO <= aspect_ratio <= MAX_SCREEN_RATIO:
                candidates.append((label, area, aspect_ratio))
        
        if not candidates:
            logger.warning("No candidates found matching aspect ratio constraints")
            return None
        
        # Sort by area (largest first)
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        selected_label, selected_area, selected_ratio = candidates[0]
        logger.info(f"Selected region: label={selected_label}, area={selected_area}, ratio={selected_ratio:.2f}")
        
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
            height=max_y - min_y + 1
        )
    
    def _generate_screen_mask(
        self,
        image_array: np.ndarray,
        alpha: np.ndarray,
        labeled_array: np.ndarray,
        screen_label: int,
        frame_width: int,
        frame_height: int
    ) -> np.ndarray:
        """Generate binary screen mask with contour."""
        
        # Create base mask from labeled region
        screen_region = (labeled_array == screen_label).astype(np.uint8) * 255
        
        # Use Canny edge detection on alpha channel for fine contours
        from scipy.ndimage import binary_erosion, binary_dilation
        
        # Get the screen region as binary
        screen_binary = (labeled_array == screen_label)
        
        # Slightly erode and dilate to smooth and reduce edge artifacts
        eroded = binary_erosion(screen_binary, iterations=1)
        dilated = binary_dilation(eroded, iterations=1)
        
        # Create output mask
        mask = np.zeros((frame_height, frame_width), dtype=np.uint8)
        mask[dilated] = 255
        
        return mask
    
    def _validate(
        self,
        mask: np.ndarray,
        frame_width: int,
        frame_height: int,
        bounds: ScreenBounds
    ) -> bool:
        """Validate generated mask."""
        
        frame_area = frame_width * frame_height
        mask_area = np.count_nonzero(mask)
        coverage = mask_area / frame_area
        
        # Check coverage
        if not (MIN_MASK_COVERAGE <= coverage <= MAX_MASK_COVERAGE):
            logger.warning(f"Coverage out of range: {coverage:.2f}")
            return False
        
        # Check mask doesn't touch edges
        if (mask[0, :].any() or mask[-1, :].any() or
            mask[:, 0].any() or mask[:, -1].any()):
            logger.warning("Mask touches image edges")
            return False
        
        # Check contour is closed (no holes in solid regions - basic check)
        if mask_area == 0:
            logger.warning("Mask is empty")
            return False
        
        # Check bounds enclose mask
        mask_rows, mask_cols = np.where(mask > 0)
        if len(mask_rows) > 0:
            mask_min_x = int(mask_cols.min())
            mask_max_x = int(mask_cols.max())
            mask_min_y = int(mask_rows.min())
            mask_max_y = int(mask_rows.max())
            
            if not (bounds.x <= mask_min_x and mask_max_x <= bounds.x + bounds.width and
                    bounds.y <= mask_min_y and mask_max_y <= bounds.y + bounds.height):
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
        frame_height: int
    ):
        """Save frame.png, mask.png, and template.json."""
        
        # Save frame
        frame_image = Image.fromarray(image_array, 'RGBA')
        frame_path = self.output_path / "frame.png"
        frame_image.save(frame_path, 'PNG')
        logger.info(f"Saved: {frame_path}")
        
        # Save mask
        mask_image = Image.fromarray(mask, 'L')
        mask_path = self.output_path / "mask.png"
        mask_image.save(mask_path, 'PNG')
        logger.info(f"Saved: {mask_path}")
        
        # Save template
        template = FrameTemplate(
            frame="frame.png",
            mask="mask.png",
            screen=bounds.to_dict(),
            frameSize={
                "width": frame_width,
                "height": frame_height
            }
        )
        
        template_path = self.output_path / "template.json"
        with open(template_path, 'w') as f:
            json.dump(template.to_dict(), f, indent=2)
        logger.info(f"Saved: {template_path}")


def find_and_process_frames(root_dir: Path, output_root: Path):
    """Recursively find and process all PNG frames."""
    
    processed_count = 0
    failed_count = 0
    
    for png_path in sorted(root_dir.rglob("*.png")):
        # Create output directory structure
        relative_path = png_path.relative_to(root_dir)
        
        # Remove .png and create output directory
        output_dir = output_root / relative_path.parent / relative_path.stem
        
        logger.info(f"\nProcessing: {relative_path}")
        
        processor = DeviceFrameProcessor(png_path, output_dir)
        if processor.process():
            processed_count += 1
        else:
            failed_count += 1
    
    logger.info(f"\n{'='*60}")
    logger.info(f"Summary: {processed_count} processed, {failed_count} failed")
    logger.info(f"{'='*60}")


if __name__ == "__main__":
    import sys
    
    # Define paths
    workspace_root = Path(__file__).parent
    frames_input = workspace_root / "device-frames-raw"
    frames_output = workspace_root / "device-frames-output"
    
    if not frames_input.exists():
        logger.error(f"Input directory not found: {frames_input}")
        sys.exit(1)
    
    logger.info(f"Processing frames from: {frames_input}")
    logger.info(f"Output directory: {frames_output}")
    
    find_and_process_frames(frames_input, frames_output)
