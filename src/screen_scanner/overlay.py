import ctypes
import sys
from importlib.metadata import version
from typing import Callable
import tkinter as tk

TRANSPARENT_MASK_COLOR = "#00FF00"


class OverlayWindow:
    def __init__(self, on_close_callback: Callable[[], None], root: tk.Tk | None = None):
        self.root = root if root is not None else tk.Tk()

        version_str = version("screen-scanner")
        self.root.title(f"Screen Scanner - {version_str}")
        self.root.geometry("960x540")
        self.root.resizable(True, True)

        self.root.config(bg=TRANSPARENT_MASK_COLOR)
        self.root.attributes("-topmost", True)
        self.root.protocol("WM_DELETE_WINDOW", on_close_callback)
        self._configure_transparency()

        self.canvas = tk.Canvas(self.root, bg=TRANSPARENT_MASK_COLOR, highlightthickness=0, bd=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def _configure_transparency(self) -> None:
        if sys.platform.startswith("win"):
            self.root.wm_attributes("-transparentcolor", TRANSPARENT_MASK_COLOR)

            try:
                self.root.update_idletasks()

                child_hwnd = self.root.winfo_id()
                top_hwnd = ctypes.windll.user32.GetParent(child_hwnd) or child_hwnd
                ctypes.windll.user32.SetWindowDisplayAffinity(top_hwnd, 0x00000011)
            except Exception as e:
                print(f"Could not set display affinity: {e}")

    def get_bounds(self) -> tuple[int, int, int, int]:
        try:
            return (
                self.root.winfo_rootx(),
                self.root.winfo_rooty(),
                self.root.winfo_width(),
                self.root.winfo_height(),
            )
        except Exception:
            return 0, 0, 0, 0

    def draw_detections(self, result) -> None:
        self.canvas.delete("detection")

        boxes = result.boxes
        names = result.names

        for box in boxes:
            bx1, by1, bx2, by2 = box.xyxy[0].tolist()
            cls_id = int(box.cls[0].item())
            conf = float(box.conf[0].item())
            label = f"{names[cls_id]} {conf:.2f}"

            self.canvas.create_rectangle(
                bx1,
                by1,
                bx2,
                by2,
                outline="red",
                width=2,
                tags="detection",
            )
            self.canvas.create_rectangle(
                bx1,
                max(0, by1 - 18),
                bx1 + (len(label) * 8) + 4,
                by1,
                fill="red",
                outline="red",
                tags="detection",
            )
            self.canvas.create_text(
                bx1 + 2,
                max(0, by1 - 16),
                anchor="nw",
                text=label,
                fill="white",
                font=("Arial", 9, "bold"),
                tags="detection",
            )

    def schedule(self, delay_ms: int, callback: Callable) -> None:
        self.root.after(delay_ms, callback)

    def mainloop(self) -> None:
        self.root.mainloop()

    def destroy(self) -> None:
        self.root.destroy()
