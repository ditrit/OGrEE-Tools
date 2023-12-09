import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import json
import os
from PIL import Image,ImageTk

def create_FBX(self,root_dir):
        self.frame = ttk.Frame(self.root, width=200, height=100)
        self.frame.pack_propagate(False)

        self.images_utilisees={
                "Avant":'',
                "Arrière":'',
                "Haut":'',
                "Bas":'',
                "Gauche":'',
                "Droite":''
                }

        def generate_command_FBX():
                if test_generate():
                        w,d,h=get_dimensions()
                        avant=self.images_utilisees["Avant"]
                        path=enter_path.get()
                        command="python "+root_dir+"\Converter\source\\fbx\FbxBuilder.py --WDH "+str(w)+","+str(d)+","+str(h)+" --front '"+avant+"' -o '"+path+"'"
                        if enter_name.get()!="":
                                name=enter_name.get()
                                command+=" --name '"+name+"'"
                        if self.images_utilisees["Arrière"]!="":
                                command+=" --back '"+self.images_utilisees["Arrière"]+"'"
                        if self.images_utilisees["Haut"]!="":
                                command+=" --top '"+self.images_utilisees["Haut"]+"'"
                        if self.images_utilisees["Bas"]!="":
                                command+=" --bottom '"+self.images_utilisees["Bas"]+"'"
                        if self.images_utilisees["Gauche"]!="":
                                command+=" --left '"+self.images_utilisees["Gauche"]+"'"
                        if self.images_utilisees["Droite"]!="":
                                command+=" --right '"+self.images_utilisees["Droite"]+"'"
                        self.generate_command(command)
                else :
                        self.launch_error('Missing arguments')

        def choisir_png(text):
                nouvelle_fenetre = tk.Toplevel(self.root)
                nouvelle_fenetre.title("Nouvelle Fenêtre")
                nouvelle_fenetre.state("zoomed")

                bot=ttk.Frame(nouvelle_fenetre)
                bot.pack(side=tk.BOTTOM,fill=tk.X)
                text_images=tk.Text(bot, height=8)
                text_images.pack(side=tk.LEFT,fill=tk.X, padx=2, pady=15, expand=True)
                contenu=text.get("1.0", tk.END)
                text_images.insert("0.0",contenu[0:len(contenu)-2])
                text_images.delete(tk.END)
                bot2=ttk.Frame(bot)
                bot2.pack(side=tk.RIGHT)
                size_label=ttk.Label(bot2,text="Choix de la face : ")
                size_label.pack(side=tk.TOP)
                options = ["Avant", "Arrière","Haut","Bas","Gauche","Droite"]
                selected_option = tk.StringVar() # Créer une variable pour stocker la valeur sélectionnée
                combo_box = ttk.Combobox(bot2, textvariable=selected_option, values=options)
                combo_box.pack(side=tk.TOP,pady=5)

                def select(event):
                        self.selected_value = combo_box.get()

                def add_image():
                        debut=''
                        text=''
                        if self.image_actuelle!='':
                                if len(self.image_labels)>1:
                                        for img_label in self.image_labels:
                                                img_label.configure(background='SystemButtonFace')
                                if self.selected_value == "Avant":
                                        debut='Avant'
                                        self.images_utilisees['Avant']=self.image_actuelle
                                        text='Avant - '+ get_name(self.image_actuelle) +'\n'
                                elif self.selected_value == "Arrière":
                                        debut='Arrière'
                                        self.images_utilisees['Arrière']=self.image_actuelle
                                        text='Arrière - '+ get_name(self.image_actuelle) +'\n'
                                elif self.selected_value == "Haut":
                                        debut='Haut'
                                        self.images_utilisees['Haut']=self.image_actuelle
                                        text='Haut - '+ get_name(self.image_actuelle) +'\n'
                                elif self.selected_value == "Bas":
                                        debut='Bas'
                                        self.images_utilisees['Bas']=self.image_actuelle
                                        text='Bas - '+ get_name(self.image_actuelle) +'\n'
                                elif self.selected_value == "Gauche":
                                        debut='Gauche'
                                        self.images_utilisees['Gauche']=self.image_actuelle
                                        text='Gauche - '+ get_name(self.image_actuelle) +'\n'
                                elif self.selected_value == "Droite":
                                        debut='Droite'
                                        self.images_utilisees['Droite']=self.image_actuelle
                                        text='Droite - '+ get_name(self.image_actuelle) +'\n'

                                self.image_actuelle='' #Déselectionne l'image 

                                #Verifie si il y a déja une image attribuée à la face choisie
                                contenu=text_images.get("1.0", tk.END)
                                occurrence = contenu.find(debut)
                                if occurrence != -1:
                                        # Si une occurrence est trouvée, supprimer l'ancienne suite
                                        fin_ligne = contenu.find("\n", occurrence)
                                        new_contenu=contenu[0:occurrence]+contenu[fin_ligne+1:len(contenu)-1]
                                        text_images.delete(f"0.0",tk.END)
                                        text_images.insert(tk.END,new_contenu)
                                text_images.insert(tk.END,text)

                def validate():
                        contenu=text_images.get("1.0", tk.END)
                        text.delete(f"0.0",tk.END)
                        text.insert(tk.END,contenu)
                        nouvelle_fenetre.destroy()

                combo_box.bind("<<ComboboxSelected>>", select) # Associer une fonction à l'événement de sélection
                button1=ttk.Button(bot2,text="Ajouter", padding=(40,5,40,5), command=lambda: add_image())
                button1.pack(side=tk.TOP)
                button2=ttk.Button(bot2,text="Valider", padding=(40,5,40,5), command=lambda: validate())
                button2.pack(side=tk.TOP)

                left=ttk.Frame(nouvelle_fenetre)
                left.pack(side=tk.LEFT,fill=tk.Y)

                right=ttk.Frame(nouvelle_fenetre)
                right.pack(side=tk.LEFT,fill=tk.BOTH, expand=True)
                canvas_images = tk.Canvas(right)
                canvas_images.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

                self.image_actuelle=''
                self.image_labels=[]
                self.selected_value=''

                # Ajouter une barre de défilement verticale à droite du canevas
                scrollbar = ttk.Scrollbar(right, orient=tk.VERTICAL, command=canvas_images.yview)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                canvas_images.config(yscrollcommand=scrollbar.set)
                scrollbar.config(command=canvas_images.yview)

                def lister_images_png(repertoire):
                        images_png = [f for f in os.listdir(repertoire) if f.lower().endswith(".png")]
                        return images_png

                def charger_images(repertoire):
                        images = []
                        images_png = lister_images_png(repertoire)

                        for image_png in images_png:
                                chemin_image = os.path.join(repertoire, image_png)
                                image = Image.open(chemin_image)
                                images.append((image, ImageTk.PhotoImage(image)))

                        return images



                def afficher_images(liste_images,noms,directory,inner_frame, width=250, height=100):
                        def image_clicked(image_path,label):
                                self.image_actuelle=image_path
                                for img_label in self.image_labels:
                                        img_label.configure(background='SystemButtonFace')
                                # Mettre en surbrillance l'image sélectionnée en changeant la couleur de fond
                                label.configure(background='blue')
                                
                        self.image_labels=[]
                        id = 0
                        for (img, imgtk), nom in zip(liste_images, noms):
                                # Redimensionner l'image
                                imgtk_resized = ImageTk.PhotoImage(img.resize((width, height)))

                                # Afficher l'image redimensionnée dans le canevas
                                label_image = ttk.Label(inner_frame, image=imgtk_resized)
                                label_image.image = imgtk_resized  # Garantit que la référence à l'image est maintenue
                                label_image.grid(row=(id // 3)*2, column=id % 3,padx=5)

                                # Associer le callback au clic de l'image
                                label_image.bind("<Button-1>", lambda event, path=directory + "\\" + nom, label=label_image: image_clicked(path,label))
                                self.image_labels.append(label_image)
                                
                                for i in range(len(nom)):
                                        if (nom[i:i+4]=='.png'):
                                                nom=nom[0:i]
                                # Afficher le nom de l'image en dessous
                                label_name = ttk.Label(inner_frame, text=nom)
                                label_name.grid(row=(id // 3)*2 + 1, column=id % 3)

                                id += 1

                def update_images(event):
                        item_selectionne = self.tree.selection()
                        item_tag = self.tree.item(item_selectionne)['text'][-4:-1]+self.tree.item(item_selectionne)['text'][-1]
                        if item_tag==".png":
                                item_type='png'
                        else:
                                item_type='folder'

                        if item_selectionne:
                        # Si l'élément sélectionné dans l'arbre est un dossier un vérifie s'il contient des images et si oui on les affiche
                                if item_type == 'folder':
                                        # Récupérer le parent de l'élément sélectionné
                                        parent = self.tree.parent(item_selectionne)
                                        nom_parent=self.tree.item(parent)['text']

                                        # Si le parent est une chaîne vide, cela signifie que l'élément sélectionné est à la racine
                                        selected_directory = ""
                                        while nom_parent!="":
                                                selected_directory = nom_parent +"\\"+ selected_directory
                                                parent = self.tree.parent(parent)
                                                nom_parent=self.tree.item(parent)['text']
                                        selected_directory=selected_directory+"\\"+self.tree.item(item_selectionne)['text']

                                        selected_directory_path = (root_dir+"\\" +selected_directory)

                                        # Effacer les anciennes images
                                        for widget in canvas_images.winfo_children():
                                                widget.destroy()

                                        #création d'une frame qui va pouvoir contenir nos images
                                        inner_frame = ttk.Frame(canvas_images)
                                        canvas_images.create_window((0, 0), window=inner_frame, anchor=tk.NE)

                                        # Charger et afficher les nouvelles images avec leurs noms
                                        images = charger_images(selected_directory_path)
                                        noms=lister_images_png(selected_directory_path)
                                        afficher_images(images,noms,selected_directory_path,inner_frame)

                                        canvas_images.update_idletasks()  # Met à jour le canevas avant de configurer la barre de défilement
                                        canvas_images.config(scrollregion=canvas_images.bbox(tk.ALL))

                                #si l'élément est un png on l'affiche simplement
                                elif item_type == 'png':
                                        self.image_actuelle=self.tree.item(item_selectionne)['text']
                                        parent = self.tree.parent(item_selectionne)
                                        nom_parent=self.tree.item(parent)['text']
                                        self.image_labels=[]

                                        # Si le parent est une chaîne vide, cela signifie que l'élément sélectionné est à la racine
                                        selected_directory = ""
                                        while nom_parent!="":
                                                selected_directory = nom_parent +"\\"+ selected_directory
                                                parent = self.tree.parent(parent)
                                                nom_parent=self.tree.item(parent)['text']
                                        selected_directory=selected_directory+"\\"+self.tree.item(item_selectionne)['text']

                                        selected_directory_path = (root_dir+"\\" +selected_directory)

                                        # Effacer les anciennes images
                                        for widget in canvas_images.winfo_children():
                                                widget.destroy()  

                                        #On affiche l'image
                                        image = Image.open(selected_directory_path)
                                        imgtk = ImageTk.PhotoImage(image)
                                        label_image = ttk.Label(canvas_images, image=imgtk)
                                        label_image.image = imgtk  # Garantit que la référence à l'image est maintenue
                                        label_image.pack(side=tk.TOP, anchor="center")


                #Création de l'arborescence de fichier en utilisant les fonctions précédentes
                self.tree = ttk.Treeview(left, show="tree",height=30)
                self.tree.pack(side=tk.LEFT,fill=tk.BOTH)
                self.tree.column("#0", width=400)
                self.fsobjects = {}
                self.file_image = tk.PhotoImage(file=root_dir+"/ToolBox/Icons/file.png") #On affecte file.png comme icone des fichiers 
                self.folder_image = tk.PhotoImage(file=root_dir+"/ToolBox/Icons/folder.png") #On affecte folder.png comme icone des dossiers
                self.tree.tag_bind("fstag", "<<TreeviewOpen>>", self.item_opened)
                self.load_tree(root_dir,"")
                self.tree.bind("<<TreeviewSelect>>", update_images)

        def get_name(path):
                ind=0
                for i in range(len(path)):
                        if path[i]=="\\":
                                ind=i
                path=path[ind+1:len(path)] 
                for i in range(len(path)):
                        if path[i:i+4]=='.png':
                                path=path[0:i]
                return path


        def choisir_path(enter):
                file_path = filedialog.askdirectory(initialdir=os.getcwd())
                enter.delete(0, tk.END)  # Efface le contenu actuel de l'Entry
                enter.insert(0, file_path)

        def choisir_JSON(entry):
                os.chdir(root_dir+"/Converter/output/OGrEE/templates")
                fichier = filedialog.askopenfilename(filetypes=[("Fichiers JSON", "*.json")], initialdir=os.getcwd())
                os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                # Affiche le lien du fichier dans l'Entry
                entry.delete(0, tk.END)  # Efface le contenu actuel de l'Entry
                entry.insert(0, fichier)  # Insère le lien du fichier choisi

        def test_generate():
                w,d,h=get_dimensions()
                avant=self.images_utilisees['Avant']
                out=enter_path.get()
                if (w!="" and d!="" and h!="" and avant!="" and out!=""):
                        return True
                else : 
                        return False

        def on_select(event):
                selected_value = combo_box.get()
                for widget in dimension_display.winfo_children():
                        widget.destroy()
                if selected_value == "manually (cm)":
                        w_label=ttk.Label(dimension_display,text=" w ")
                        w_label.pack(side=tk.LEFT,padx=10)
                        w_entry=ttk.Entry(dimension_display,width=5)
                        w_entry.insert(0,"434")
                        w_entry.pack(side=tk.LEFT)
                        d_label=ttk.Label(dimension_display,text=" d ")
                        d_label.pack(side=tk.LEFT,padx=10)
                        d_entry=ttk.Entry(dimension_display,width=5)
                        d_entry.insert(0,"755")
                        d_entry.pack(side=tk.LEFT)
                        h_label=ttk.Label(dimension_display,text=" h ")
                        h_label.pack(side=tk.LEFT,padx=10)
                        h_entry=ttk.Entry(dimension_display,width=5,)
                        h_entry.insert(0,"87")
                        h_entry.pack(side=tk.LEFT)
                elif selected_value == "with a JSON":
                        parcourir_JSON=ttk.Button(dimension_display,text="Choose JSON",width=20, command=lambda: choisir_JSON(JSON_entry))
                        parcourir_JSON.pack(side=tk.LEFT,padx=10)
                        JSON_entry=ttk.Entry(dimension_display)
                        JSON_entry.pack(side=tk.LEFT,padx=10,fill=tk.X, expand=True)

        def get_dimensions():
                w,d,h='','',''
                widgets=[]
                for widget in dimension_display.winfo_children():
                        if widget.winfo_class()=="TEntry":
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
                return w,d,h

        label = ttk.Label(self.frame, text="FBX Converter")
        label.pack(pady=5)

        front = ttk.Frame(self.frame)
        front.pack(fill=tk.X, pady=5)
        front_label = ttk.Label(front, text="Choisissez vos images :", anchor="w")
        front_label.pack(fill=tk.X,side=tk.TOP, pady=5)
        
        images=tk.Text(front,height=6)
        images.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)
        front_parcourir = ttk.Button(front, text="Parcourir", command=lambda: choisir_png(images), width=20)
        front_parcourir.pack(side=tk.RIGHT, padx=20)

        dimensions=ttk.Frame(self.frame)
        dimensions.pack(side=tk.TOP, fill=tk.X,pady=5)
        size_label=ttk.Label(dimensions,text="Choose the dimensions of your component : ")
        size_label.pack(side=tk.LEFT,pady=5)
        options = ["manually (cm)", "with a JSON"]
        selected_option = tk.StringVar() # Créer une variable pour stocker la valeur sélectionnée
        combo_box = ttk.Combobox(dimensions, textvariable=selected_option, values=options)
        combo_box.pack(side=tk.LEFT,pady=5)
        combo_box.set("manually (cm)") # Définir une option par défaut
        combo_box.bind("<<ComboboxSelected>>", on_select) # Associer une fonction à l'événement de sélection
        enter_name=ttk.Entry(dimensions,width=50)
        enter_name.pack(side=tk.RIGHT, padx=10)
        label_name=ttk.Label(dimensions,text="Choose your FBX file name :")
        label_name.pack(side=tk.RIGHT)
        

        dimension_display=ttk.Frame(self.frame)
        dimension_display.pack(side=tk.TOP, fill=tk.X,pady=10)

        path=ttk.Frame(self.frame)
        path.pack(side=tk.TOP, fill=tk.X)
        enter_button=ttk.Button(path, text="Out path", padding=(0,5,0,5), command=lambda: choisir_path(enter_path))
        enter_button.pack(pady=5,padx=10 ,side=tk.LEFT)
        enter_path=ttk.Entry(path, width=100)
        enter_path.pack(pady=5,padx=10 , fill=tk.X)

        bot=ttk.Frame(self.frame)
        bot.pack(side=tk.BOTTOM, fill=tk.X)
        finish_button=ttk.Button(bot, text="generate", padding=(0,10,0,10), width=20, command=lambda: generate_command_FBX())
        finish_button.pack(pady=5,padx=10)

        return self.frame


        