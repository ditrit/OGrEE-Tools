import tkinter as tk
from tkinter import filedialog

def create_FBX(self):
        frame = tk.Frame(self.root, width=200, height=100, bg="pink")
        frame.pack_propagate(False)

        label = tk.Label(frame, text="FBX Converter", bg="red")
        label.pack(pady=10)

        front = tk.Frame(frame, bg="green")
        front.pack(fill=tk.X)
        front_label = tk.Label(front, text="Choose your front image :", anchor="w")
        front_label.pack(fill=tk.X,side=tk.TOP, pady=20)
        front_entry = tk.Entry(front)
        front_entry.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)
        front_parcourir = tk.Button(front, text="Parcourir", command=lambda: self.choisir_png(front_entry, front_image), bg="red", width=20)
        front_parcourir.pack(side=tk.RIGHT, padx=20)

        back = tk.Frame(frame, bg="green")
        back.pack(fill=tk.X)
        back_label = tk.Label(back, text="Choose your back image :", anchor="w")
        back_label.pack(fill=tk.X,side=tk.TOP, pady=20)
        back_entry = tk.Entry(back)
        back_entry.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)
        back_parcourir = tk.Button(back, text="Parcourir", command=lambda: self.choisir_png(back_entry, back_image), bg="red", width=20)
        back_parcourir.pack(side=tk.RIGHT, padx=20)

        front_image = tk.Label(frame)
        front_image.pack(side=tk.LEFT,pady=10)

        back_image = tk.Label(frame)
        back_image.pack(side=tk.RIGHT, pady=10)

        bot2=tk.Frame(frame, bg="green")
        bot2.pack(side=tk.BOTTOM, fill=tk.X)
        finish_button=tk.Button(bot2, text="finish", padx=10, width=20)
        finish_button.pack(pady=10,padx=10 ,side=tk.RIGHT)
        enter_button=tk.Button(bot2, text="Out path", padx=10, width=10, command=lambda: self.choisir_path(enter))
        enter_button.pack(pady=10,padx=10 ,side=tk.LEFT)
        enter=tk.Entry(bot2, width=100)
        enter.pack(pady=10,padx=10 , fill=tk.X)

        bot1=tk.Frame(frame, bg="blue")
        bot1.pack(side=tk.BOTTOM, fill=tk.X)
        size_label=tk.Label(bot1,text="Choose the dimensions : w ", bg="blue")
        size_label.pack(side=tk.LEFT,pady=10)
        w_entry=tk.Entry(bot1,width=5, bg="blue")
        w_entry.pack(side=tk.LEFT,pady=10)
        d_label=tk.Label(bot1,text=" d ", bg="blue")
        d_label.pack(side=tk.LEFT,pady=10)
        d_entry=tk.Entry(bot1,width=5, bg="blue")
        d_entry.pack(side=tk.LEFT,pady=10)
        h_label=tk.Label(bot1,text=" h ", bg="blue")
        h_label.pack(side=tk.LEFT,pady=10)
        h_entry=tk.Entry(bot1,width=5, bg="blue")
        h_entry.pack(side=tk.LEFT,pady=10)

        return frame