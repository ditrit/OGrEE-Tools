import tkinter as tk
from tkinter import filedialog

def create_FBX(self):
        frame = tk.Frame(self.root, width=200, height=100)
        frame.pack_propagate(False)

        label = tk.Label(frame, text="FBX Converter")
        label.pack(pady=10)

        front = tk.Frame(frame)
        front.pack(fill=tk.X)
        front_label = tk.Label(front, text="Choose your front image :", anchor="w")
        front_label.pack(fill=tk.X,side=tk.TOP, pady=20)
        front_entry = tk.Entry(front)
        front_entry.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)
        front_parcourir = tk.Button(front, text="Parcourir", command=lambda: self.choisir_png(front_entry), width=20)
        front_parcourir.pack(side=tk.RIGHT, padx=20)

        back = tk.Frame(frame)
        back.pack(fill=tk.X)
        back_label = tk.Label(back, text="Choose your back image :", anchor="w")
        back_label.pack(fill=tk.X,side=tk.TOP, pady=20)
        back_entry = tk.Entry(back)
        back_entry.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)
        back_parcourir = tk.Button(back, text="Parcourir", command=lambda: self.choisir_png(back_entry), width=20)
        back_parcourir.pack(side=tk.RIGHT, padx=20)

        dimensions=tk.Frame(frame)
        dimensions.pack(side=tk.TOP, fill=tk.X)
        size_label=tk.Label(dimensions,text="Choose the dimensions : w ")
        size_label.pack(side=tk.LEFT,pady=10)
        w_entry=tk.Entry(dimensions,width=5)
        w_entry.pack(side=tk.LEFT,pady=10)
        d_label=tk.Label(dimensions,text=" d ")
        d_label.pack(side=tk.LEFT,pady=10)
        d_entry=tk.Entry(dimensions,width=5)
        d_entry.pack(side=tk.LEFT,pady=10)
        h_label=tk.Label(dimensions,text=" h ")
        h_label.pack(side=tk.LEFT,pady=10)
        h_entry=tk.Entry(dimensions,width=5,)
        h_entry.pack(side=tk.LEFT,pady=10)

        path=tk.Frame(frame)
        path.pack(side=tk.TOP, fill=tk.X)
        enter_button=tk.Button(path, text="Out path", padx=10, width=10, command=lambda: self.choisir_path(enter))
        enter_button.pack(pady=10,padx=10 ,side=tk.LEFT)
        enter=tk.Entry(path, width=100)
        enter.pack(pady=10,padx=10 , fill=tk.X)

        bot2=tk.Frame(frame)
        bot2.pack(side=tk.BOTTOM, fill=tk.X)
        label_file=tk.Label(bot2,text="Here is you generated FBX file : ")
        label_file.pack(side=tk.TOP)
        file=tk.Entry(bot2)
        file.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)

        bot=tk.Frame(frame)
        bot.pack(side=tk.BOTTOM, fill=tk.X)
        finish_button=tk.Button(bot, text="generate", padx=10, width=20)
        finish_button.pack(pady=10,padx=10)

        return frame