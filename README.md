
# Processing frames
![Frame process to seperate Mask and Frame](docs/process_frames_graphic.png)  
Each frame is originally a png, stored in `/device-frames-raw`. In order to put a screenshot within the frame though, we need a mask. `process_frames.py` creates masks and a template.json with important information for each frame, and stores them within `/device-frames-output`.

**Algorithm Overview**

#### Step 1: Normalize Image
- Load PNG and convert to RGBA
- Extract alpha channel (0-255 range)

#### Step 2: Classify Pixels by Opacity
- **Transparent** (α ≤ 10): Screen interior
- **Solid** (α ≥ 245): Device frame
- **Edge/anti-aliased**: Everything in between

#### Step 3: Find Contiguous Transparent Regions
- Connected-component labeling on transparency mask
- Identify all transparent regions with their areas
- Reject regions touching image borders (background)
- Reject tiny regions (holes, speaker grills, < 5000 pixels)

#### Step 4: Select Screen Candidate
Chooses the region with:
- Largest area
- Aspect ratio within 1.3-2.5 range (phones & tablets)
- Fully enclosed by opaque pixels

#### Step 5-6: Extract Bounds & Contour
- Calculate minX, minY, maxX, maxY of selected region
- Generate bounding box
- Extract precise screen contour using edge detection

#### Step 7: Generate Screen Mask
- Create blank image (frame size)
- Fill detected contour with white (255)
- Fill background with black (0)
- Feather inward by ~1px to avoid edge bleed


### Output structure:

Each processed frame generates 3 files in `device-frames-output/`:

```
device-frames-output/
├── {device-type}/
│   └── {device-model}/
│       └── {color-variant}/
│           ├── frame.png         (original frame, RGBA, transparent background)
│           ├── mask.png          (binary screen mask, grayscale)
│           └── template.json     (metadata: coordinates, sizes)
```

### Output Format

**template.json** - Metadata for each device frame:  
```json
{
  "frame": "frame.png",
  "mask": "mask.png",
  "screen": {
    "x": 183,
    "y": 169,
    "width": 1145,
    "height": 2549
  },
  "frameSize": {
    "width": 1511,
    "height": 2896
  }
}
```

**Fields:**
- `frame`: Relative path to RGBA frame image
- `mask`: Relative path to binary screen mask (white=screen, black=background)
- `screen.x, y`: Top-left corner of screen bounding box
- `screen.width, height`: Screen dimensions
- `frameSize`: Full frame dimensions

#### `frame.png`
Original device frame (copy) with transparent background

#### `mask.png`
Binary mask where:
- **White (255)**: Screen region
- **Black (0)**: Everything else



---