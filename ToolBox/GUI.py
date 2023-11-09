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

        self.bottom=tk.Frame(root, bg="light grey")
        self.bottom.pack(side=tk.BOTTOM, fill=tk.X)
        enter_button=tk.Button(self.bottom, text="enter", padx=10, width=15, command=lambda: self.launch_command(self.enter.get()))
        enter_button.pack(pady=10,padx=10 ,side=tk.RIGHT)
        self.enter=tk.Entry(self.bottom, width=100)
        self.enter.pack(pady=10,padx=10 , fill=tk.X)
        self.terminal=tk.Text(self.bottom,height=6)
        self.terminal.pack(side=tk.BOTTOM, padx=10, pady=10,fill=tk.X)

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
    
root = tk.Tk()
chargement=Chargement(root)
root.mainloop()