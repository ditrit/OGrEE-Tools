import tkinter as tk

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
            "ACAD2OGrEE":self.create_A2O,
            "NonSquareRooms":self.create_NSR,
            "VSS2PNG":self.create_V2P,
            "3DTools":self.create_3DT,
            "FBX Converter":self.create_FBX
        }

        self.current_frame = None

    ##Mettez vos codes pour chacun des outils dans les frames en-dessous

    #frame for ACAD2OGrEE
    def create_A2O(self):
        frame = tk.Frame(self.root, width=200, height=100, bg="red")
        frame.pack_propagate(False)
        label = tk.Label(frame, text="Frame 1 Content", bg="red", fg="white")
        label.pack(fill=tk.BOTH, expand=True)
        return frame


    #frame for NonSquareRooms
    def create_NSR(self):
        frame = tk.Frame(self.root, width=200, height=100, bg="yellow")
        frame.pack_propagate(False)
        label = tk.Label(frame, text="Frame 1 Content", bg="yellow", fg="white")
        label.pack(fill=tk.BOTH, expand=True)
        return frame

    #frame for VSS2PNG
    def create_V2P(self):
        frame = tk.Frame(self.root, width=200, height=100, bg="blue")
        frame.pack_propagate(False)
        label = tk.Label(frame, text="Frame 1 Content", bg="blue", fg="white")
        label.pack(fill=tk.BOTH, expand=True)
        return frame

    #frame for 3DTools
    def create_3DT(self):
        frame = tk.Frame(self.root, width=200, height=100, bg="green")
        frame.pack_propagate(False)
        label = tk.Label(frame, text="Frame 1 Content", bg="green", fg="white")
        label.pack(fill=tk.BOTH, expand=True)
        return frame

    #frame for FBX Converter
    def create_FBX(self):
        frame = tk.Frame(self.root, width=200, height=100, bg="pink")
        frame.pack_propagate(False)
        label = tk.Label(frame, text="Frame 1 Content", bg="pink", fg="white")
        label.pack(fill=tk.BOTH, expand=True)
        return frame

    #changement de la frame en changeant d'item dans la liste

    def show_selected_frame(self, event):
        selected_item = self.listbox.get(self.listbox.curselection())
        frame_creator = self.tool_frames.get(selected_item)
        if self.current_frame:
            self.current_frame.destroy()
        if frame_creator:
            self.current_frame = frame_creator()
            self.current_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    
root = tk.Tk()
chargement=Chargement(root)
root.mainloop()