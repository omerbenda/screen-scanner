from typing import Optional
import mss
import numpy as np


class ScreenCapture:
    def __init__(self):
        self._sct = mss.MSS()

    def grab_region(self, x: int, y: int, width: int, height: int) -> Optional[np.ndarray]:
        if width <= 1 or height <= 1:
            return None

        try:
            region = {"top": y, "left": x, "width": width, "height": height}
            sct_img = self._sct.grab(region)
            bgr_img = np.asarray(sct_img)

            return bgr_img[:, :, :3]
        except mss.exception.ScreenShotError:
            return None

    def capture(self, x: int, y: int, width: int, height: int) -> Optional[np.ndarray]:
        if width <= 1 or height <= 1:
            return None

        try:
            monitor_region = {"top": y, "left": x, "width": width, "height": height}

            sct_img = self._sct.grab(monitor_region)
            frame_bgra = np.asarray(sct_img)

            return frame_bgra[:, :, :3]
        except mss.exception.ScreenShotError:
            return None

    def close(self):
        self._sct.close()
