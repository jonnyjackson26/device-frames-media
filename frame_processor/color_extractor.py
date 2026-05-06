"""Extract a representative hex color from a device frame PNG.

A device frame's cross-section, from outside to inside, looks like:

    [transparent background] [chamfer] [highlight] [body] [inner bezel] [screen]

The "body" segment is the device's actual color (e.g. "Cosmic Orange",
"Deep Purple"); the inner bezel between body and screen is near-black on
nearly every phone, and the outer chamfer/highlight are dark/specular. A
naive "first opaque pixel" approach lands on the chamfer; "most common
opaque pixel" lands on the inner bezel (since the bezel covers the most
area).

To find the body, for each row we walk inward from the outer edge through
opaque pixels, skipping near-black bezel pixels and stopping when we cross
into the bezel. We do the same from the right edge, and analogously per
column. The dominant quantized color among these samples is the body color.
"""

from pathlib import Path

import numpy as np
from PIL import Image

SOLID_ALPHA_THRESHOLD = 240
EDGE_BAND_WIDTH = 25
BEZEL_BRIGHTNESS_MAX = 80
BEZEL_STREAK_REQUIRED = 2
BEZEL_RAMP_DROP = 3
QUANTIZATION_STEP = 16


def _collect_band_samples(
    indices: np.ndarray,
    line: np.ndarray,
    out: list,
) -> None:
    """Walk inward from a line's outer edge, collecting body pixels.

    Stops once we cross into the inner bezel — detected as a sustained run of
    BEZEL_STREAK_REQUIRED consecutive dark pixels. Once detected, drops the
    last BEZEL_RAMP_DROP samples since they're typically the brightness ramp
    from body into bezel and aren't the real body color (the ramp would
    otherwise dominate the histogram for variants where many rows share the
    same near-black ramp colors).
    """
    band: list = []
    dark_streak = 0
    seen_bright = False
    triggered = False
    for idx in indices[:EDGE_BAND_WIDTH]:
        pixel = line[idx]
        is_dark = int(pixel[0]) + int(pixel[1]) + int(pixel[2]) <= BEZEL_BRIGHTNESS_MAX
        if is_dark:
            # Skip leading dark pixels (outer shadow chamfer on some phones,
            # e.g. iPhone XS, that starts with pure-black shadow before the
            # rail body). Once we've seen a bright body pixel, dark pixels
            # are bezel territory.
            if not seen_bright:
                continue
            dark_streak += 1
            if dark_streak >= BEZEL_STREAK_REQUIRED:
                triggered = True
                break
        else:
            seen_bright = True
            dark_streak = 0
        band.append(pixel)

    if triggered and len(band) > BEZEL_RAMP_DROP:
        band = band[:-BEZEL_RAMP_DROP]

    out.extend(band)


def extract_frame_hex_color(frame_path: Path) -> str:
    """Return the dominant outer-body color of a frame PNG as ``#RRGGBB``."""
    image = np.array(Image.open(frame_path).convert("RGBA"))
    rgb = image[:, :, :3]
    alpha = image[:, :, 3]

    samples: list[np.ndarray] = []

    for y in range(alpha.shape[0]):
        cols = np.where(alpha[y] >= SOLID_ALPHA_THRESHOLD)[0]
        if len(cols) >= 2:
            _collect_band_samples(cols, rgb[y], samples)
            _collect_band_samples(cols[::-1], rgb[y], samples)

    for x in range(alpha.shape[1]):
        rows = np.where(alpha[:, x] >= SOLID_ALPHA_THRESHOLD)[0]
        if len(rows) >= 2:
            _collect_band_samples(rows, rgb[:, x], samples)
            _collect_band_samples(rows[::-1], rgb[:, x], samples)

    if not samples:
        raise ValueError(f"No opaque body pixels found in {frame_path}")

    samples_array = np.stack(samples).astype(np.int32)

    quantized = (samples_array // QUANTIZATION_STEP) * QUANTIZATION_STEP
    keys = (
        quantized[:, 0] * 65536
        + quantized[:, 1] * 256
        + quantized[:, 2]
    )
    unique_keys, counts = np.unique(keys, return_counts=True)
    dominant_key = unique_keys[counts.argmax()]

    in_dominant_bucket = keys == dominant_key
    avg = samples_array[in_dominant_bucket].mean(axis=0)
    r, g, b = (int(round(channel)) for channel in avg)

    return f"#{r:02X}{g:02X}{b:02X}"
