import queue
import sys
import threading
import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk
from typing import Callable
from ultralytics import YOLO


@dataclass(frozen=True)
class Success:
    payload: YOLO


@dataclass(frozen=True)
class Failure:
    error: Exception


LoadingResult = Success | Failure


class LoadingScreen:
    def __init__(self, root: tk.Tk, model_name: str):
        self.root = root
        self.model_name = model_name
        self.result: LoadingResult | None = None

        self.root.title("Screen Scanner - Loading Model")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        win_w, win_h = 420, 140
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        pos_x = max(0, (screen_w - win_w) // 2)
        pos_y = max(0, (screen_h - win_h) // 2)
        self.root.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")

        self.frame = ttk.Frame(self.root, padding=(20, 18))
        self.frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            self.frame,
            text=f"Fetching model '{model_name}'...",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w")

        ttk.Label(
            self.frame,
            text="Downloading model from the internet, please wait...",
            font=("Segoe UI", 8),
            foreground="#555555",
        ).pack(anchor="w", pady=(2, 12))

        self.progressbar = ttk.Progressbar(self.frame, mode="indeterminate")
        self.progressbar.pack(fill=tk.X)
        self.progressbar.start(10)

    def _on_close(self) -> None:
        self.progressbar.stop()
        self.root.destroy()
        sys.exit(0)

    def load(self, load_fn: Callable[[], YOLO]) -> YOLO:
        result_queue = queue.Queue[LoadingResult]()

        def worker() -> None:
            try:
                load_result: YOLO = load_fn()
                result_queue.put(Success(payload=load_result))
            except Exception as e:
                result_queue.put(Failure(error=e))

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

        def check_queue() -> None:
            try:
                self.result = result_queue.get_nowait()
                self.progressbar.stop()
                self.frame.destroy()

                self.root.quit()
                return
            except queue.Empty:
                self.root.after(50, check_queue)

        self.root.after(50, check_queue)
        self.root.mainloop()

        thread.join(timeout=1.0)

        if isinstance(self.result, Failure):
            raise self.result.error

        if isinstance(self.result, Success):
            return self.result.payload

        raise RuntimeError("Loading window closed without a result.")
