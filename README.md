# Device Frames Media
This repository contains data for common Apple/Android device frames.
For each device, it contains a
 - PNG of the device frame
 - PNG of the mask of the frame
 - JSON file with metadata  

**Example of Frame, Template, and Mask**
![iPhone 17 Pro Max Cosmic Orange Frame, Template, and Mask PNGs](docs/frame-template-and-mask-examples.png)

This data is stored within `device-frames-output`, which has this structure:
```
device-frames-output/
├── {device-type}/                (android-phone, android-tablet, iOS, or iPad)
│   └── {device-model}/           (ex: 17 Pro Max, iPad mini 8.3, Pixel 9 Pro XL)
│       └── {variant}/            (ex: Cosmic Orange, Blue, Titanium)
│           ├── frame.png         (original frame, RGBA, transparent background)
│           ├── mask.png          (binary screen mask, grayscale)
│           └── template.json     (metadata: coordinates, sizes)
```


**Example template.json**
```json
{
  "frame": "frame.png",            (RGBA frame image)
  "mask": "mask.png",              (binary screen mask: white=screen, black=everything else, such as background or notches)
  "screen": {
    "x": 183,                      (screen top-left x)
    "y": 169,                      (screen top-left y)
    "width": 1145,                 (screen width)
    "height": 2549                 (screen height)
  },
  "frameSize": {
    "width": 1511,                 (full frame width)
    "height": 2896                 (full frame height)
  }
}
```

  [**Generated index.json**](https://raw.githubusercontent.com/jonnyjackson26/device-frames-media/main/device-frames-output/index.json)

  Running `process_frames.py` also creates `device-frames-output/index.json`, which contains all frames in a nested lookup structure:

  - `{device-type}` key in kebab-case (example: `ios`, `android-phone`)
  - `{device-model}` key in kebab-case (example: `17-pro-max`)
  - `{variant}` key in kebab-case (example: `cosmic-orange`)

  Each variant includes hosted URLs and template metadata:

  ```json
  {
    "ios": {
      "17-pro-max": {
        "cosmic-orange": {
          "frame": "https://jonnyjackson26.github.io/device-frames-media/device-frames-output/iOS/17%20Pro%20Max/Cosmic%20Orange/frame.png",
          "mask": "https://jonnyjackson26.github.io/device-frames-media/device-frames-output/iOS/17%20Pro%20Max/Cosmic%20Orange/mask.png",
          "screen": {
            "x": 100,
            "y": 100,
            "width": 1320,
            "height": 2868
          },
          "frameSize": {
            "width": 1520,
            "height": 3068
          }
        }
      }
    }
  }
  ```

This data is created from raw PNGs of device frames (`device-frames-raw`) with the script `process_frames.py`.  
![Frame process to seperate Mask and Frame](docs/process-frames-graphic.png)  

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


# Installation
```
pip install -r requirements.txt
python process_frames.py
```

By default, `process_frames.py` is incremental: it only processes PNGs that are new or changed since their generated outputs were last written.

To fully regenerate all outputs, delete `device-frames-output` and run `python process_frames.py` again.

# Contributing
Please add more device frames to expand the dataset.
1. Add the frame PNG to the appropriate spot in device-frames-raw
2. Push your branch (or open a PR) and GitHub Actions will automatically run `process_frames.py` and regenerate the device list below

# TODO:
=========================================================================
can we make the commit message detail what new frames were added?
Consider removing generated template.json files, i think they're useless

# List of Devices and Variations
**iOS:**

 - 8
   - Gold, Silver, Space Grey
 - 13 mini
   - Black, Blue, Pink, Product (RED), Starlight
 - 14 Pro Max
   - Deep Purple, Deep Purple - Shadow, Gold, Gold - Shadow, Silver, Silver - Shadow, Space Black, Space Black - Shadow
 - 15 Pro Max
   - Black Titanium, Blue Titanium, Natural Titanium, White Titanium
 - 16
   - Black, Pink, Teal, Ultramarine, White
 - 16 Plus
   - Black, Pink, Teal, Ultramarine, White
 - 16 Pro
   - Black Titanium, Desert Titanium, Natural Titanium, White Titanium
 - 16 Pro Max
   - Black Titanium, Desert Titanium, Natural Titanium, White Titanium
 - 17 Pro
   - Cosmic Orange, Deep Blue, Silver
 - 17 Pro Max
   - Cosmic Orange, Deep Blue, Silver
 - Air
   - Cloud White, Light Gold, Sky Blue, Space Black

**iPad:**

 - iPad Air 11 M2 & M3
   - Blue, Blue2, Lavender, Lavender2, Space Gray, Space Gray2, Stardust, Stardust2
 - iPad Air 13 M2 & M3
   - Blue, Blue2, Lavender, Lavender2, Space Gray, Space Gray2, Stardust, Stardust2
 - iPad Air - 10.9 M1
   - Blue, Blue 2, Green, Green 2, Rose Gold, Rose Gold 2, Silver, Silver 2, Space Grey, Space Grey 2
 - iPad mini 8.3 A17 Pro
   - Starlight, Starlight2
 - iPad Pro 11 A12X to M2
   - iPad Pro 11 A12X to M2 - Landscape - Silver, iPad Pro 11 A12X to M2 - Landscape - Silver - Pencil, iPad Pro 11 A12X to M2 - Landscape - Space Grey, iPad Pro 11 A12X to M2 - Landscape - Space Grey - Pencil, iPad Pro 11 A12X to M2 - Portrait - Silver, iPad Pro 11 A12X to M2 - Portrait - Silver - Pencil, iPad Pro 11 A12X to M2 - Portrait - Space Grey, iPad Pro 11 A12X to M2 - Portrait - Space Grey - Pencil
 - iPad Pro 11 M4 & M5
   - iPad Pro 11 M4 & M5 - Landscape - Silver, iPad Pro 11 M4 & M5 - Landscape - Space Black, iPad Pro 11 M4 & M5 - Portrait - Silver, iPad Pro 11 M4 & M5 - Portrait - Space Black
 - iPad Pro 13 A12X to M2
   - iPad Pro 13 A12X to M2 - Landscape - Silver, iPad Pro 13 A12X to M2 - Landscape - Silver - Pencil, iPad Pro 13 A12X to M2 - Landscape - Space Grey, iPad Pro 13 A12X to M2 - Landscape - Space Grey - Pencil, iPad Pro 13 A12X to M2 - Portrait - Silver, iPad Pro 13 A12X to M2 - Portrait - Silver - Pencil, iPad Pro 13 A12X to M2 - Portrait - Space Grey, iPad Pro 13 A12X to M2 - Portrait - Space Grey - Pencil
 - iPad Pro 13 M4 & M5
   - iPad Pro 13 M4 & M5 - Landscape - Silver, iPad Pro 13 M4 & M5 - Landscape - Space Black, iPad Pro 13 M4 & M5 - Portrait - Silver, iPad Pro 13 M4 & M5 - Portrait - Space Black

**Android Phones:**

 - Pixel 8
   - Hazel
 - Pixel 8 Pro
   - Black, Blue, Silver
 - Pixel 9 Pro
   - Hazel, Obsidian, Rose Quartz
 - Pixel 9 Pro XL
   - Hazel, Obsidian, Rose Quartz
 - Samsung Galaxy S21
   - Black, Pink, Violet, White

**Android Tablets:**

 - Fake Pixel Tablet
   - Hazel
 - Pixel Tablet
   - Hazel, Porcelain
 - Samsung Galaxy Tab S11 Ultra
   - Samsung Galaxy Tab S11 Ultra
