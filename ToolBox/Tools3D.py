import tkinter as tk
from tkinter import filedialog

def create_3DT(self):
        frame = tk.Frame(self.root, width=200, height=100, bg="green")
        frame.pack_propagate(False)
        label = tk.Label(frame, text="Frame 1 Content", bg="green", fg="white")
        label.pack(fill=tk.BOTH, expand=True)
        return frame