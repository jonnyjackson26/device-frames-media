# Process Frames — Architecture & Algorithm

## Entry Point

All processing is driven by a single script:

```
python process_frames.py [OPTIONS] [FILE ...]
```

| Invocation | Behaviour |
|---|---|
| `python process_frames.py` | Process only frames whose raw source has changed (mtime comparison) |
| `python process_frames.py --all` | Force-reprocess every frame regardless of modification time |
| `python process_frames.py f1.png f2.png ...` | Process explicit files (used by GitHub Actions) |
| `CHANGED_FILES="f1\nf2" python process_frames.py` | Explicit files via environment variable (GitHub Actions) |
| add `--skip-readme` | Skip the README device list update step |

## Package Structure

```
process_frames.py          ← CLI entry point
frame_processor/
  __init__.py              ← public API exports
  pipeline.py              ← file discovery & orchestration
  processor.py             ← core image analysis (DeviceFrameProcessor)
  indexer.py               ← generates device-frames-output/index.json
  readme.py                ← updates README device list section
  models.py                ← ScreenBounds, FrameTemplate dataclasses
  common.py                ← shared logger & constants
```

## Pipeline Flow

```
1. Determine file list
   ├── Explicit files (CLI args or CHANGED_FILES env)
   ├── Changed only (default) — mtime check via pipeline.py
   └── All frames       (--all flag)

2. process_frame_list()   ← pipeline.py
   └── DeviceFrameProcessor.process()  ← processor.py (per frame)

3. generate_index_file()  ← indexer.py
   └── Writes device-frames-output/index.json

4. update_readme()        ← readme.py
   └── Rewrites "List of Devices and Variations" section in README.md
```

## Output per Frame

For each raw PNG at `device-frames-raw/<Type>/<Model>/<Variant>.png`, three files
are written to `device-frames-output/<Type>/<Model>/<Variant>/`:

| File | Contents |
|---|---|
| `frame.png` | Original PNG copied as-is (RGBA) |
| `mask.png` | Greyscale mask — white = screen area, black = frame |
| `template.json` | Screen bounding box + frame dimensions |

---

## Image Analysis Algorithm

The algorithm is defined in [frame_processor/processor.py](../frame_processor/processor.py).

#### Step 1: Normalize Image
- Load PNG and convert to RGBA
- Extract and normalise alpha channel to 0–255 range

#### Step 2: Classify Pixels by Opacity
- **Transparent** (α ≤ 10): Screen interior
- **Solid** (α ≥ 245): Device frame
- **Anti-aliased / edge**: Everything in between

#### Step 3: Find Contiguous Transparent Regions
- Connected-component labeling on the transparency mask
- Reject regions touching image borders (background, not screen)
- Reject tiny regions (holes, speaker grills — < 5 000 pixels)

#### Step 4: Select Screen Candidate
Chooses the region with:
- Largest area
- Aspect ratio within 1.3–2.5 (covers phones and tablets)
- Fully enclosed by opaque pixels

#### Step 5–6: Extract Bounds & Contour
- Calculate minX, minY, maxX, maxY of the selected region
- Generate bounding box (stored in `template.json` as `screen`)
- Extract precise screen contour using edge detection

#### Step 7: Generate Screen Mask
- Create blank image (same size as frame)
- Fill detected contour with white (255)
- Fill background with black (0)
- Feather inward by ~1 px to avoid edge bleed

#### Step 8: Validate
Checks that:
- Mask coverage is 50–90% of total frame area
- Mask does not touch any image edge
- Bounding box fully encloses the mask region

---

## Constants (frame_processor/common.py)

| Constant | Value | Purpose |
|---|---|---|
| `ALPHA_CLEAR` | 10 | Pixel is considered transparent below this alpha |
| `MIN_SCREEN_RATIO` | 1.3 | Minimum screen aspect ratio |
| `MAX_SCREEN_RATIO` | 2.5 | Maximum screen aspect ratio |
| `MIN_MASK_COVERAGE` | 0.5 | Minimum mask area / frame area |
| `MAX_MASK_COVERAGE` | 0.9 | Maximum mask area / frame area |
| `MIN_REGION_AREA` | 5 000 | Minimum transparent region size in pixels |

