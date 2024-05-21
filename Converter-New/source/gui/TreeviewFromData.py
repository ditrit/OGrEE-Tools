from tkinter import ttk
from typing import Any, Callable
from source.gui.DynamicTable import DynamicTable


class TreeviewFromData(ttk.Frame):
    """
    A treeview that is dynamically updated with data from a dictionary. Represents the data as a tree.
    """

    tree: ttk.Treeview
    dynamic_table: DynamicTable

    def __init__(self, parent: Any, on_select_tree: Callable, dcim_name: str, mirrored: bool = False, **options) -> None:
        """
        The __init__ function is called when the class is instantiated.
        It sets up the instance of the class, and defines all its attributes.

        :param parent: Any: Specify the parent widget of the new object
        :param on_select_tree: Callable: Pass a function to the class called when its treeview is selected
        :param dcim_name: str: Set the heading of the treeview
        :param mirrored: bool: Determine if the table and tree are left and right or right and left
        :param **options: Pass in any number of keyword arguments
        :return: None
        """
        super().__init__(parent, **options)
        self.rowconfigure(0, weight=1)
        self.columnconfigure([0, 2] if not mirrored else [0, 1], weight=1)
        self.dynamic_table = DynamicTable(self, mirrored)
        self.dynamic_table.grid(column=2 if not mirrored else 0, sticky="nsew")
        self.tree = ttk.Treeview(self)
        self.tree.heading("#0", text=dcim_name)
        self.tree.grid(column=0 if not mirrored else 1, row=0, sticky="nsew")

        tree_scroll = ttk.Scrollbar(self, command=self.tree.yview)
        tree_scroll.grid(column=1 if not mirrored else 2, row=0, sticky="nsw")
        self.tree.configure(yscrollcommand=tree_scroll.set)
        self.tree.bind(
            "<<TreeviewSelect>>",
            on_select_tree,
        )  # Bind the selection event

    def create_treeview_from_data(self, data: dict) -> None:
        """
        The create_treeview_from_data function takes in a dictionary and calls the aux function.
        The aux function is a recursive function that takes in a dictionary and
        a parent node. It iterates through the dictionary, inserting each key as
        a child of the parent node. If the value associated with that key is also
        a dictionary, it calls itself again on that value and passes in its own
        item_id as the new parent.

        :param data: dict: Pass the dictionary to the function
        :return: None
        """

        def aux(data: dict, parent: str) -> None:
            for k, v in data.items():
                item_id = self.tree.insert(parent, "end", text=k)
                aux(v, item_id)

        aux(data, "")

    def redraw(self, data: dict) -> None:
        """
        The redraw function is called when the user clicks on a button in the GUI.
        The function deletes all of the entries in both tables and then calls
        create_treeview_from_data to repopulate them with new data.

        :param data: dict: Pass the data to the redraw function
        :return: None
        """
        self.tree.delete(*self.tree.get_children())
        self.dynamic_table.delete_table_entries()
        self.create_treeview_from_data(data)
