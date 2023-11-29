import tkinter as tk
from tkinter import filedialog
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
        self.root.title("Chargement")

        self.tools=["ACAD2OGrEE","NonSquareRooms","VSS2PNG","3DTools","FBX Converter"] #liste de tous les outils
        self.buttons={}

        #set up de la fenêtre de pré chargement

        self.head=tk.Frame(root, bg="light grey")
        self.head.pack(fill="x")
        lb1=tk.Label(self.head,width=20 , text="Tools",bg="light grey")
        lb1.pack(side=tk.LEFT, padx=10, pady=10)
        lb2=tk.Label(self.head , text="Launch", bg="light grey")
        lb2.pack(side=tk.LEFT, padx=40, pady=10)

        for i in self.tools:
            frame = tk.Frame(root)
            frame.pack(side=tk.TOP)
            tool_label=tk.Label(frame,width=20 , text=i)
            tool_label.pack(side=tk.LEFT,padx=10, pady=10)
            var = tk.IntVar()
            checkButton = tk.Checkbutton(frame, variable=var, onvalue=1, offvalue=0)
            checkButton.pack(side=tk.LEFT, padx=40, pady=10)

            # Stocker les boutons dans le dictionnaire avec le nom comme clé
            self.buttons[i] = var

        self.launch_button=tk.Button(root, text="Launch ToolBox", command=self.launch)
        self.launch_button.pack(side=tk.BOTTOM,pady=10)

        root.resizable(False, False)

    #lancement de la fenêtre principal de la toolbox

    def launch(self):
        self.root.destroy()
        principal=tk.Tk()
        toLaunch=[]
        for i in self.tools:
            if self.buttons[i].get()==1:
                toLaunch.append(i)
        self.toolbox=ToolBox(principal, toLaunch)
        principal.mainloop()

    def run(self):
        self.root.mainloop()

class ToolBox():
    def __init__(self, root, tools):
        self.root=root
        self.root.title("ToolBox")
        self.root.state('zoomed') ##set the window to full screen

        #création de la barre du bas

        self.bottom=tk.Frame(root, bg="light grey")
        self.bottom.pack(side=tk.BOTTOM, fill=tk.X)
        enter_button=tk.Button(self.bottom, text="enter", padx=10, width=15, command=lambda: self.launch_command(self.enter.get()))
        enter_button.pack(pady=10,padx=10 ,side=tk.RIGHT)
        self.enter=tk.Entry(self.bottom, width=100)
        self.enter.pack(pady=10,padx=10 , fill=tk.X)
        self.terminal=tk.Text(self.bottom,height=6)
        self.terminal.pack(side=tk.BOTTOM, padx=10, pady=10,fill=tk.X)

        #création de la liste d'outils
        self.side_frame=tk.Frame(root,width=40)
        self.side_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.listbox = tk.Listbox(self.side_frame,  font="20", width=40)
        for i in tools:
            self.listbox.insert(tk.END, i)
        self.listbox.pack(fill=tk.X)
        self.listbox.bind("<ButtonRelease-1>", self.show_selected_frame)

        self.tree = ttk.Treeview(self.side_frame, show="tree",height=200)
        self.tree.pack(side=tk.BOTTOM,fill=tk.BOTH,)
        self.fsobjects = {}

        self.file_image = tk.PhotoImage(file="./ToolBox/Icons/file.png")
        self.folder_image = tk.PhotoImage(file="./ToolBox/Icons/folder.png")
        self.tree.tag_bind("fstag", "<<TreeviewOpen>>", self.item_opened)
        self.load_tree("D:\IMT-A2\Projet entreprise\OGrEE-Tools","")
        

        self.tool_frames={
            "ACAD2OGrEE":create_A2O,
            "NonSquareRooms":create_NSR,
            "VSS2PNG":create_V2P,
            "3DTools":create_3DT,
            "FBX Converter":create_FBX
        }

        self.current_frame = None

    #changement de la frame en changeant d'outil dans la liste
    def show_selected_frame(self, event):
        selected_item = self.listbox.get(self.listbox.curselection())
        frame_creator = self.tool_frames.get(selected_item)
        if self.current_frame:
            self.current_frame.destroy()
        if frame_creator:
            self.current_frame = frame_creator(self)
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

    #Ecrit la commande dans la barre en bas de l'écran
    def generate_command(self,command):
        self.enter.delete(0, tk.END)
        self.enter.insert(0,command)

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

    def safe_iterdir(self, path) :
        """
        Like `Path.iterdir()`, but do not raise on permission errors.
        """
        try:
            return tuple(Path(path).iterdir())
        except PermissionError:
            print("You don't have permission to read", path)
            return ()

    def insert_item(self, name, path, parent):
        """
        Insert a file or folder into the treeview and return the item ID.
        """
        iid = self.tree.insert(
            parent, tk.END, text=name, tags=("fstag",),
            image=self.get_icon(path))
        self.fsobjects[iid] = path
        return iid
    
    def load_subitems(self, iid):
        """
        Load the content of each folder inside the specified item
        into the treeview.
        """
        for child_iid in self.tree.get_children(iid):
            if Path(self.fsobjects[child_iid]).is_dir():
                self.load_tree(self.fsobjects[child_iid],
                            parent=child_iid)

    def item_opened(self, event):
        """
        Handler invoked when a folder item is expanded.
        """
        iid = self.tree.selection()[0]
        # If it is a folder, loads its content.
        self.load_subitems(iid)

    def get_icon(self, path):
        """
        Return a folder icon if `path` is a directory and
        a file icon otherwise.
        """
        return self.folder_image if Path(path).is_dir() else self.file_image
    
root = tk.Tk()
chargement=Chargement(root)
root.mainloop()