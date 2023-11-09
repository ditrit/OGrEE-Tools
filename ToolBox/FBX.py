import tkinter as tk
from tkinter import filedialog

def create_FBX(self):
        self.frame = tk.Frame(self.root, width=200, height=100)
        self.frame.pack_propagate(False)

        label = tk.Label(self.frame, text="FBX Converter")
        label.pack(pady=10)

        front = tk.Frame(self.frame)
        front.pack(fill=tk.X, pady=20)
        front_label = tk.Label(front, text="Choose your front image :", anchor="w")
        front_label.pack(fill=tk.X,side=tk.TOP, pady=20)
        front_entry = tk.Entry(front)
        front_entry.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)
        front_parcourir = tk.Button(front, text="Parcourir", command=lambda: choisir_png(front_entry), width=20)
        front_parcourir.pack(side=tk.RIGHT, padx=20)

        back = tk.Frame(self.frame)
        back.pack(fill=tk.X,pady=20)
        back_label = tk.Label(back, text="Choose your back image :", anchor="w")
        back_label.pack(fill=tk.X,side=tk.TOP, pady=20)
        back_entry = tk.Entry(back)
        back_entry.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)
        back_parcourir = tk.Button(back, text="Parcourir", command=lambda: choisir_png(back_entry), width=20)
        back_parcourir.pack(side=tk.RIGHT, padx=20)

        dimensions=tk.Frame(self.frame)
        dimensions.pack(side=tk.TOP, fill=tk.X,pady=20)
        size_label=tk.Label(dimensions,text="Choose the dimensions of your component : w ")
        size_label.pack(side=tk.LEFT,pady=10)
        w_entry=tk.Entry(dimensions,width=5)
        w_entry.insert(0,"434")
        w_entry.pack(side=tk.LEFT,pady=10)
        d_label=tk.Label(dimensions,text=" d ")
        d_label.pack(side=tk.LEFT,pady=10)
        d_entry=tk.Entry(dimensions,width=5)
        d_entry.insert(0,"755")
        d_entry.pack(side=tk.LEFT,pady=10)
        h_label=tk.Label(dimensions,text=" h ")
        h_label.pack(side=tk.LEFT,pady=10)
        h_entry=tk.Entry(dimensions,width=5,)
        h_entry.insert(0,"87")
        h_entry.pack(side=tk.LEFT,pady=10)
        enter_name=tk.Entry(dimensions,width=50)
        enter_name.pack(side=tk.RIGHT, padx=10)
        label_name=tk.Label(dimensions,text="Choose your FBX file name :")
        label_name.pack(side=tk.RIGHT)

        path=tk.Frame(self.frame)
        path.pack(side=tk.TOP, fill=tk.X)
        enter_button=tk.Button(path, text="Out path", padx=10, width=10, command=lambda: choisir_path(enter_path))
        enter_button.pack(pady=10,padx=10 ,side=tk.LEFT)
        enter_path=tk.Entry(path, width=100)
        enter_path.pack(pady=10,padx=10 , fill=tk.X)

        bot2=tk.Frame(self.frame)
        bot2.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=20)
        label_file=tk.Label(bot2,text="Here is you generated FBX file : ")
        label_file.pack(side=tk.TOP, pady=10)
        file=tk.Entry(bot2)
        file.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)

        bot=tk.Frame(self.frame)
        bot.pack(side=tk.BOTTOM, fill=tk.X)
        finish_button=tk.Button(bot, text="generate", padx=10, width=20, command=lambda: generate_command_FBX())
        finish_button.config(state=tk.DISABLED)
        finish_button.pack(pady=10,padx=10)

        def generate_command_FBX():
                w=w_entry.get()
                d=d_entry.get()
                h=h_entry.get()
                front=front_entry.get()
                back=back_entry.get()
                path=enter_path.get()
                command="python .\FbxBuilder.py --WDH "+w+","+d+","+h+" --front "+front+" --back "+back+" -o "+path
                if enter_name.get()!="":
                        name=enter_name.get()
                        command+=" --name "+name
                self.generate_command(command)

        def choisir_png(entry):
                # Ouvre une boîte de dialogue pour choisir un fichier PNG
                fichier = filedialog.askopenfilename(filetypes=[("Fichiers PNG", "*.png")], initialdir="./OGrEE-Tools/Converter/output/OGrEE/pictures")

                # Affiche le lien du fichier dans l'Entry
                entry.delete(0, tk.END)  # Efface le contenu actuel de l'Entry
                entry.insert(0, fichier)  # Insère le lien du fichier choisi
                update_generate_button()

        def choisir_path(enter):
                file_path = filedialog.askdirectory()
                enter.delete(0, tk.END)  # Efface le contenu actuel de l'Entry
                enter.insert(0, file_path)
                update_generate_button()

        def update_generate_button():
                w=w_entry.get()
                d=d_entry.get()
                h=h_entry.get()
                front=front_entry.get()
                back=back_entry.get()
                out=enter_path.get()
                if (w!="" and d!="" and h!="" and front!="" and back!="" and out!=""):
                        finish_button.config(state=tk.NORMAL)

        return self.frame


        