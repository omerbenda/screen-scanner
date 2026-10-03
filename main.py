import tkinter as tk


transparent_mask_color = "#00FF00"


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Screen Scanner")

    root.geometry("960x540")

    root.config(bg=transparent_mask_color)
    root.wm_attributes("-transparentcolor", transparent_mask_color)

    root.attributes("-topmost", True)

    root.mainloop()
