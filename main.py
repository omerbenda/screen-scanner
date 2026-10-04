import tkinter as tk
import cv2

transparent_mask_color = "#00FF00"

cap = cv2.VideoCapture(0)

root = tk.Tk()
root.title("Screen Scanner")
root.geometry("960x540")

root.config(bg=transparent_mask_color)
root.wm_attributes("-transparentcolor", transparent_mask_color)

root.attributes("-topmost", True)


def _update_frame() -> None:
    root.after(30, _update_frame)

if __name__ == "__main__":
    _update_frame()
    root.mainloop()
    cap.release()
