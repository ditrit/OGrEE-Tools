import tkinter as tk
from tkinter import filedialog
import subprocess
import os
import venv

def create_NSR(self,root_Dir):
        rootDir = root_Dir
        setupDir = f"{rootDir}\\NonSquareRooms\\setup"
        envDir = f"{rootDir}\\.venv\\Scripts"
        pythonExe = f"{envDir}\\python.exe"
        #pythonExe = "C:\\Users\\Pako JUSTIN\\AppData\\Roaming\\Local\\Programs\\Python\\python.exe"
        os.chdir(setupDir)
        #pythonExe = os.environ['APPDATA']+"\\..\\Local\\Programs\\Python\\python.exe"
        subprocess.run([pythonExe, 'setup.py'])
        os.chdir(rootDir)
        subprocess.run([f"{envDir}\\./activate"], shell=True)
        os.chdir(f"{rootDir}\\NonSquareRooms")

#Création de la fenetre pour NonSquareRooms
        self.frame = tk.Frame(self.root, width=200, height=100)
        self.frame.pack_propagate(False)

        label = tk.Label(self.frame, text="NonSquareRooms")
        label.pack(pady=10)

#création du label json afin d'afficher le fichier Json que l'utilisateur veut traiter avec le NonSquareRooms
        json = tk.Frame(self.frame)
        json.pack(fill=tk.X, pady=20)
        json_label = tk.Label(json, text="Choose your json file :", anchor="w")
        json_label.pack(fill=tk.X,side=tk.TOP, pady=20)
        json_entry = tk.Entry(json)
        json_entry.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)
        front_parcourir = tk.Button(json, text="Parcourir", command=lambda: choisir_json(json_entry), width=20)
        front_parcourir.pack(side=tk.RIGHT, padx=20)

#création du label name afin que l'utilisateur renseigne un nom de fichier si il le souhaite
        nom=tk.Frame(self.frame)
        nom.pack(side=tk.TOP, fill=tk.X,pady=20)
        enter_name=tk.Entry(nom,width=50)
        enter_name.pack(side=tk.RIGHT, padx=10)
        label_name=tk.Label(nom,text="Choose your JSON file name (no space between words) :")
        label_name.pack(side=tk.RIGHT)


#création du label taille afin que l'utilisateur renseigne la valeur souhaitée si il en a besoin
        taille=tk.Frame(self.frame)
        taille.pack(side=tk.TOP, fill=tk.X,pady=20)
        enter_taille=tk.Entry(taille,width=50)
        enter_taille.pack(side=tk.RIGHT, padx=10)
        label_taille=tk.Label(taille,text="Choose your Tiles Size (in cm) :")
        label_taille.pack(side=tk.RIGHT)

#création du label angle afin que l'utilisateur renseigne la valeur souhaitée si il en a besoin
        angle=tk.Frame(self.frame)
        angle.pack(side=tk.TOP, fill=tk.X,pady=20)
        enter_angle=tk.Entry(angle,width=50)
        enter_angle.pack(side=tk.RIGHT, padx=10)
        label_angle=tk.Label(angle,text="Choose your Angle (in °) :")
        label_angle.pack(side=tk.RIGHT)

#création du label offset afin que l'utilisateur renseigne la valeur souhaitée si il en a besoin
        offset=tk.Frame(self.frame)
        offset.pack(side=tk.TOP, fill=tk.X,pady=20)
        enter_offset=tk.Entry(offset,width=50)
        enter_offset.pack(side=tk.RIGHT, padx=10)
        label_offset=tk.Label(offset,text="Choose your Offset (x,y) (in cm) :")
        label_offset.pack(side=tk.RIGHT)

#création de la case à cocher draw pour savoir si l'utilisateuur veut ou non utiliser cette option
        dessin = tk.Frame(self.frame)
        dessin.pack(side=tk.RIGHT)
        dessin_label=tk.Label(dessin,width=5, text="Draw?")
        dessin_label.pack(side=tk.LEFT,padx=10, pady=10)
        varia = tk.IntVar()
        checkButton_des = tk.Checkbutton(dessin, variable=varia, onvalue=1, offvalue=0)
        checkButton_des.pack(side=tk.RIGHT, padx=10, pady=5)

#création de la case à cocher Opti pour savoir si l'utilisateuur veut ou non utiliser cette option
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


#fonction permettant d'obtenir le chemin complet menant à GenTiles.py
        def find_gen_tiles():   
                target_file = "GenTiles.py"
                start_directory = os.getcwd() 
                for root, dirs, files in os.walk(start_directory):
                        if target_file in files:
                                return os.path.join(root, target_file)





        def generate_command_NSR():
                json=json_entry.get()
                json_f=os.path.basename(json)

                # Utilisez la fonction pour trouver le chemin complet de GenTiles.py
                gen_tiles_path = find_gen_tiles()
                #commande si on exécute la focntion GenTiles avant
                command="python .\GenTiles.py --json "+json_f
                
                #commmande si on veut pouvoir executer directement sans lancer GentTiles au préalable 
                
                # command= gen_tiles_path+" --json "+json_f
                #on ajoute les informations: nom du fichier, angle, offset, taille, optimisation, dessin si l'utilisateur les impose
                if enter_name.get()!="":
                        name=enter_name.get()
                        command+=" --out "+name+".json"
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
                #on recherche directement les fichiers Json présent dans le Répertoire de l'ordinateur
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
