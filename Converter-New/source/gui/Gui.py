import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import traceback

from source.ConfigHandler import ConfigHandler
from source.classes.BaseConverter import BaseConverter
from source.classes.NetBoxTodcTrack import NetBoxTodcTrack
from source.classes.dcTrackToNetBox import dcTrackToNetBox
from source.classes.dcTrackToOGrEE import dcTrackToOGrEE
from source.gui.DCIM import DCIM
from source.classes.DataLoader import EDCIM, DataLoader


class MainApp(tk.Tk):

    def __init__(self) -> None:
        """
        The __init__ function is called when the class is instantiated.
        It loads the config, sets up the GUI and defines all of its widgets.

        :return: None
        """
        super().__init__()
        self.title("DCIM Converter")
        # Initialize style
        s = ttk.Style()
        # Create style used by default for all Frames
        s.configure("Frame1.TFrame", background="green")
        s.configure("Frame2.TFrame", background="red")
        main_frame = ttk.Frame(self)
        main_frame.grid(column=0, row=0, sticky="nsew")
        main_frame.columnconfigure([0, 1], weight=1)
        main_frame.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        try:
            config = ConfigHandler()
            config.LoadConfig(f"{os.path.dirname(__file__)}/../../config.toml")
        except ConfigHandler.DCIMNotLoaded as e:
            messagebox.showwarning(
                "Config file error",
                f"One or more DCIMs config were not loaded :{e.wrongDCIMS}",
            )
        except Exception:
            traceback.print_exc()
            messagebox.showerror(
                "Config file error",
                'An error occured while loading configuration. The config file needs to be a toml file called "config.toml" in the same directory as the executable.',
            )
            self.destroy()
            return

        self.dcims: list[DCIM] = []

        self.converters: list[BaseConverter] = [
            dcTrackToNetBox(),
            NetBoxTodcTrack(),
            dcTrackToOGrEE(),
        ]
        self.converter: BaseConverter = None
        self.left_dcim: DCIM = None
        self.right_dcim: DCIM = None
        for dcim_config in config.dcims:
            if dcim_config.upper() in EDCIM.__members__:
                for dataloader_class in DataLoader.__subclasses__():
                    if EDCIM[dcim_config.upper()] == dataloader_class.edcim:
                        self.dcims.append(
                            DCIM(
                                main_frame,
                                dataloader_class(config.dcims[dcim_config].url, config.headers | {"Authorization": config.dcims[dcim_config].token}),
                                False,
                            )
                        )
                        if config.dcims[dcim_config].default_items != "":
                            try:
                                self.dcims[-1].import_from_json(open(f"{os.path.dirname(__file__)}/../../{config.dcims[dcim_config].default_items}"), False)
                            except:
                                messagebox.showwarning(
                                    "Config file error",
                                    f"Can't load default items file for {dcim_config}.",
                                )
                                traceback.print_exc()
                        if config.dcims[dcim_config].default_models != "":
                            try:
                                self.dcims[-1].import_from_json(open(f"{os.path.dirname(__file__)}/../../{config.dcims[dcim_config].default_models}"), True)
                            except:
                                messagebox.showwarning(
                                    "Config file error",
                                    f"Can't load default models file for {dcim_config}.",
                                )
                                traceback.print_exc()

        def on_select(event):
            left = EDCIM[combobox_left.get()].value if combobox_left.get() in EDCIM.__members__ else float("inf")
            right = EDCIM[combobox_right.get()].value if combobox_right.get() in EDCIM.__members__ else float("-inf")
            for dcim in self.dcims:
                dcim.grid_forget()
                if dcim.DCIM.value == right:
                    self.right_dcim = dcim
                    dcim.grid(column=1, row=1, sticky="nsew")
                if dcim.DCIM.value == left:
                    self.left_dcim = dcim
                    dcim.grid(column=0, row=1, sticky="nsew")
            self.converter = None
            for converter in self.converters:
                if converter.dcim_code == right - left:
                    self.converter = converter
            print(self.converter)

        options = list(map(lambda s: s.name, list(EDCIM)))
        combobox_left = ttk.Combobox(main_frame, values=options)
        combobox_left.grid(column=0, row=0)
        combobox_left.set("From")

        combobox_left.bind("<<ComboboxSelected>>", on_select)

        combobox_right = ttk.Combobox(main_frame, values=options)
        combobox_right.grid(column=1, row=0)
        combobox_right.set("To")

        combobox_right.bind("<<ComboboxSelected>>", on_select)

        frame_button = ttk.Frame(main_frame)
        frame_button.grid(row=2, column=0, sticky="nsew", columnspan=4)
        frame_button.columnconfigure([0, 1, 2, 3], weight=1)
        button_convert = ttk.Button(frame_button, text="Convert", command=self.convert)
        button_convert.grid(column=0, row=0, sticky="nsew", columnspan=4)

    def convert(self) -> None:
        """
        ///WIP///
        The convert function is used to convert a selected item in the left DCIM tree into an object of the right DCIM.
        The function first checks if both trees are populated and if a converter has been defined. If not, it returns without doing anything.
        Then it gets the name of the selected item in the left tree and checks that this is not empty or equal to the DCIM name. If so, it returns without doing anything.
        Finally, it asks for confirmation before converting.

        :return: None
        """
        if self.left_dcim is None or self.right_dcim is None or self.converter is None:
            return
        left_item = self.left_dcim.tree_item.tree.item(self.left_dcim.tree_item.tree.selection(), "text")
        if left_item == "" or left_item == self.left_dcim.DCIM.name:
            return
        ask = messagebox.askyesno(
            None,
            f"Convert {self.left_dcim.tree_item.tree.item(self.left_dcim.tree_item.tree.selection(),'text')} into {self.right_dcim.DCIM.name} object ?",
        )
