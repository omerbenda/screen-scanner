import ctypes
import queue
import sys
import threading
import time
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

detection_queue: queue.Queue = queue.Queue(maxsize=1)
running = True


def capture_bgr(root: tk.Tk) -> Optional[np.ndarray]:
    try:
        x = root.winfo_rootx()
        y = root.winfo_rooty()
        w = root.winfo_width()
        h = root.winfo_height()

        if w > 1 and h > 1:
            monitor_region = {"top": y, "left": x, "width": w, "height": h}

            sct_img = sct.grab(monitor_region)
            frame_bgra = np.asarray(sct_img)

            return frame_bgra[:, :, :3]
    except Exception:
        return None

    return None


def add_detection(root: tk.Tk, model: YOLO) -> None:
    while running:
        frame_bgr = capture_bgr(root)

        if frame_bgr is not None:
            with torch.inference_mode():
                results = model(frame_bgr, device=DEVICE, verbose=False, quantize="fp16" if DEVICE == 0 else None)

                if detection_queue.full():
                    try:
                        detection_queue.get_nowait()
                    except queue.Empty:
                        pass
                detection_queue.put(results[0])
        else:
            time.sleep(config.inference_timeout_ms)


def update_ui(root: tk.Tk, canvas: tk.Canvas) -> None:
    try:
        relevant_result = detection_queue.get_nowait()

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
    except queue.Empty:
        pass

    root.after(16, lambda: update_ui(root, canvas))


def on_close(root: tk.Tk) -> None:
    global running

    running = False
    sct.close()
    root.destroy()


def create_root() -> tk.Tk:
    try:
        # DPI awareness, must be called before window is created
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

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

    worker_thread = threading.Thread(
        target=add_detection,
        args=(root, model),
        daemon=True,
    )
    worker_thread.start()

    root.after(100, lambda: update_ui(root, canvas))
    root.mainloop()
