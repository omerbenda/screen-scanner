import ctypes
import sys
import tkinter as tk
from tkinter import messagebox
from typing import Optional
import mss
import numpy as np
import torch
from importlib.metadata import version
from ultralytics import YOLO
import config
from model import load_model

TRANSPARENT_MASK_COLOR = "#00FF00"

DEVICE = 0 if torch.cuda.is_available() else "cpu"
print(f"Running YOLO inference on: {'GPU (CUDA)' if DEVICE == 0 else 'CPU'}")

sct = mss.MSS()


def capture_bgr(root: tk.Tk) -> Optional[np.ndarray]:
    x = root.winfo_rootx()
    y = root.winfo_rooty()
    w = root.winfo_width()
    h = root.winfo_height()

    if w > 1 and h > 1:
        monitor_region = {"top": y, "left": x, "width": w, "height": h}

        try:
            sct_img = sct.grab(monitor_region)
            frame_bgra = np.asarray(sct_img)

            return frame_bgra[:, :, :3]
        except mss.exception.ScreenShotError:
            return None

    return None


def capture_and_detect(root: tk.Tk, canvas: tk.Canvas, model: YOLO):
    root.update_idletasks()
    frame_bgr = capture_bgr(root)

    if frame_bgr is not None:
        results = model(frame_bgr, device=DEVICE, verbose=False)
        relevant_result = results[0]

        canvas.delete("detection")

        boxes = relevant_result.boxes
        names = relevant_result.names

        for box in boxes:
            bx1, by1, bx2, by2 = box.xyxy[0].tolist()
            cls_id = int(box.cls[0].item())
            conf = float(box.conf[0].item())
            label = f"{names[cls_id]} {conf:.2f}"

            canvas.create_rectangle(
                bx1,
                by1,
                bx2,
                by2,
                outline="red",
                width=2,
                tags="detection",
            )

            canvas.create_rectangle(
                bx1,
                max(0, by1 - 18),
                bx1 + (len(label) * 8) + 4,
                by1,
                fill="red",
                outline="red",
                tags="detection",
            )
            canvas.create_text(
                bx1 + 2,
                max(0, by1 - 16),
                anchor="nw",
                text=label,
                fill="white",
                font=("Arial", 9, "bold"),
                tags="detection",
            )

    root.after(config.inference_timeout_ms, lambda: capture_and_detect(root, canvas, model))


def on_close(root: tk.Tk) -> None:
    sct.close()
    root.destroy()


def create_root() -> tk.Tk:
    root = tk.Tk()
    version_str = version("screen-scanner")
    root.title(f"Screen Scanner - {version_str}")
    root.geometry("960x540")

    root.config(bg=TRANSPARENT_MASK_COLOR)
    root.protocol("WM_DELETE_WINDOW", lambda: on_close(root))
    root.attributes("-topmost", True)

    if sys.platform.startswith("win"):
        root.wm_attributes("-transparentcolor", TRANSPARENT_MASK_COLOR)

        try:
            root.update_idletasks()

            child_hwnd = root.winfo_id()
            top_hwnd = ctypes.windll.user32.GetParent(child_hwnd) or child_hwnd

            WDA_EXCLUDEFROMCAPTURE = 0x00000011
            success = ctypes.windll.user32.SetWindowDisplayAffinity(top_hwnd, WDA_EXCLUDEFROMCAPTURE)
            if not success:
                print("Warning: SetWindowDisplayAffinity failed to apply.")
        except Exception as e:
            print(f"Could not set display affinity: {e}")

    return root


if __name__ == "__main__":
    try:
        model: YOLO = load_model()
    except Exception as e:
        temp_root = tk.Tk()
        temp_root.withdraw()
        messagebox.showerror(
            "Model Error",
            f"Could not load model: '{config.model}'\n\n"
            f"Please place your .pt file inside the 'models' folder."
        )
        sys.exit(1)

    root = create_root()

    canvas = tk.Canvas(
        root,
        bg=TRANSPARENT_MASK_COLOR,
        highlightthickness=0,
        bd=0,
    )
    canvas.pack(fill=tk.BOTH, expand=True)

    root.after(100, lambda: capture_and_detect(root, canvas, model))
    root.mainloop()
