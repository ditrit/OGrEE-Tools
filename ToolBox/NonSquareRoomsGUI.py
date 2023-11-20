import tkinter as tk
from tkinter import filedialog
import subprocess
import os
import venv

def create_NSR(self):
       # curDir = os.path.dirname(__file__)
      #  rootDir = f"{curDir}\\.."
       # setupDir = f"{rootDir}\\NonSquareRooms\\setup"
        #envDir = f"{rootDir}\\.venv\\Scripts"
        #pythonExe = f"{envDir}\\python.exe"
        #pythonExe = "C:\\Users\\Pako JUSTIN\\AppData\\Roaming\\Local\\Programs\\Python\\python.exe"
        #pythonExe = os.environ['APPDATA']+"\\..\\Local\\Programs\\Python\\python.exe"
        #subprocess.run([pythonExe, 'setup.py'])
        #os.chdir(rootDir)
        #subprocess.run([f"{envDir}\\./activate"], shell=True)
        #os.chdir(f"{rootDir}\\NonSquareRooms")

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

        #path=tk.Frame(self.frame)
        #path.pack(side=tk.TOP, fill=tk.X)
        #enter_button=tk.Button(path, text="Out path", padx=10, width=10, command=lambda: choisir_path(enter_path))
        #enter_button.pack(pady=10,padx=10 ,side=tk.LEFT)
        #enter_path=tk.Entry(path, width=100)
        #enter_path.pack(pady=10,padx=10 , fill=tk.X)

        nom=tk.Frame(self.frame)
        nom.pack(side=tk.TOP, fill=tk.X,pady=20)
        enter_name=tk.Entry(nom,width=50)
        enter_name.pack(side=tk.RIGHT, padx=10)
        label_name=tk.Label(nom,text="Choose your JSON file name (no space between words) :")
        label_name.pack(side=tk.RIGHT)

        taille=tk.Frame(self.frame)
        taille.pack(side=tk.TOP, fill=tk.X,pady=20)
        enter_taille=tk.Entry(taille,width=50)
        enter_taille.pack(side=tk.RIGHT, padx=10)
        label_taille=tk.Label(taille,text="Choose your Tiles Size :")
        label_taille.pack(side=tk.RIGHT)

        angle=tk.Frame(self.frame)
        angle.pack(side=tk.TOP, fill=tk.X,pady=20)
        enter_angle=tk.Entry(angle,width=50)
        enter_angle.pack(side=tk.RIGHT, padx=10)
        label_angle=tk.Label(angle,text="Choose your Angle :")
        label_angle.pack(side=tk.RIGHT)

        offset=tk.Frame(self.frame)
        offset.pack(side=tk.TOP, fill=tk.X,pady=20)
        enter_offset=tk.Entry(offset,width=50)
        enter_offset.pack(side=tk.RIGHT, padx=10)
        label_offset=tk.Label(offset,text="Choose your Offset :")
        label_offset.pack(side=tk.RIGHT)

       # bot2=tk.Frame(self.frame)
        #bot2.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=20)
        #label_file=tk.Label(bot2,text="Here is you generated JSON file : ")
        #label_file.pack(side=tk.TOP, pady=10)
        #file=tk.Entry(bot2)
        #file.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)

        dessin = tk.Frame(self.frame)
        dessin.pack(side=tk.RIGHT)
        dessin_label=tk.Label(dessin,width=5, text="Draw?")
        dessin_label.pack(side=tk.LEFT,padx=10, pady=10)
        varia = tk.IntVar()
        checkButton_des = tk.Checkbutton(dessin, variable=varia, onvalue=1, offvalue=0)
        checkButton_des.pack(side=tk.RIGHT, padx=10, pady=5)

        opti = tk.Frame(self.frame)
        opti.pack(side=tk.RIGHT)
        opti_label=tk.Label(opti,width=5, text="Opti?")
        opti_label.pack(side=tk.LEFT,padx=10, pady=10)
        vari = tk.IntVar()
        checkButton_opt = tk.Checkbutton(opti, variable=vari, onvalue=1, offvalue=0)
        checkButton_opt.pack(side=tk.RIGHT, padx=10, pady=5)

        bot=tk.Frame(self.frame)
        bot.pack(side=tk.BOTTOM, fill=tk.X)
        finish_button=tk.Button(bot, text="generate", padx=10, width=20, command=lambda: generate_command_NSR())
        finish_button.config(state=tk.DISABLED)
        finish_button.pack(pady=10,padx=10)

        def generate_command_NSR():
                json=json_entry.get()
                #path=enter_path.get()
                #[-h] --json JSON [--out OUT] [--angle ANGLE] [--offset OFFSET] [--draw] [--opti] [--tileSize TILESIZE]
                command="python .\GenTiles.py --json "+json
                if enter_name.get()!="":
                        name=enter_name.get()
                        command+=" --out "+name
                if enter_angle.get() != "":
                        angle=enter_angle.get()
                        command+= " --angle " + angle
                if enter_offset.get()!="":
                        offset=enter_offset.get()
                        command+= " --offset " + offset  
                if varia.get()==1:
                        command+= " --draw "
                if vari.get()==1:
                        command+= " --opti "
                if enter_taille.get() != "":
                        taille=enter_taille.get()
                        command += " --tileSize " + taille
                

                self.generate_command(command)

        def choisir_json(entry):
                # Ouvre une boîte de dialogue pour choisir un fichier Json
               
               # initial_dir=r"C:\\Users\\amine\\OGrEE-Tools-1\\NonSquareRooms"
               # fichier = filedialog.askopenfilename(filetypes=[("Fichiers JSON", "*.json")], initialdir=initial_dir)
                
                desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
                fichier = filedialog.askopenfilename(filetypes=[("Fichiers JSON", "*.json")], initialdir=desktop_path)


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
