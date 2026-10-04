import sys
import tkinter as tk
import numpy as np
from PIL import ImageGrab
from ultralytics import YOLO
import torch

TRANSPARENT_MASK_COLOR = "#00FF00"

DEVICE = 0 if torch.cuda.is_available() else "cpu"
print(f"Running YOLO inference on: {'GPU (CUDA)' if DEVICE == 0 else 'CPU'}")

model = YOLO("models/yolo26x.pt")


def capture_and_detect(root: tk.Tk, canvas: tk.Canvas):
    root.update_idletasks()

    x1 = root.winfo_rootx()
    y1 = root.winfo_rooty()
    w = root.winfo_width()
    h = root.winfo_height()
    x2 = x1 + w
    y2 = y1 + h

    if w > 0 and h > 0:
        screen_img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        frame_rgb = np.array(screen_img)

        results = model(frame_rgb, device=DEVICE, verbose=False)

        canvas.delete("detection")

        boxes = results[0].boxes
        names = results[0].names

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

    root.after(33, lambda: capture_and_detect(root, canvas))


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Screen Scanner")
    root.geometry("960x540")

    root.config(bg=TRANSPARENT_MASK_COLOR)
    if sys.platform.startswith("win"):
        root.wm_attributes("-transparentcolor", TRANSPARENT_MASK_COLOR)
    root.attributes("-topmost", True)

    canvas = tk.Canvas(
        root,
        bg=TRANSPARENT_MASK_COLOR,
        highlightthickness=0,
        bd=0,
    )
    canvas.pack(fill=tk.BOTH, expand=True)

    root.after(100, lambda: capture_and_detect(root, canvas))
    root.mainloop()
