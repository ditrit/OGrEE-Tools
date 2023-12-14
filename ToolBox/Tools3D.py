import tkinter as tk
from tkinter import filedialog

import tkinter as tk
from tkinter import filedialog
import subprocess
import os
import venv

def create_3DT(self,root_Dir):

        rootDir = root_Dir
        toolDir = f"{rootDir}\\3dtools"
        os.chdir(toolDir)
#Création de la fenetre pour NonSquareRooms
        self.frame = tk.Frame(self.root, width=200, height=100)
        self.frame.pack_propagate(False)
        self.face = "none"

        label = tk.Label(self.frame, text="3DTools")
        label.pack(pady=10)

#création du label json afin d'afficher le fichier Json que l'utilisateur veut traiter avec le NonSquareRooms
        png = tk.Frame(self.frame)
        png.pack(fill=tk.X, pady=20)
        png_label = tk.Label(png, text="Choose your png file :", anchor="w")
        png_label.pack(fill=tk.X,side=tk.TOP, pady=20)
        png_entry = tk.Entry(png)
        png_entry.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)
        front_parcourir = tk.Button(png, text="Parcourir", command=lambda: choisir_png(png_entry), width=20)
        front_parcourir.pack(side=tk.RIGHT, padx=20)

#création du label name afin que l'utilisateur renseigne un nom de fichier si il le souhaite
        nom=tk.Frame(self.frame)
        nom.pack(side=tk.TOP, fill=tk.X,pady=20)
        enter_name=tk.Entry(nom,width=50)
        enter_name.pack(side=tk.RIGHT, padx=10)
        label_name=tk.Label(nom,text="Choose your JSON file name (no space between words) :")
        label_name.pack(side=tk.RIGHT)


#création du label taille afin que l'utilisateur renseigne la valeur souhaitée si il en a besoin
        height=tk.Frame(self.frame)
        height.pack(side=tk.TOP, fill=tk.X,pady=20)
        enter_height=tk.Entry(height,width=50)
        enter_height.pack(side=tk.RIGHT, padx=10)
        label_height=tk.Label(height,text="Choose your height (in mm) :")
        label_height.pack(side=tk.RIGHT)

#création du label angle afin que l'utilisateur renseigne la valeur souhaitée si il en a besoin
        width=tk.Frame(self.frame)
        width.pack(side=tk.TOP, fill=tk.X,pady=20)
        enter_width=tk.Entry(width,width=50)
        enter_width.pack(side=tk.RIGHT, padx=10)
        label_width=tk.Label(width,text="Choose your width (in mm) :")
        label_width.pack(side=tk.RIGHT)

#création du label offset afin que l'utilisateur renseigne la valeur souhaitée si il en a besoin
        face=tk.Frame(self.frame)
        face.pack(side=tk.TOP, fill=tk.X,pady=20)
        enter_front=tk.Button(face,text="front",width=10, command=lambda: front_button())
        enter_rear=tk.Button(face,text="rear",width=10, command=lambda: rear_button())
        enter_front.pack(side=tk.RIGHT, padx=10)
        enter_rear.pack(side=tk.RIGHT, padx=10)
        label_face=tk.Label(face,text="Choose your face :")
        label_face.pack(side=tk.RIGHT)

        bot=tk.Frame(self.frame)
        bot.pack(side=tk.BOTTOM, fill=tk.X)
        finish_button=tk.Button(bot, text="generate", padx=10, width=20, command=lambda: generate_command_3DT())
        finish_button.config(state=tk.DISABLED)
        finish_button.pack(pady=10,padx=10)


#fonction permettant d'obtenir le chemin complet menant à GenTiles.py
        def find_gen_tiles():   
                target_file = "GenTiles.py"
                start_directory = os.getcwd() 
                for root, dirs, files in os.walk(start_directory):
                        if target_file in files:
                                return os.path.join(root, target_file)


        def generate_command_3DT():
                png=png_entry.get()
                png_f=os.path.basename(png)

                # Utilisez la fonction pour trouver le chemin complet de GenTiles.py
                gen_tiles_path = find_gen_tiles()
                #commande si on exécute la focntion GenTiles avant
                command="python main.py --servername "+ png_f
                
                #commmande si on veut pouvoir executer directement sans lancer GentTiles au préalable 
                
                # command= gen_tiles_path+" --json "+json_f
                #on ajoute les informations: nom du fichier, angle, offset, taille, optimisation, dessin si l'utilisateur les impose
                if enter_height.get() != "":
                        height=enter_height.get()
                        command += " --height " + height
                if enter_width.get() != "":
                        width=enter_width.get()
                        command+= " --width " + width
                if self.face != "" :
                        command+= " --face " + self.face
                        
                self.generate_command(command)

        def front_button ():
                self.face = "front"
                enter_front.config(state=tk.DISABLED)
                enter_rear.config(state=tk.NORMAL)
                update_generate_button()
        def rear_button ():
                self.face = "rear"
                enter_front.config(state=tk.NORMAL)
                enter_rear.config(state=tk.DISABLED)
                update_generate_button()

        def choisir_png(entry):
                # Ouvre une boîte de dialogue pour choisir un fichier Json
                #on recherche directement les fichiers Json présent dans le Répertoire de l'ordinateur
                desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
                fichier = filedialog.askopenfilename(filetypes=[("Fichiers PNG", "*.png")], initialdir=desktop_path)


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
                png=png_entry.get()
                width=enter_width.get()
                height=enter_height.get()
                if (png!="") and height!="" and width!="" and self.face!="none" :
                        finish_button.config(state=tk.NORMAL)

        return self.frame
