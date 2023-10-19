import tkinter as tk
from tkinter import filedialog
import subprocess
from FBX import *
from VSS2PNG import *
from NonSquareRooms import *
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

        self.bottom=tk.Frame(root, bg="light grey", height=30)
        self.bottom.pack(side=tk.BOTTOM, fill=tk.X)
        enter_button=tk.Button(self.bottom, text="enter", padx=10, width=25)
        enter_button.pack(pady=10,padx=10 ,side=tk.RIGHT)
        enter=tk.Entry(self.bottom, width=100)
        enter.pack(pady=10,padx=10 , fill=tk.X)

        #création de la liste d'outils

        self.listbox = tk.Listbox(root, width=40,  font="20")
        for i in tools:
            self.listbox.insert(tk.END, i)
        self.listbox.pack(side=tk.LEFT, fill=tk.Y)
        self.listbox.bind("<ButtonRelease-1>", self.show_selected_frame)

        self.tool_frames={
            "ACAD2OGrEE":create_A2O,
            "NonSquareRooms":create_NSR,
            "VSS2PNG":create_V2P,
            "3DTools":create_3DT,
            "FBX Converter":create_FBX
        }

        self.current_frame = None

    #changement de la frame en changeant d'item dans la liste

    def show_selected_frame(self, event):
        selected_item = self.listbox.get(self.listbox.curselection())
        frame_creator = self.tool_frames.get(selected_item)
        if self.current_frame:
            self.current_frame.destroy()
        if frame_creator:
            self.current_frame = frame_creator(self)
            self.current_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # Lance la commande dans le terminal et print le résultat et les erreur en sortie
    def command(self,command):
        output=subprocess.run(command,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print("Sortie de la commande :", output.stdout)
        print("Erreurs de la commande :", output.stderr)

    ## FBX functions    
    #Update le bouton pour générer la commande
    def update_generate_button(self):
        w=self.w_entry.get()
        print(w)
        d=self.d_entry.get()
        print(d)
        h=self.h_entry.get()
        print(h)
        front=self.front_entry.get()
        print(front)
        back=self.back_entry.get()
        print(back)
        out=self.enter.get()
        print(out)
        if (w!="" and d!="" and h!="" and front!="" and back!="" and out!=""):
                self.finish_button.config(state=tk.NORMAL)

    #Génere la commande
    def generate_command(self):
        w=self.w_entry.get()
        d=self.d_entry.get()
        h=self.h_entry.get()

    def choisir_png(self,entry):
        # Ouvre une boîte de dialogue pour choisir un fichier PNG
        fichier = filedialog.askopenfilename(filetypes=[("Fichiers PNG", "*.png")])

        # Affiche le lien du fichier dans l'Entry
        entry.delete(0, tk.END)  # Efface le contenu actuel de l'Entry
        entry.insert(0, fichier)  # Insère le lien du fichier choisi
        self.update_generate_button()

    def choisir_path(self,enter):
        file_path = filedialog.askdirectory()
        enter.delete(0, tk.END)  # Efface le contenu actuel de l'Entry
        enter.insert(0, file_path)
        self.update_generate_button()
    
root = tk.Tk()
chargement=Chargement(root)
root.mainloop()