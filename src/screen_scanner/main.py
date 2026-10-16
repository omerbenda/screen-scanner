import queue
import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox
import torch
from ultralytics import YOLO
import screen_scanner.config as config
import screen_scanner.model as model
from screen_scanner.capture import ScreenCapture
from screen_scanner.overlay import OverlayWindow

DEVICE = 0 if torch.cuda.is_available() else "cpu"
print(f"Running YOLO inference on: {'GPU (CUDA)' if DEVICE == 0 else 'CPU'}")


def _load_model_or_exit() -> YOLO:
    try:
        return model.load_model()
    except Exception:
        temp_root = tk.Tk()
        temp_root.withdraw()
        messagebox.showerror(
            "Model Error",
            f"Could not load model: '{config.model}'\n\n"
            f"Please place your .pt file inside the 'models' folder."
        )
        sys.exit(1)


class ScreenScannerApp:
    def __init__(self):
        self.model = _load_model_or_exit()
        self.capture = ScreenCapture()
        self.detection_queue = queue.Queue(maxsize=1)
        self.running = True

        self.overlay = OverlayWindow(on_close_callback=self.stop)

    def detection_worker(self):
        while self.running:
            x, y, w, h = self.overlay.get_bounds()
            frame_bgr = self.capture.grab_region(x, y, w, h)

            if frame_bgr is not None:
                with torch.inference_mode():
                    results = self.model(
                        frame_bgr,
                        device=DEVICE,
                        verbose=False,
                        quantize="fp16" if DEVICE == 0 else None,
                    )

                    if self.detection_queue.full():
                        try:
                            self.detection_queue.get_nowait()
                        except queue.Empty:
                            pass

                    self.detection_queue.put(results[0])
            else:
                time.sleep(config.inference_timeout_sec)

    def update_ui(self):
        try:
            result = self.detection_queue.get_nowait()
            self.overlay.draw_detections(result)
        except queue.Empty:
            pass

        self.overlay.schedule(16, self.update_ui)

    def stop(self):
        self.running = False
        self.capture.close()
        self.overlay.destroy()

    def run(self):
        thread = threading.Thread(target=self.detection_worker, daemon=True)
        thread.start()
        self.overlay.schedule(100, self.update_ui)
        self.overlay.mainloop()


if __name__ == "__main__":
    app = ScreenScannerApp()
    app.run()
