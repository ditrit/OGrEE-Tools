import tkinter as tk
from tkinter import filedialog

def create_NSR(self):
        cur = os.getcwd()
        os.chdir(cur+"\\OGrEE-Tools\\NonSquareRooms\\setup")
        import setup as s
        os.chdir(cur)
        path = cur+"\\OGrEE-Tools\\.venv\\Scripts\\activate"
        subprocess.call(f"{path}", shell=True)
        os.chdir(cur+"\\OGrEE-Tools\\NonSquareRooms")
        import GenTiles as G
        os.chdir(cur)
        frame = tk.Frame(self.root, width=200, height=100, bg="yellow")
        frame.pack_propagate(False)
        label = tk.Label(frame, text="Frame 1 Content", bg="yellow", fg="white")
        label.pack(fill=tk.BOTH, expand=True)
        return frame
