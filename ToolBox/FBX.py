import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import json
import os

def create_FBX(self):
        self.frame = tk.Frame(self.root, width=200, height=100)
        self.frame.pack_propagate(False)

        def generate_command_FBX():
                w,d,h=get_dimensions()
                front=front_entry.get()
                back=back_entry.get()
                path=enter_path.get()
                command="python .\FbxBuilder.py --WDH "+str(w)+","+str(d)+","+str(h)+" --front "+front+" --back "+back+" -o "+path
                if enter_name.get()!="":
                        name=enter_name.get()
                        command+=" --name "+name
                self.generate_command(command)

        def choisir_png(entry):
                os.chdir("./Converter/output/OGrEE/pictures")
                # Ouvre une boîte de dialogue pour choisir un fichier PNG
                fichier = filedialog.askopenfilename(filetypes=[("Fichiers PNG", "*.png")],initialdir=os.getcwd())
                os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                # Affiche le lien du fichier dans l'Entry
                entry.delete(0, tk.END)  # Efface le contenu actuel de l'Entry
                entry.insert(0, fichier)  # Insère le lien du fichier choisi
                update_generate_button()

        def choisir_path(enter):
                file_path = filedialog.askdirectory(initialdir=os.getcwd())
                enter.delete(0, tk.END)  # Efface le contenu actuel de l'Entry
                enter.insert(0, file_path)
                update_generate_button()

        def choisir_JSON(entry):
                os.chdir("./Converter/output/OGrEE/templates")
                fichier = filedialog.askopenfilename(filetypes=[("Fichiers JSON", "*.json")], initialdir=os.getcwd())
                os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                # Affiche le lien du fichier dans l'Entry
                entry.delete(0, tk.END)  # Efface le contenu actuel de l'Entry
                entry.insert(0, fichier)  # Insère le lien du fichier choisi

        def update_generate_button():
                w,d,h=get_dimensions()
                front=front_entry.get()
                back=back_entry.get()
                out=enter_path.get()
                if (w!="" and d!="" and h!="" and front!="" and back!="" and out!=""):
                        finish_button.config(state=tk.NORMAL)

        def on_select(event):
                selected_value = combo_box.get()
                for widget in dimension_display.winfo_children():
                        widget.destroy()
                if selected_value == "manually (cm)":
                        w_label=tk.Label(dimension_display,text=" w ")
                        w_label.pack(side=tk.LEFT,padx=10)
                        w_entry=tk.Entry(dimension_display,width=5)
                        w_entry.insert(0,"434")
                        w_entry.pack(side=tk.LEFT)
                        d_label=tk.Label(dimension_display,text=" d ")
                        d_label.pack(side=tk.LEFT,padx=10)
                        d_entry=tk.Entry(dimension_display,width=5)
                        d_entry.insert(0,"755")
                        d_entry.pack(side=tk.LEFT)
                        h_label=tk.Label(dimension_display,text=" h ")
                        h_label.pack(side=tk.LEFT,padx=10)
                        h_entry=tk.Entry(dimension_display,width=5,)
                        h_entry.insert(0,"87")
                        h_entry.pack(side=tk.LEFT)
                elif selected_value == "with a JSON":
                        parcourir_JSON=tk.Button(dimension_display,text="Choose JSON",width=20, command=lambda: choisir_JSON(JSON_entry))
                        parcourir_JSON.pack(side=tk.LEFT,padx=10)
                        JSON_entry=tk.Entry(dimension_display)
                        JSON_entry.pack(side=tk.LEFT,padx=10,fill=tk.X, expand=True)

        def get_dimensions():
                w,d,h='','',''
                widgets=[]
                for widget in dimension_display.winfo_children():
                        if widget.winfo_class()=="Entry":
                                widgets.append(widget)
                if len(widgets)==3 :
                        w=widgets[0].get()
                        d=widgets[1].get()
                        h=widgets[2].get()
                elif len(widgets)==1:
                        JSON_path=widgets[0].get()
                        try:
                                with open(JSON_path, 'r') as file:
                                        data = json.load(file)
                                if "sizeWDHmm" in data:
                                        # Accéder à la liste de "sizeWDHmm"
                                        size_data = data["sizeWDHmm"]
                                        # Accéder aux éléments individuels de la liste
                                        if len(size_data) == 3:
                                                w,d,h = size_data
                                                w=w/10 #On convertit les mesures récupérées (en mm) en cm
                                                d=d/10
                                                h=h/10
                                else :
                                        self.terminal.insert(tk.END,f"Le fichier {JSON_path} ne contient pas de dimensions. \n")
                        except FileNotFoundError:
                                self.terminal.insert(tk.END,f"Erreur : le fichier {JSON_path} n'a pas été trouvé. \n")
                        except json.JSONDecodeError as e:
                                self.terminal.insert(tk.END,f"Erreur lors du décodage JSON : {e} \n")
                print(w,d,h)
                return w,d,h

        label = tk.Label(self.frame, text="FBX Converter")
        label.pack(pady=10)

        front = tk.Frame(self.frame)
        front.pack(fill=tk.X, pady=10)
        front_label = tk.Label(front, text="Choose your front image :", anchor="w")
        front_label.pack(fill=tk.X,side=tk.TOP, pady=10)
        front_entry = tk.Entry(front)
        front_entry.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)
        front_parcourir = tk.Button(front, text="Parcourir", command=lambda: choisir_png(front_entry), width=20)
        front_parcourir.pack(side=tk.RIGHT, padx=20)

        back = tk.Frame(self.frame)
        back.pack(fill=tk.X,pady=10)
        back_label = tk.Label(back, text="Choose your back image :", anchor="w")
        back_label.pack(fill=tk.X,side=tk.TOP, pady=10)
        back_entry = tk.Entry(back)
        back_entry.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)
        back_parcourir = tk.Button(back, text="Parcourir", command=lambda: choisir_png(back_entry), width=20)
        back_parcourir.pack(side=tk.RIGHT, padx=20)

        dimensions=tk.Frame(self.frame)
        dimensions.pack(side=tk.TOP, fill=tk.X,pady=10)
        size_label=tk.Label(dimensions,text="Choose the dimensions of your component : ")
        size_label.pack(side=tk.LEFT,pady=10)
        options = ["manually (cm)", "with a JSON"]
        selected_option = tk.StringVar() # Créer une variable pour stocker la valeur sélectionnée
        combo_box = ttk.Combobox(dimensions, textvariable=selected_option, values=options)
        combo_box.pack(side=tk.LEFT,pady=10)
        combo_box.set("manually (cm)") # Définir une option par défaut
        combo_box.bind("<<ComboboxSelected>>", on_select) # Associer une fonction à l'événement de sélection
        enter_name=tk.Entry(dimensions,width=50)
        enter_name.pack(side=tk.RIGHT, padx=10)
        label_name=tk.Label(dimensions,text="Choose your FBX file name :")
        label_name.pack(side=tk.RIGHT)
        

        dimension_display=tk.Frame(self.frame)
        dimension_display.pack(side=tk.TOP, fill=tk.X,pady=10)

        path=tk.Frame(self.frame)
        path.pack(side=tk.TOP, fill=tk.X)
        enter_button=tk.Button(path, text="Out path", padx=10, width=10, command=lambda: choisir_path(enter_path))
        enter_button.pack(pady=10,padx=10 ,side=tk.LEFT)
        enter_path=tk.Entry(path, width=100)
        enter_path.pack(pady=10,padx=10 , fill=tk.X)

        bot2=tk.Frame(self.frame)
        bot2.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        label_file=tk.Label(bot2,text="Here is you generated FBX file : ")
        label_file.pack(side=tk.TOP, pady=10)
        file=tk.Entry(bot2)
        file.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)

        bot=tk.Frame(self.frame)
        bot.pack(side=tk.BOTTOM, fill=tk.X)
        finish_button=tk.Button(bot, text="generate", padx=10, width=20, command=lambda: generate_command_FBX())
        finish_button.config(state=tk.DISABLED)
        finish_button.pack(pady=10,padx=10)

        return self.frame


        