import traceback
import typing
from tkinter import filedialog, messagebox, simpledialog, ttk

from source.classes.DataLoader import DataLoader, EDCIM
from source.gui.TreeviewFromData import TreeviewFromData


class DCIM(ttk.Frame):
    def __init__(self, parent, data_loader : DataLoader, mirrored: bool, **options) -> None:
        """
        The __init__ function is called when the class is instantiated.
        It sets up the GUI and initializes all of its widgets.
        
        
        :param parent: Tell the class which window it should be a part of
        :param data_loader : DataLoader: Pass the data_loader object to the class
        :param mirrored: bool: Determine if the window is mirrored or not
        :param **options: Pass in any keyword arguments that are not explicitly defined in the function
        :return: None
        """
        super().__init__(parent, **options)
        self.DCIM : EDCIM = data_loader.edcim
        self.rowconfigure(0,weight=1)
        self.columnconfigure(0,weight=1)
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0,column=0,sticky="nsew")
        self.data_loader = data_loader

        self.page_items = ttk.Frame(self.notebook)        
        self.notebook.add(self.page_items, text="Items")
        self.page_items.columnconfigure(0, weight=1)
        self.page_items.rowconfigure(0, weight=1)

        self.tree_item = TreeviewFromData(self.page_items, lambda e: self.tree_item.dynamic_table.update_table_rows(self.data_loader.item_data[e.widget.item(e.widget.selection(), "text")]),data_loader.edcim.name, mirrored)
        self.tree_item.grid(column=0,row=0,sticky="nsew")
        button_frame = ttk.Frame(self.page_items)
        button_frame.grid(row=1, column=0, sticky="nsew")

        button_import_all = ttk.Button(button_frame, text="Import All", command=self.get_all_items)
        button_import_all.grid(column=0, sticky="nsew")

        button_import_one_item = ttk.Button(button_frame, text="Import one item", command=self.get_one_item)
        button_import_one_item.grid(column=1, row=0, sticky="nsew")

        button_import_json = ttk.Button(button_frame, text="Import from file", command=lambda: self.ask_import_from_json(False))
        button_import_json.grid(column=0, row=1, sticky="nsew")

        button_export_json = ttk.Button(button_frame, text="Save to file", command=lambda: self.export_to_json(False))
        button_export_json.grid(column=1, row=1, sticky="nsew")

         # Second Page
        self.page_models = ttk.Frame(self.notebook)
        self.notebook.add(self.page_models, text="Models")
        self.page_models.columnconfigure(0, weight=1)
        self.page_models.rowconfigure(0, weight=1)
        
        self.tree_model = TreeviewFromData(self.page_models, lambda e: self.tree_model.dynamic_table.update_table_rows(self.data_loader.model_data[e.widget.item(e.widget.selection(), "text")]),data_loader.edcim.name, mirrored)
        self.tree_model.grid(column=0,row=0,sticky="nsew")
        button_frame = ttk.Frame(self.page_models)
        button_frame.grid(row=1, column=0, sticky="nsew")

        button_import_all = ttk.Button(button_frame, text="Import All", command=self.get_all_models)
        button_import_all.grid(column=0, sticky="nsew")

        button_import_one_model = ttk.Button(button_frame, text="Import one model", command=self.get_one_model)
        button_import_one_model.grid(column=1, row=0, sticky="nsew")

        button_import_one_manufacturer = ttk.Button(button_frame, text="Import one manufacturer", command=self.get_one_manufacturer)
        button_import_one_manufacturer.grid(column=2, row=0, sticky="nsew")

        button_import_json = ttk.Button(button_frame, text="Import from file", command=lambda: self.ask_import_from_json(True))
        button_import_json.grid(column=0, row=1, sticky="nsew")

        button_export_json = ttk.Button(button_frame, text="Save to file", command=lambda: self.export_to_json(True))
        button_export_json.grid(column=1, row=1, sticky="nsew")
    
    def import_from_json(self, file: typing.IO, model: bool) -> None:
        """
        The import_from_json function is used to import data from a json file.
        If there's an error while importing, it will show up in a messagebox.
        
        :param file: typing.IO: Specify the file to be imported
        :param model: bool: Determine whether the data is a model or an item tree
        :return: None
        """
        try:
            self.data_loader.import_from_json(file, model)
        except Exception:
            traceback.print_exc()
            messagebox.showerror("Error", f"Can't retrieve data : make sure that the file is of the correct format.")
            return
        if model:
            self.tree_model.redraw(self.data_loader.model_tree)
        else:
            self.tree_item.redraw(self.data_loader.item_tree)

    def ask_import_from_json(self, model: bool) -> None:
        """
        The ask_import_from_json function is used to import data from a JSON file.                
        
        :param model: bool: Determine whether the data is a model or an item tree
        :return: None
        """
        file = filedialog.askopenfile(
            title="Chose your DCIM data", defaultextension=".json", filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )
        if not file:
            return
        self.import_from_json(file, model)

    def export_to_json(self, model: bool) -> None:
        """
        The export_to_json function is used to export the data from the program into a JSON file.                
        
        :param model: bool: Determine whether the data is a model or an item tree
        :return: None
        """
        file = filedialog.asksaveasfile(
            title="Chose a file to save to", defaultextension=".json", filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )
        try:
            self.data_loader.export_to_json(file, model)
        except Exception:
            traceback.print_exc()
            messagebox.showerror("Error", f"Can't save the data.")

    def get_one_item(self) -> None:
        """
        The get_one_item function is used to retrieve a single item from the API and redraws the treeview with it.
        It asks for the category and name of the item, then retrieves it using 
        the data_loader's get_one_item function. If an error occurs, it displays 
        a messagebox with an error message.
        
        :return: None
        """
        category = simpledialog.askstring(title="", prompt="Enter the category of the item")
        zoomed = self.winfo_toplevel().state() == "zoomed"
        if category is None:
            return
        self.winfo_toplevel().after(
            50,
            lambda: (self.winfo_toplevel().withdraw(), self.winfo_toplevel().deiconify(), zoomed and self.winfo_toplevel().state("zoomed")),
        )
        name = simpledialog.askstring(title="", prompt="Enter the name of the item")
        if name is None:
            return
        try:
            self.data_loader.get_one_item(name, category)
        except Exception:
            traceback.print_exc()
            messagebox.showerror("Item not found", f"Can't retrieve {category} {name} : make sure that there is no typo and that the API is online.")
            return
        self.tree_item.redraw(self.data_loader.item_tree)

    def get_all_items(self) -> None:
        """
        The get_all_items function retrieves all items from the API and redraws the treeview with them.
        
        :return: None
        """
        try:
            self.data_loader.get_all_items()
        except Exception:
            traceback.print_exc()
            messagebox.showerror("Items not found", f"Can't retrieve data : make sure that the API is online.")
            return
        self.tree_item.redraw(self.data_loader.item_tree)

    def get_one_model(self) -> None:
        """
        The get_one_model function retrieves a model from the API and displays it in the treeview.
        
        :return: None
        """
        name = simpledialog.askstring(title="", prompt="Enter the name of the model")
        if name is None:
            return
        try:
            self.data_loader.get_one_model(name)
        except Exception:
            traceback.print_exc()
            messagebox.showerror("Model not found", f"Can't retrieve {name} : make sure that there is no typo and that the API is online.")
            return
        self.tree_model.redraw(self.data_loader.model_tree)

    def get_one_manufacturer(self) -> None:
        """
        The get_one_manufacturer function retrieves the manufacturer's name from the user and calls
        the get_one_manufacturer function of data_loader. If an error occurs, it displays a messagebox with
        an error message. Otherwise, it redraws the treeview.
        
        :return: None
        """
        name = simpledialog.askstring(title="", prompt="Enter the name of the manufacturer")
        if name is None:
            return
        try:
            self.data_loader.get_one_manufacturer(name)
        except Exception:
            traceback.print_exc()
            messagebox.showerror("Manufacturers not found", f"Can't retrieve {name} : make sure that there is no typo and that the API is online.")
            return
        self.tree_model.redraw(self.data_loader.model_tree)

    def get_all_models(self) -> None:
        """
        The get_all_models function retrieves all the models from the database.

        :return: None
        """
        try:
            self.data_loader.get_all_models()
        except Exception:
            traceback.print_exc()
            messagebox.showerror("Items not found", f"Can't retrieve data : make sure that the API is online.")
        self.tree_model.redraw(self.data_loader.model_tree)