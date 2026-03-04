# Device Frames Media
**The Open Source Standard Library for Device Templates** - [Website](https://device-frames-web.vercel.app/frame-media)

For each device, there is a:
 - PNG of the device frame 
 - PNG of the mask of the frame (grayscale binary screen mask)
 - JSON file with metadata  

**Example of Frame, Template, and Mask**
![iPhone 17 Pro Max Cosmic Orange Frame, Template, and Mask PNGs](docs/frame-template-and-mask-examples.png)

This data is stored within [`device-frames-output`](device-frames-output), which has this structure:
```
device-frames-output/
├── {category}/         
│   └── {model}/
│       └── {variant}/            
│           ├── frame.png         
│           ├── mask.png
│           └── template.json  
├── index.json 
```
where **category** is either `Apple iPhone, Android Phone, Android Tablet, Apple iPad`,   
**model** is the type of device `(ex: 17 Pro Max, iPad mini 8.3, Pixel 9 Pro XL)`, and  
**variant** is the different colors `(ex: Cosmic Orange, Blue, Titanium)`,  
and [`index.json`](https://raw.githubusercontent.com/jonnyjackson26/device-frames-media/main/device-frames-output/index.json) is a JSON file which contains all frames in a nested lookup structure, each variant in kebab-case with hosted URLs and template metadata:
  ```json
  {
    "apple-iphone": {
      "17-pro-max": {
        "cosmic-orange": {
          "frame": "https://jonnyjackson26.github.io/device-frames-media/device-frames-output/Apple%20iPhone/17%20Pro%20Max/Cosmic%20Orange/frame.png",
          "mask": "https://jonnyjackson26.github.io/device-frames-media/device-frames-output/Apple%20iPhone/17%20Pro%20Max/Cosmic%20Orange/mask.png",
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

This data is created from raw PNGs of device frames (`device-frames-raw`) with the script `process_frames.py`.  [Algorithm docs](docs/PROCESS_FRAMES_ALGORITHM.md)
![Frame process to seperate Mask and Frame](docs/process-frames-graphic.png)  


# Contributing
Please add more device frames to expand the dataset. See [CONTRIBUTING.md](CONTRIBUTING.md).
1. Add the frame PNG to the appropriate spot in device-frames-raw
2. Push your branch (or open a PR) and GitHub Actions will automatically run `process_frames.py` and regenerate the device list below

# List of Devices and Variations
**Apple iPhone:**

 - 8
   - [Gold](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/8/Gold), [Silver](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/8/Silver), [Space Grey](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/8/Space%20Grey)
 - 8 copy
   - [Gold](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/8%20copy/Gold), [Silver](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/8%20copy/Silver), [Space Grey](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/8%20copy/Space%20Grey)
 - 13 mini
   - [Black](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/13%20mini/Black), [Blue](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/13%20mini/Blue), [Pink](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/13%20mini/Pink), [Product (RED)](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/13%20mini/Product%20%28RED%29), [Starlight](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/13%20mini/Starlight)
 - 14 Pro Max
   - [Deep Purple](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/14%20Pro%20Max/Deep%20Purple), [Deep Purple - Shadow](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/14%20Pro%20Max/Deep%20Purple%20-%20Shadow), [Gold](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/14%20Pro%20Max/Gold), [Gold - Shadow](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/14%20Pro%20Max/Gold%20-%20Shadow), [Silver](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/14%20Pro%20Max/Silver), [Silver - Shadow](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/14%20Pro%20Max/Silver%20-%20Shadow), [Space Black](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/14%20Pro%20Max/Space%20Black), [Space Black - Shadow](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/14%20Pro%20Max/Space%20Black%20-%20Shadow)
 - 15 Pro Max
   - [Black Titanium](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/15%20Pro%20Max/Black%20Titanium), [Blue Titanium](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/15%20Pro%20Max/Blue%20Titanium), [Natural Titanium](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/15%20Pro%20Max/Natural%20Titanium), [White Titanium](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/15%20Pro%20Max/White%20Titanium)
 - 16
   - [Black](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/16/Black), [Pink](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/16/Pink), [Teal](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/16/Teal), [Ultramarine](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/16/Ultramarine), [White](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/16/White)
 - 16 Plus
   - [Black](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/16%20Plus/Black), [Pink](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/16%20Plus/Pink), [Teal](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/16%20Plus/Teal), [Ultramarine](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/16%20Plus/Ultramarine), [White](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/16%20Plus/White)
 - 16 Pro
   - [Black Titanium](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/16%20Pro/Black%20Titanium), [Desert Titanium](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/16%20Pro/Desert%20Titanium), [Natural Titanium](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/16%20Pro/Natural%20Titanium), [White Titanium](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/16%20Pro/White%20Titanium)
 - 16 Pro Max
   - [Black Titanium](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/16%20Pro%20Max/Black%20Titanium), [Desert Titanium](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/16%20Pro%20Max/Desert%20Titanium), [Natural Titanium](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/16%20Pro%20Max/Natural%20Titanium), [White Titanium](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/16%20Pro%20Max/White%20Titanium)
 - 17 Pro
   - [Cosmic Orange](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/17%20Pro/Cosmic%20Orange), [Deep Blue](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/17%20Pro/Deep%20Blue), [Silver](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/17%20Pro/Silver)
 - 17 Pro Max
   - [Cosmic Orange](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/17%20Pro%20Max/Cosmic%20Orange), [Deep Blue](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/17%20Pro%20Max/Deep%20Blue), [Silver](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/17%20Pro%20Max/Silver)
 - Air
   - [Cloud White](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/Air/Cloud%20White), [Light Gold](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/Air/Light%20Gold), [Sky Blue](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/Air/Sky%20Blue), [Space Black](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/Air/Space%20Black)
 - DELEET ME
   - [Gold](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/DELEET%20ME/Gold), [Silver](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/DELEET%20ME/Silver), [Space Grey](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPhone/DELEET%20ME/Space%20Grey)

**Apple iPad:**

 - iPad Air 11 M2 & M3
   - [Blue](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Air%2011%20M2%20%26%20M3/Blue), [Blue2](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Air%2011%20M2%20%26%20M3/Blue2), [Lavender](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Air%2011%20M2%20%26%20M3/Lavender), [Lavender2](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Air%2011%20M2%20%26%20M3/Lavender2), [Space Gray](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Air%2011%20M2%20%26%20M3/Space%20Gray), [Space Gray2](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Air%2011%20M2%20%26%20M3/Space%20Gray2), [Stardust](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Air%2011%20M2%20%26%20M3/Stardust), [Stardust2](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Air%2011%20M2%20%26%20M3/Stardust2)
 - iPad Air 13 M2 & M3
   - [Blue](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Air%2013%20M2%20%26%20M3/Blue), [Blue2](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Air%2013%20M2%20%26%20M3/Blue2), [Lavender](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Air%2013%20M2%20%26%20M3/Lavender), [Lavender2](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Air%2013%20M2%20%26%20M3/Lavender2), [Space Gray](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Air%2013%20M2%20%26%20M3/Space%20Gray), [Space Gray2](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Air%2013%20M2%20%26%20M3/Space%20Gray2), [Stardust](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Air%2013%20M2%20%26%20M3/Stardust), [Stardust2](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Air%2013%20M2%20%26%20M3/Stardust2)
 - iPad Air - 10.9 M1
   - [Blue](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Air%20-%2010.9%20M1/Blue), [Blue 2](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Air%20-%2010.9%20M1/Blue%202), [Green](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Air%20-%2010.9%20M1/Green), [Green 2](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Air%20-%2010.9%20M1/Green%202), [Rose Gold](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Air%20-%2010.9%20M1/Rose%20Gold), [Rose Gold 2](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Air%20-%2010.9%20M1/Rose%20Gold%202), [Silver](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Air%20-%2010.9%20M1/Silver), [Silver 2](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Air%20-%2010.9%20M1/Silver%202), [Space Grey](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Air%20-%2010.9%20M1/Space%20Grey), [Space Grey 2](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Air%20-%2010.9%20M1/Space%20Grey%202)
 - iPad mini 8.3 A17 Pro
   - [Starlight](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20mini%208.3%20A17%20Pro/Starlight), [Starlight2](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20mini%208.3%20A17%20Pro/Starlight2)
 - iPad Pro 11 A12X to M2
   - [Landscape - Silver](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Pro%2011%20A12X%20to%20M2/Landscape%20-%20Silver), [Landscape - Silver - Pencil](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Pro%2011%20A12X%20to%20M2/Landscape%20-%20Silver%20-%20Pencil), [Landscape - Space Grey](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Pro%2011%20A12X%20to%20M2/Landscape%20-%20Space%20Grey), [Landscape - Space Grey - Pencil](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Pro%2011%20A12X%20to%20M2/Landscape%20-%20Space%20Grey%20-%20Pencil), [Portrait - Silver](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Pro%2011%20A12X%20to%20M2/Portrait%20-%20Silver), [Portrait - Silver - Pencil](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Pro%2011%20A12X%20to%20M2/Portrait%20-%20Silver%20-%20Pencil), [Portrait - Space Grey](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Pro%2011%20A12X%20to%20M2/Portrait%20-%20Space%20Grey), [Portrait - Space Grey - Pencil](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Pro%2011%20A12X%20to%20M2/Portrait%20-%20Space%20Grey%20-%20Pencil)
 - iPad Pro 11 M4 & M5
   - [Landscape - Silver](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Pro%2011%20M4%20%26%20M5/Landscape%20-%20Silver), [Landscape - Space Black](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Pro%2011%20M4%20%26%20M5/Landscape%20-%20Space%20Black), [Portrait - Silver](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Pro%2011%20M4%20%26%20M5/Portrait%20-%20Silver), [Portrait - Space Black](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Pro%2011%20M4%20%26%20M5/Portrait%20-%20Space%20Black)
 - iPad Pro 13 A12X to M2
   - [Landscape - Silver](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Pro%2013%20A12X%20to%20M2/Landscape%20-%20Silver), [Landscape - Silver - Pencil](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Pro%2013%20A12X%20to%20M2/Landscape%20-%20Silver%20-%20Pencil), [Landscape - Space Grey](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Pro%2013%20A12X%20to%20M2/Landscape%20-%20Space%20Grey), [Landscape - Space Grey - Pencil](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Pro%2013%20A12X%20to%20M2/Landscape%20-%20Space%20Grey%20-%20Pencil), [Portrait - Silver](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Pro%2013%20A12X%20to%20M2/Portrait%20-%20Silver), [Portrait - Silver - Pencil](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Pro%2013%20A12X%20to%20M2/Portrait%20-%20Silver%20-%20Pencil), [Portrait - Space Grey](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Pro%2013%20A12X%20to%20M2/Portrait%20-%20Space%20Grey), [Portrait - Space Grey - Pencil](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Pro%2013%20A12X%20to%20M2/Portrait%20-%20Space%20Grey%20-%20Pencil)
 - iPad Pro 13 M4 & M5
   - [Landscape - Silver](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Pro%2013%20M4%20%26%20M5/Landscape%20-%20Silver), [Landscape - Space Black](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Pro%2013%20M4%20%26%20M5/Landscape%20-%20Space%20Black), [Portrait - Silver](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Pro%2013%20M4%20%26%20M5/Portrait%20-%20Silver), [Portrait - Space Black](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Apple%20iPad/iPad%20Pro%2013%20M4%20%26%20M5/Portrait%20-%20Space%20Black)

**Android Phone:**

 - Pixel 8
   - [Hazel](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Android%20Phone/Pixel%208/Hazel)
 - Pixel 8 Pro
   - [Black](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Android%20Phone/Pixel%208%20Pro/Black), [Blue](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Android%20Phone/Pixel%208%20Pro/Blue), [Silver](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Android%20Phone/Pixel%208%20Pro/Silver)
 - Pixel 9 Pro
   - [Hazel](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Android%20Phone/Pixel%209%20Pro/Hazel), [Obsidian](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Android%20Phone/Pixel%209%20Pro/Obsidian), [Rose Quartz](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Android%20Phone/Pixel%209%20Pro/Rose%20Quartz)
 - Pixel 9 Pro XL
   - [Hazel](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Android%20Phone/Pixel%209%20Pro%20XL/Hazel), [Obsidian](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Android%20Phone/Pixel%209%20Pro%20XL/Obsidian), [Rose Quartz](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Android%20Phone/Pixel%209%20Pro%20XL/Rose%20Quartz)
 - Pixel 100
   - [Hazel](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Android%20Phone/Pixel%20100/Hazel), [Obsidian](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Android%20Phone/Pixel%20100/Obsidian), [Rose Quartz](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Android%20Phone/Pixel%20100/Rose%20Quartz)
 - Pixel 1000
   - [Hazel](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Android%20Phone/Pixel%201000/Hazel), [Obsidian](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Android%20Phone/Pixel%201000/Obsidian), [Rose Quartz](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Android%20Phone/Pixel%201000/Rose%20Quartz)
 - Pixel 1000 copy
   - [Hazel](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Android%20Phone/Pixel%201000%20copy/Hazel), [Obsidian](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Android%20Phone/Pixel%201000%20copy/Obsidian), [Rose Quartz](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Android%20Phone/Pixel%201000%20copy/Rose%20Quartz)
 - Samsung Galaxy S21
   - [Black](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Android%20Phone/Samsung%20Galaxy%20S21/Black), [Pink](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Android%20Phone/Samsung%20Galaxy%20S21/Pink), [Violet](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Android%20Phone/Samsung%20Galaxy%20S21/Violet), [White](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Android%20Phone/Samsung%20Galaxy%20S21/White)

**Android Tablet:**

 - Pixel Tablet
   - [Hazel](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Android%20Tablet/Pixel%20Tablet/Hazel), [Porcelain](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Android%20Tablet/Pixel%20Tablet/Porcelain)
 - Samsung Galaxy Tab S11 Ultra
   - [Samsung Galaxy Tab S11 Ultra](https://github.com/jonnyjackson26/device-frames-media/tree/main/device-frames-output/Android%20Tablet/Samsung%20Galaxy%20Tab%20S11%20Ultra/Samsung%20Galaxy%20Tab%20S11%20Ultra)
