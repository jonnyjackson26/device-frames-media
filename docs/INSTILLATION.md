
# Installation
```
pip install -r requirements.txt
python process_frames.py
```

By default, `process_frames.py` is incremental: it only processes PNGs that are new or changed since their generated outputs were last written, and it prunes generated outputs for raw PNGs that were removed or renamed.

To fully regenerate all outputs, delete `device-frames-output` and run `python process_frames.py` again.