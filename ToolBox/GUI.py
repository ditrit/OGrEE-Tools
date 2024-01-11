import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import subprocess
from pathlib import Path
from FBX import *
from VSS2PNG import *
from NonSquareRoomsGUI import *
from ACAD2OGrEE import *
from Tools3D import *

class Chargement():
    def __init__(self,root):
        self.root = root
        self.root_Dir = ""
        self.root.title("Chargement")

        self.tools=["ACAD2OGrEE","NonSquareRooms","VSS2PNG","3DTools","FBX Converter"] #liste de tous les outils
        self.buttons={}

        #set up de la fenêtre de pré chargement

        #Entête
        self.head=ttk.Frame(root)
        self.head.pack(fill="x")
        lb1=ttk.Label(self.head,width=20 , text="Tools")
        lb1.pack(side=tk.LEFT, padx=10, pady=10)
        lb2=ttk.Label(self.head , text="Launch")
        lb2.pack(side=tk.LEFT, padx=40, pady=10)

        #Création des boutons
        for i in self.tools:
            frame = ttk.Frame(root)
            frame.pack(side=tk.TOP)
            tool_label=ttk.Label(frame,width=20 , text=i)
            tool_label.pack(side=tk.LEFT,padx=10, pady=10)
            var = tk.IntVar()
            checkButton = ttk.Checkbutton(frame, variable=var, onvalue=1, offvalue=0)
            checkButton.pack(side=tk.LEFT, padx=40, pady=10)

            # Stocker les boutons dans le dictionnaire avec le nom comme clé
            self.buttons[i] = var

        self.launch_button=ttk.Button(root, text="Launch ToolBox", command=self.launch)
        self.launch_button.pack(side=tk.BOTTOM,pady=10)

        root.resizable(False, False)

    #lancement de la fenêtre principal de la toolbox

    def launch(self):
        self.root_Dir = os.path.dirname(os.path.dirname(__file__))
        toLaunch=[]
        for i in self.tools:
            if self.buttons[i].get()==1:
                toLaunch.append(i)
        if len(toLaunch)>0:
            self.root.destroy()
            principal=tk.Tk()
            self.toolbox=ToolBox(principal, toLaunch, self.root_Dir)
            principal.mainloop()

    def run(self):
        self.root.mainloop()

class ToolBox():
    def __init__(self, root, tools,root_dir):
        self.root_Dir=root_dir
        self.root=root
        self.root.title("ToolBox")
        self.root.state('zoomed') ##set the window to full screen

        #création de la barre du bas

        self.bottom=ttk.Frame(root, relief="solid", borderwidth=2)
        self.bottom.pack(side=tk.BOTTOM, fill=tk.X)
        enter_button=ttk.Button(self.bottom, text="enter", padding=(0,10,0,10), width=15, command=lambda: self.launch_command(self.enter.get()))
        enter_button.pack(pady=10,padx=10 ,side=tk.RIGHT)
        self.enter=ttk.Entry(self.bottom, width=100)
        self.enter.pack(pady=10,padx=10 , fill=tk.X)
        self.terminal=tk.Text(self.bottom,height=6)
        self.terminal.pack(side=tk.BOTTOM, padx=10, pady=10,fill=tk.X)

        #création de la liste d'outils
        self.side_frame=ttk.Frame(root,width=40)
        self.side_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.listbox = tk.Listbox(self.side_frame,  font="20", width=40)
        for i in tools:
            self.listbox.insert(tk.END, i)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        self.listbox.bind("<ButtonRelease-1>", self.show_selected_frame)

        #Liste de toute les fonctions correspondant à chaque outil
        self.tool_frames={
            "ACAD2OGrEE":create_A2O,
            "NonSquareRooms":create_NSR,
            "VSS2PNG":create_V2P,
            "3DTools":create_3DT,
            "FBX Converter":create_FBX
        }

        self.current_frame = None #Pas de fenêtre affichée au départ

    #changement de la frame en changeant d'outil dans la liste
    def show_selected_frame(self, event):
        selected_item = self.listbox.get(self.listbox.curselection()) #Récupère l'item sélectionné dans la liste
        frame_creator = self.tool_frames.get(selected_item) #Prend la fonction associée
        if self.current_frame:
            self.current_frame.destroy() #Enlève l'ancienne fenêtre
        if frame_creator:
            self.current_frame = frame_creator(self,self.root_Dir) #Crée la nouvelle en appelant la fonction
            self.current_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # Lance la commande dans le terminal et print le résultat et les erreur en sortie
    def launch_command(self,command):
        output=subprocess.run(command,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.terminal.tag_config('command',foreground="blue")
        self.terminal.tag_config('error',foreground="red")
        self.terminal.insert(tk.END,command+"\n",'command')
        if output.stdout!="":
            self.terminal.insert(tk.END,output.stdout+"\n")
        if output.stderr!="":
            self.terminal.insert(tk.END,output.stderr+"\n",'error')

    #Lance une erreur dans le terminal
    def launch_error(self,error):
        self.terminal.tag_config('error',foreground="red")
        self.terminal.insert(tk.END,error+"\n",'error')

    #Ecrit la commande dans la barre au-dessus du terminal
    def generate_command(self,command):
        self.enter.delete(0, tk.END)
        self.enter.insert(0,command)

    # Permet de créer une arborescence de fichier (treeview)
    def load_tree(self, path, parent):
        """
        Load the contents of `path` into the treeview.
        """
        for fsobj in self.safe_iterdir(path):
            fullpath = path / fsobj
            child = self.insert_item(fsobj.name, fullpath, parent)
            # Preload the content of each directory within `path`.
            # This is necessary to make the folder item expandable.
            if Path(fullpath).is_dir():
                for sub_fsobj in self.safe_iterdir(fullpath):
                    self.insert_item(sub_fsobj.name, fullpath / sub_fsobj, child)

    #Vérifie que l'on peut ouvrir les fichier pour les afficher dans le treeview
    def safe_iterdir(self, path) :
        try:
            return tuple(Path(path).iterdir())
        except PermissionError:
            print("You don't have permission to read", path)
            return ()
        
    #Insert un item dans le treeview
    def insert_item(self, name, path, parent):
        iid = self.tree.insert(
            parent, tk.END, text=name, tags=("fstag",),
            image=self.get_icon(path))
        self.fsobjects[iid] = path
        return iid
    
    #Affiche le contenu des fichiers déjà affichés dans le treeview
    def load_subitems(self, iid):
        for child_iid in self.tree.get_children(iid):
            if Path(self.fsobjects[child_iid]).is_dir():
                self.load_tree(self.fsobjects[child_iid],
                            parent=child_iid)

    #Gère l'ouverture des fichier dans le treeview
    def item_opened(self, event):
        iid = self.tree.selection()[0]
        # If it is a folder, loads its content.
        self.load_subitems(iid)

    #Renvoie l'icone à afficher (file ou folder)
    def get_icon(self, path):
        return self.folder_image if Path(path).is_dir() else self.file_image

root = tk.Tk()
chargement=Chargement(root)
root.mainloop()
