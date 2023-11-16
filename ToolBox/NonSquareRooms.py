import tkinter as tk
from tkinter import filedialog
import subprocess
import os
import venv

def create_NSR(self):
        curDir = os.path.dirname(__file__)
        rootDir = f"{curDir}\\.."
        setupDir = f"{rootDir}\\NonSquareRooms\\setup"
        envDir = f"{rootDir}\\.venv\\Scripts"
        #pythonExe = f"{envDir}\\python.exe"
        #pythonExe = "C:\\Users\\Pako JUSTIN\\AppData\\Roaming\\Local\\Programs\\Python\\python.exe"
        pythonExe = os.environ['APPDATA']+"\\..\\Local\\Programs\\Python\\python.exe"
        subprocess.run([pythonExe, 'setup.py'])
        os.chdir(rootDir)
        subprocess.run([f"{envDir}\\./activate"], shell=True)
        os.chdir(f"{rootDir}\\NonSquareRooms")

        self.frame = tk.Frame(self.root, width=200, height=100)
        self.frame.pack_propagate(False)

        label = tk.Label(self.frame, text="NonSquareRoome")
        label.pack(pady=10)

        json = tk.Frame(self.frame)
        json.pack(fill=tk.X, pady=20)
        json_label = tk.Label(json, text="Choose your json file :", anchor="w")
        json_label.pack(fill=tk.X,side=tk.TOP, pady=20)
        json_entry = tk.Entry(json)
        json_entry.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)
        front_parcourir = tk.Button(json, text="Parcourir", command=lambda: choisir_json(json_entry), width=20)
        front_parcourir.pack(side=tk.RIGHT, padx=20)

        path=tk.Frame(self.frame)
        path.pack(side=tk.TOP, fill=tk.X)
        enter_button=tk.Button(path, text="Out path", padx=10, width=10, command=lambda: choisir_path(enter_path))
        enter_button.pack(pady=10,padx=10 ,side=tk.LEFT)
        enter_path=tk.Entry(path, width=100)
        enter_path.pack(pady=10,padx=10 , fill=tk.X)

        dimensions=tk.Frame(self.frame)
        dimensions.pack(side=tk.TOP, fill=tk.X,pady=20)
        enter_name=tk.Entry(dimensions,width=50)
        enter_name.pack(side=tk.RIGHT, padx=10)
        label_name=tk.Label(dimensions,text="Choose your JSON file name :")
        label_name.pack(side=tk.RIGHT)

        bot2=tk.Frame(self.frame)
        bot2.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=20)
        label_file=tk.Label(bot2,text="Here is you generated JSON file : ")
        label_file.pack(side=tk.TOP, pady=10)
        file=tk.Entry(bot2)
        file.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)

        bot=tk.Frame(self.frame)
        bot.pack(side=tk.BOTTOM, fill=tk.X)
        finish_button=tk.Button(bot, text="generate", padx=10, width=20, command=lambda: generate_command_NSR())
        finish_button.config(state=tk.DISABLED)
        finish_button.pack(pady=10,padx=10)

        def generate_command_NSR():
                json=json_entry.get()
                path=enter_path.get()
                #[-h] --json JSON [--out OUT] [--angle ANGLE] [--offset OFFSET] [--draw] [--opti] [--tileSize TILESIZE]
                command="python .\GenTiles.py --json "+json+" -o "+path
                if enter_name.get()!="":
                        name=enter_name.get()
                        command+=" --name "+name
                self.generate_command(command)

        def choisir_json(entry):
                # Ouvre une boîte de dialogue pour choisir un fichier PNG
                fichier = filedialog.askopenfilename(filetypes=[("Fichiers JSON", "*.json")], initialdir="./OGrEE-Tools/Converter/output/OGrEE/pictures")

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
                front=json_entry.get()
                if (front!=""):
                        finish_button.config(state=tk.NORMAL)

        return self.frame
