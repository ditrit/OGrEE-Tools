from tkinter import ttk
from typing import Any
from source.gui.VerticalScrollFrame import VerticalScrolledFrame


class DynamicTable(ttk.Frame):
    """
    A table that is dynamically updated with data from a dictionary.
    """

    def __init__(self, parent: Any, is_model: bool, mirrored: bool = False, **options) -> None:
        """
        The __init__ function is called when the class is instantiated.
        It sets up the instance of the class, and defines all of its attributes.


        :param parent: Any: Pass the parent widget to the class
        :param is_model: bool: Determine if the treeview is a model or an item view
        :param mirrored: bool: Determine whether the window is mirrored or not
        :param **options: Pass in keyword arguments
        :return: None
        """
        super().__init__(parent, **options)
        self.parent = parent
        self.is_model = is_model
        self.mirrored = mirrored
        self.table_frame = VerticalScrolledFrame(self)
        self.table_frame.grid(column=0, row=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def update_table_rows(self, new_data: dict[str, None | str | dict | list]) -> None:
        """
        The update_table_rows function takes a potentially recursive dictionary and recursively flattens it into a UI table.
        It does this by iterating through the dictionary, creating labels for each key and entries for each value.
        If the value is another dict or list, then it will create labels and entries for those keys and values as well.

        :param new_data: Pass in the new data that will be used to update the table
        :return: None
        """

        def flatten_dict(indent: int, row: int, key: str, value: None | str | dict | list) -> int:
            """
            The flatten_dict function takes a key and value and add them to a UI table row.
            If the value is another dict or list, then it will create labels and entries for those keys and values as well.

            :param indent: int: Determine how many levels deep the function is
            :param row: int: Keep track of the row number
            :param key: str: Determine what the label text should be
            :param value: None | str | dict | list: Determine the value that is passed in
            :return: The row number of the last item in the dictionary
            """
            label = ttk.Label(
                self.table_frame.interior,
                text=key,
                anchor="w" if not self.mirrored else "e",
                borderwidth=1,
                relief="solid",
                background="silver" if isinstance(value, dict) or isinstance(value, list) else "ghostwhite",
            )
            label.grid(row=row, column=0 if not self.mirrored else 1, sticky="nsew", padx=(indent * 10, 0))
            if isinstance(value, dict):
                row += 1
                for k, v in value.items():
                    row = flatten_dict(indent + 1, row, k, v)
            elif isinstance(value, list):
                row += 1
                for i in range(len(value)):
                    row = flatten_dict(
                        indent + 1,
                        row,
                        (
                            value[i]["name"]
                            if hasattr(value[i], "__iter__") and "name" in value[i]
                            else value[i]["display"] if hasattr(value[i], "__iter__") and "display" in value[i] else i
                        ),
                        value[i],
                    )
            else:
                entry = ttk.Entry(self.table_frame.interior)
                entry.insert(0, str(value) if value is not None else "")
                entry.grid(row=row, column=1 if not self.mirrored else 0, sticky="ew")
                row += 1
            return row

        for child in self.table_frame.interior.winfo_children():
            child.destroy()
        row = 0
        for key, value in new_data.items():
            row = flatten_dict(0, row, key, value)

        self.table_frame.interior.columnconfigure([0, 1], weight=1)

    def delete_table_entries(self) -> None:
        """
        The delete_table_entries function is used to delete all the entries in the table.
        This function is called when the treeview is redrawn

        :return: None
        """
        for child in self.table_frame.interior.winfo_children():
            child.destroy()
