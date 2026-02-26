from dataclasses import dataclass
from typing import Dict


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
            "height": int(self.height),
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
            "frameSize": self.frameSize,
        }
