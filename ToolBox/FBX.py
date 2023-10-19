import tkinter as tk
from tkinter import filedialog

def create_FBX(self):
        self.frame = tk.Frame(self.root, width=200, height=100)
        self.frame.pack_propagate(False)

        self.label = tk.Label(self.frame, text="FBX Converter")
        self.label.pack(pady=10)

        front = tk.Frame(self.frame)
        front.pack(fill=tk.X, pady=20)
        front_label = tk.Label(front, text="Choose your front image :", anchor="w")
        front_label.pack(fill=tk.X,side=tk.TOP, pady=20)
        self.front_entry = tk.Entry(front)
        self.front_entry.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)
        front_parcourir = tk.Button(front, text="Parcourir", command=lambda: self.choisir_png(self.front_entry), width=20)
        front_parcourir.pack(side=tk.RIGHT, padx=20)

        back = tk.Frame(self.frame)
        back.pack(fill=tk.X,pady=20)
        back_label = tk.Label(back, text="Choose your back image :", anchor="w")
        back_label.pack(fill=tk.X,side=tk.TOP, pady=20)
        self.back_entry = tk.Entry(back)
        self.back_entry.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)
        back_parcourir = tk.Button(back, text="Parcourir", command=lambda: self.choisir_png(self.back_entry), width=20)
        back_parcourir.pack(side=tk.RIGHT, padx=20)

        dimensions=tk.Frame(self.frame)
        dimensions.pack(side=tk.TOP, fill=tk.X,pady=20)
        size_label=tk.Label(dimensions,text="Choose the dimensions of your component : w ")
        size_label.pack(side=tk.LEFT,pady=10)
        self.w_entry=tk.Entry(dimensions,width=5)
        self.w_entry.insert(0,"12")
        self.w_entry.pack(side=tk.LEFT,pady=10)
        d_label=tk.Label(dimensions,text=" d ")
        d_label.pack(side=tk.LEFT,pady=10)
        self.d_entry=tk.Entry(dimensions,width=5)
        self.d_entry.pack(side=tk.LEFT,pady=10)
        h_label=tk.Label(dimensions,text=" h ")
        h_label.pack(side=tk.LEFT,pady=10)
        self.h_entry=tk.Entry(dimensions,width=5,)
        self.h_entry.pack(side=tk.LEFT,pady=10)

        path=tk.Frame(self.frame)
        path.pack(side=tk.TOP, fill=tk.X)
        enter_button=tk.Button(path, text="Out path", padx=10, width=10, command=lambda: self.choisir_path(self.enter))
        enter_button.pack(pady=10,padx=10 ,side=tk.LEFT)
        self.enter=tk.Entry(path, width=100)
        self.enter.pack(pady=10,padx=10 , fill=tk.X)

        bot2=tk.Frame(self.frame)
        bot2.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=20)
        label_file=tk.Label(bot2,text="Here is you generated FBX file : ")
        label_file.pack(side=tk.TOP, pady=10)
        file=tk.Entry(bot2)
        file.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)

        bot=tk.Frame(self.frame)
        bot.pack(side=tk.BOTTOM, fill=tk.X)
        self.finish_button=tk.Button(bot, text="generate", padx=10, width=20)
        self.finish_button.config(state=tk.DISABLED)
        self.finish_button.pack(pady=10,padx=10)

        return self.frame
