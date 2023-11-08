# Imports
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
import os
import ezdxf
import sys
import numpy as np
from rdp import rdp
from collections import defaultdict
import matplotlib.pyplot as plt
import sys
import re
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.patches import Polygon
from matplotlib.patches import Rectangle
import re

matplotlib.use("TkAgg")
from tkinter.filedialog import asksaveasfile

sys.path.append("./divers")
from divers.tools import *

# To be done: json export funcion
# Add a button to select ponint to delete from the drawing


class App(tk.Tk):
    def __init__(self):
        super().__init__()  # create CTk window like you do with the Tk window
        self.initial_width = 1600
        self.initial_height = 900
        self.geometry(f"{self.initial_width}x{self.initial_height}")
        self.configure(bg="#d9d9d9")
        self.resizable(False, False)
        self.x_ratio = self.initial_width / 1280
        self.y_ratio = self.initial_height / 720
        self.cur_file = ""
        self.protocol("WM_DELETE_WINDOW", self.on_closing_window)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=70)
        self.grid_columnconfigure(1, weight=70)

        # Lieux de dessin

        self.cadre = tk.Frame(self, bg="white")
        self.canvas_width = self.initial_width * 0.7
        self.canvas_height = self.initial_height * 0.9
        self.cadre.place(relx=0.025, rely=0.05, width=self.canvas_width, height=self.canvas_height)

        self.fig, self.ax = plt.subplots(figsize=(26 * self.x_ratio, 6 * self.y_ratio), dpi=100)
        self.horizontal_line = self.ax.axhline(0, color="red", linestyle="--", visible=False, lw=1)
        self.vertical_line = self.ax.axvline(0, color="red", linestyle="--", visible=False, lw=1)
        self.fig.canvas.mpl_connect("motion_notify_event", self.cursor_hover)
        self.fig.canvas.mpl_connect("axes_leave_event", self.cursor_leave)
        self.fig.canvas.mpl_connect("motion_notify_event", self.closest_pt)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.cadre)
        self.canvas.get_tk_widget().pack()
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.cadre)
        self.toolbar.update()
        zoom_pan = ZoomPan()
        zoom_func, pan_func, release_func = zoom_pan.zoom_factory(self.ax)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH)
        self.lines_to_draw = []
        self.point_id = []

        # Menu
        self.buton_size = 33
        # bouton fichier
        self.file_border = tk.Frame(self, bg="#d9d9d9")
        self.file_border.place(relx=0.75, rely=0.05, width=self.buton_size + 4, height=self.buton_size + 4)
        self.fichier_icone = tk.PhotoImage(file="graphic/file.png")
        self.file_bouton = tk.Button(self.file_border, image=self.fichier_icone, command=self.file_func, bg="white")
        self.file_bouton.place(x=2, y=2, width=self.buton_size, height=self.buton_size)
        CreateToolTip(self.file_bouton, text="Open a file")

        # bouton axes
        self.axis_border = tk.Frame(self, bg="#d9d9d9")
        self.axis_border.place(relx=0.775, rely=0.05, width=self.buton_size + 4, height=self.buton_size + 4)
        self.axis_icone = tk.PhotoImage(file="graphic/axis.png")
        self.axis_bouton = tk.Button(self.axis_border, image=self.axis_icone, command=self.redefine_axis, bg="white")
        self.axis_bouton.place(x=2, y=2, width=self.buton_size, height=self.buton_size)
        self.rect = False
        CreateToolTip(self.axis_bouton, text="Redefine axes")

        # bouton mesure
        self.mesure_border = tk.Frame(self, bg="#d9d9d9")
        self.mesure_border.place(relx=0.8, rely=0.05, width=self.buton_size + 4, height=self.buton_size + 4)
        self.mesure_icone = tk.PhotoImage(file="graphic/regle.png")
        self.mesure_bouton = tk.Button(self.mesure_border, image=self.mesure_icone, command=self.mesurer, bg="white")
        self.mesure_bouton.place(x=2, y=2, width=self.buton_size, height=self.buton_size)
        self.mesure = False
        CreateToolTip(self.mesure_bouton, text="Measure distance between\ntwo points")

        # bouton iso_xy
        self.xy_border = tk.Frame(self, bg="#d9d9d9")
        self.xy_border.place(relx=0.825, rely=0.05, width=self.buton_size + 4, height=self.buton_size + 4)
        self.iso_xy_icone = tk.PhotoImage(file="graphic/iso_xy.png")
        self.iso_xy = tk.Button(self.xy_border, image=self.iso_xy_icone, command=self.equalize_xy, bg="white")
        self.iso_xy.place(x=2, y=2, width=self.buton_size, height=self.buton_size)
        self.are_equals = True
        CreateToolTip(self.iso_xy, text="Normalize X/Y axis\nKeep real ratio X/Y")

        # bouton json export
        self.json_border = tk.Frame(self, bg="#d9d9d9")
        self.json_border.place(relx=0.85, rely=0.05, width=self.buton_size + 4, height=self.buton_size + 4)
        self.json_icone = tk.PhotoImage(file="graphic/json.png")
        self.json = tk.Button(self.json_border, image=self.json_icone, command=self.export_to_json, bg="white")
        self.json.place(x=2, y=2, width=self.buton_size, height=self.buton_size)
        self.are_equals = True
        CreateToolTip(self.json, text="Export selected points\nto Json")

        # bouton add_points
        self.add_point_border = tk.Frame(self, bg="#d9d9d9")
        self.add_point_border.place(relx=0.75, rely=0.63, width=self.buton_size + 4, height=self.buton_size + 4)
        self.add_point_icone = tk.PhotoImage(file="graphic/plus.png")
        self.add_point_button = tk.Button(self.add_point_border, image=self.add_point_icone, command=self.on_click_add, bg="white")
        self.add_point_button.place(x=2, y=2, width=self.buton_size, height=self.buton_size)
        CreateToolTip(self.add_point_button, text="Add a Point")
        self.add = False

        # bouton select_point with area
        self.button_border = tk.Frame(self, bg="#d9d9d9")
        self.button_border.place(relx=0.775, rely=0.63, width=self.buton_size + 4, height=self.buton_size + 4)
        self.aera_icone = tk.PhotoImage(file="graphic/area.png")
        self.area_button = tk.Button(self.button_border, image=self.aera_icone, command=self.on_choose_press, bg="white")
        self.area_button.place(x=2, y=2, width=self.buton_size, height=self.buton_size)
        self.choose = False
        self.area = None
        self.selection = []
        self.selected = None
        CreateToolTip(self.area_button, text="Select points within an area\nto export too Json file")

        # bouton select_point
        self.plus_border = tk.Frame(self, bg="#d9d9d9")
        self.plus_border.place(relx=0.8, rely=0.63, width=self.buton_size + 4, height=self.buton_size + 4)
        self.plus_icone = tk.PhotoImage(file="graphic/sel_point.png")
        self.plus_button = tk.Button(self.plus_border, image=self.plus_icone, command=self.selection_points, bg="white")
        self.plus_button.place(x=2, y=2, width=self.buton_size, height=self.buton_size)
        CreateToolTip(self.plus_button, text="Select points by click")
        self.selecting_points = False
        self.selected_points = {}

        # bouton polyline
        self.polyline_border = tk.Frame(self, bg="#d9d9d9")
        self.polyline_border.place(relx=0.825, rely=0.63, width=self.buton_size + 4, height=self.buton_size + 4)
        self.polyline_icone = tk.PhotoImage(file="graphic/polyline.png")
        self.polyline_button = tk.Button(self.polyline_border, image=self.polyline_icone, command=self.extract_points, bg="white")
        self.polyline_button.place(x=2, y=2, width=self.buton_size, height=self.buton_size)
        CreateToolTip(self.polyline_button, text="Create new polyline between selected points\nRemove the other and reindex")

        # Choix des couches
        self.liste_couches = tk.Listbox(self, selectmode=tk.SINGLE)
        self.liste_couches.place(relx=0.750, rely=0.1, width=200 * self.x_ratio, height=175 * self.y_ratio)

        self.vertical_scrollbar_couches = tk.Scrollbar(self.liste_couches, orient="vertical")
        self.vertical_scrollbar_couches.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.liste_couches.config(yscrollcommand=self.vertical_scrollbar_couches.set)
        self.vertical_scrollbar_couches.config(command=self.liste_couches.yview)

        self.horizontal_scrollbar_couches = tk.Scrollbar(self.liste_couches, orient="horizontal")
        self.horizontal_scrollbar_couches.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.liste_couches.config(xscrollcommand=self.horizontal_scrollbar_couches.set)
        self.horizontal_scrollbar_couches.config(command=self.liste_couches.xview)

        # Choix des objets a dessiner
        self.liste_objets = tk.Listbox(self, selectmode=tk.MULTIPLE, activestyle="none")
        self.liste_objets.place(relx=0.750, rely=0.35, width=200 * self.x_ratio, height=175 * self.y_ratio)

        self.vertical_scrollbar_objets = tk.Scrollbar(self.liste_objets, orient="vertical")
        self.vertical_scrollbar_objets.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.liste_objets.config(yscrollcommand=self.vertical_scrollbar_objets.set)
        self.vertical_scrollbar_objets.config(command=self.liste_objets.yview)

        self.horizontal_scrollbar_objets = tk.Scrollbar(self.liste_objets, orient="horizontal")
        self.horizontal_scrollbar_objets.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.liste_objets.config(xscrollcommand=self.horizontal_scrollbar_objets.set)
        self.horizontal_scrollbar_objets.config(command=self.liste_objets.xview)

        # Box pour séléction de points
        self.box_points = DragDropListbox(self, activestyle="none")
        self.box_points.place(relx=0.750, rely=0.68, width=200 * self.x_ratio, height=175 * self.y_ratio)

        self.vertical_scrollbar_points = tk.Scrollbar(self.box_points, orient="vertical")
        self.vertical_scrollbar_points.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.box_points.config(yscrollcommand=self.vertical_scrollbar_points.set)
        self.vertical_scrollbar_points.config(command=self.box_points.yview)

        self.bind("<Button-1>", self.on_click)

        self.id_selected = []
        self.highlight = None
        self.close = None
        self.id_close = None
        self.bind("<Escape>", self.escape)

        # Lance l'app
        self.mainloop()

    ########Fonctions liées au boutons################

    # Bouton fichier
    def file_func(self):
        # option pour la selection du fichier dxf
        options = {"defaultextension": ".dxf", "filetypes": [("Fichiers dxf", ".dxf")], "initialdir": os.getcwd()}

        fichier = filedialog.askopenfilename(**options)

        self.cur_file = fichier
        if self.cur_file != "":
            # ouvre le fichier avec ezdxf
            self.doc = ezdxf.readfile(f"{self.cur_file}")
            self.msp = self.doc.modelspace()
            group = self.msp.groupby(dxfattrib="layer")

            # Charge les layers dans le dico et leurs objets associés
            a = defaultdict(lambda: defaultdict(lambda: 0))
            for layer, entities in group.items():
                for entity in entities:
                    a[layer][entity.dxftype()] += 1
            self.layers = {k: dict(a[k]) for k in a}
            self.liste_couches.delete(0, tk.END)
            # On ajoute les layers dans la fenetre adaptée
            for layer in self.layers:
                self.liste_couches.insert(tk.END, f"{layer}")

            # On trie les layers par ordre alphabetique
            elements = list(self.liste_couches.get(0, tk.END))
            elements.sort()
            self.liste_couches.delete(0, tk.END)
            for element in elements:
                self.liste_couches.insert(tk.END, element)
            self.liste_couches.insert(tk.END, "")
            self.liste_couches.itemconfigure(
                len(elements), selectbackground=self.liste_objets.cget("background"), selectforeground=self.liste_objets.cget("foreground")
            )

    # Bouton axes
    def redefine_axis(self):
        self.escape(None)
        if self.lines_to_draw == []:
            self.warning("Tracez d'abord quelque chose")

        else:
            self.point1 = []
            self.point2 = []
            self.point3 = []
            # Créer un canvas supplémentaire pour le rectangle
            if not self.rect:
                self.axis_border["bg"] = "black"
                self.mesure_bouton.configure(state="disabled")
                self.rect = True
                self.label = tk.Label(
                    self.cadre,
                    text=f"Séléctionez 2 points dans ce cadre pour servir de nouvel axe x\npuis un pour le centre",
                    background="white",
                    font=("Arial", 14),
                )
                self.label.place(relx=0.22, rely=0.00)
                self.cursor = self.canvas.mpl_connect("button_press_event", self.on_click_curseur)

            else:
                self.canvas.mpl_disconnect(self.cursor)
                self.rect = False
                self.label.destroy()
                self.axis_border["bg"] = "#d9d9d9"
                self.mesure_bouton.configure(state="normal")

    # Fonction axes
    def on_click_curseur(self, event):
        if self.point1 == []:
            if self.close:
                self.point1 = self.close
            else:
                self.point1 = [event.xdata, event.ydata]
        elif self.point2 == []:
            if self.close:
                self.point2 = self.close
            else:
                self.point2 = [event.xdata, event.ydata]
        elif self.point3 == []:
            if self.close:
                self.point3 = self.close
            else:
                self.point3 = [event.xdata, event.ydata]
            self.canvas.mpl_disconnect(self.cursor)
            self.rect = False
            self.label.destroy()

            if None in self.point1 or None in self.point2 or None in self.point3:
                self.warning("L'un des points n'est pas dans le plan !")
                self.point1 = []
                self.point2 = []
                self.point3 = []

            else:
                self.point1 = np.array(self.point1)
                self.point2 = np.array(self.point2)
                self.point3 = np.array(self.point3)
                axis1 = -self.point1 + self.point2
                axis1 /= np.linalg.norm(axis1)
                new_lines_to_draw = []
                for i in self.lines_to_draw:
                    new_lines_to_draw.append(transform_single_axis(i, self.point3, axis1, True))
                self.lines_to_draw = new_lines_to_draw
                self.point1 = []
                self.point2 = []
                self.point3 = []
                self.plot_on_canvas(self.lines_to_draw)
            self.axis_border["bg"] = "#d9d9d9"
            self.mesure_bouton.configure(state="normal")

    # Bouton mesurer
    def mesurer(self):
        self.escape(None)
        self.point1 = []
        self.point2 = []

        if not self.mesure:
            self.mesure_border["bg"] = "black"
            self.label = tk.Label(self.cadre, text=f"Séléctionez 2 points entre lesquels mesurer", background="white", font=("Arial", 14))
            self.label.place(relx=0.22, rely=0.0)
            self.mesure = True
            self.cursor = self.canvas.mpl_connect("button_press_event", self.on_click_mesure)
            self.axis_bouton.configure(state="disabled")

        else:
            self.mesure_border["bg"] = "#d9d9d9"
            self.canvas.mpl_disconnect(self.cursor)
            self.mesure = False
            self.label.destroy()
            self.canvas.draw_idle()
            self.axis_bouton.configure(state="normal")

    # Mesure
    def on_click_mesure(self, event):
        if self.point1 == []:
            if self.close:
                self.point1 = self.close
            else:
                self.point1 = [event.xdata, event.ydata]

        elif self.point2 == []:
            if self.close:
                self.point2 = self.close
            else:
                self.point2 = [event.xdata, event.ydata]
            self.canvas.mpl_disconnect(self.cursor)
            self.mesure = False
            self.label.destroy()
            if None in self.point1 or None in self.point2:
                self.warning("L'un des points n'est pas dans le plan !")
                self.point1 = []
                self.point2 = []
                self.axis_bouton.configure(state="normal")

            else:
                self.point1 = np.array(self.point1)
                self.point2 = np.array(self.point2)
                distance = np.linalg.norm(self.point1 - self.point2)
                x1 = self.point1[0]
                x2 = self.point2[0]
                y1 = self.point1[1]
                y2 = self.point2[1]

                self.ax.plot([x1, x2], [y1, y2], c="b")
                x_text = (self.point1[0] + self.point2[0]) / 2
                y_text = (self.point1[1] + self.point2[1]) / 2
                self.ax.text(x_text, y_text, f"Distance: {distance:.2f}")
                self.canvas.draw_idle()
            self.mesure_border["bg"] = "#d9d9d9"
            self.axis_bouton.configure(state="normal")

    # Bouton isométrie
    def equalize_xy(self):
        if self.are_equals:
            self.ax.set_aspect("auto")
            self.are_equals = False
        else:
            self.ax.set_aspect("equal")
            self.are_equals = True

        self.horizontal_line = self.ax.axhline(0, color="red", linestyle="--", visible=False, lw=1)
        self.vertical_line = self.ax.axvline(0, color="red", linestyle="--", visible=False, lw=1)
        self.canvas.draw_idle()

    # Bouton séléction de points par aire
    def on_choose_press(self):
        # Lorsque on clique sur le bouton pour choisir des points
        # On vérifie qu'il n'y en a pas de séléction déja en cours et sinon on lance la sélection

        if not self.choose:
            self.escape(None)
            self.button_border["bg"] = "black"
            self.choose_curs = self.ax.figure.canvas.mpl_connect("button_press_event", self.choose_area)  # evenemnt sélection
            self.choose = True
        else:
            self.button_border["bg"] = "#d9d9d9"
            self.ax.figure.canvas.mpl_disconnect(self.choose_curs)
            self.choose = False

    # Vérifie que le point de départ pour faire le triangle est valide est si oui lance le dessin
    def choose_area(self, event):
        # debut de la sélection, evennement desisn de rctangele
        start_x = event.xdata
        start_y = event.ydata
        if start_x and start_y:
            self.drop = self.fig.canvas.mpl_connect("button_release_event", lambda event: self.choosed_area(event, start_x, start_y))
            self.drag = self.fig.canvas.mpl_connect("motion_notify_event", lambda event: self.in_select(event, start_x, start_y))

    # dessine le rectangle
    @cap_frequency(24)
    def in_select(self, event, x_start, y_start):
        x = event.xdata
        y = event.ydata

        if self.area:
            self.area.remove()
            self.canvas.draw_idle()
            self.area = None

        if x and y:
            # dessin du rectangle
            self.area = Rectangle((x_start, y_start), -x_start + x, -y_start + y, fill=False, linestyle="--", lw=1.5)
            self.ax.add_patch(self.area)
            self.canvas.draw_idle()

    # détérmine la liste des points séléctionés
    def choosed_area(self, event, x_start, y_start):
        if self.selected:
            self.selected.remove()
            self.selected = None
        self.box_points.delete(0, tk.END)
        self.selected_points = {}
        self.id_selected = []
        self.selection = []
        self.id_selected = []
        x = event.xdata
        y = event.ydata
        # Fin du dessin
        if self.area:
            self.area.remove()
        self.canvas.draw_idle()
        self.area = None
        self.choose = False
        self.ax.figure.canvas.mpl_disconnect(self.choose_curs)
        self.ax.figure.canvas.mpl_disconnect(self.drag)
        self.ax.figure.canvas.mpl_disconnect(self.drop)
        self.button_border["bg"] = "#d9d9d9"
        if x and y:
            for c, i in enumerate(self.lines_to_draw):
                ids_points = self.point_id[c]
                if not False in np.equal(i[0, :], i[-1, :]) and np.shape(i)[0] > 1:
                    i = i[:-1, :]
                    ids_points = self.point_id[c][:-1]
                self.selection += list(
                    i[(i[:, 0] > min(x_start, x)) * (i[:, 0] < max(x_start, x)) * (i[:, 1] > min(y_start, y)) * (i[:, 1] < max(y_start, y)), :]
                )
                self.id_selected += list(
                    ids_points[(i[:, 0] > min(x_start, x)) * (i[:, 0] < max(x_start, x)) * (i[:, 1] > min(y_start, y)) * (i[:, 1] < max(y_start, y))]
                )

            self.selection = [list(i) for i in self.selection]
            self.highlight_selected(self.selection)

            for number, value in zip(self.id_selected, self.selection):
                label = f"point n°{number}"
                self.box_points.insert(tk.END, label)
                self.selected_points[label] = value

    # Bouton Json
    def export_to_json(self):
        if not self.selection:
            self.warning("First select some points to export")
            return
        extensions = [("Json file", "*.json")]
        default_name = get_file_name(self.cur_file)  # vire le path et l'extension

        JSON_form = tk.Toplevel()
        JSON_form.title = "JSON export"
        JSON_form.protocol("WM_DELETE_WINDOW", JSON_form.destroy)
        JSON_form.attributes("-topmost", 1)
        JSON_form.grab_set_global()
        JSON_form.grid_rowconfigure([0,1], weight=1)
        JSON_form.grid_columnconfigure([0], weight=1)

        def handle_category_change():
            if category.get() == "room":
                frame_orient.grid()
                frame_floor_unit.grid()
            else:
                frame_orient.grid_remove()
                frame_floor_unit.grid_remove()

        self.slug_valid = False
        self.height_valid = False

        def check_slug(newval, op):
            errmsg_slug.set("")
            self.slug_valid = re.match("^[a-zA-Z0-9-]+$",newval) is not None
            button_proceed.state(["!disabled"] if (self.slug_valid and self.height_valid) else ["disabled"])
            if op == "key":
                ok_so_far = re.match("^(^[a-zA-Z0-9-]+$)?$",newval) is not None
                if not ok_so_far:
                    if len(newval) == 0:
                        errmsg_slug.set("Slug can not be empty")
                    else:
                        errmsg_slug.set("Slug must be a single ASCII word")
                return ok_so_far
            if op == "focusout" and not self.slug_valid:
                if len(newval) == 0:
                    errmsg_slug.set("Slug can not be empty")
                else:
                    errmsg_slug.set("Slug must be a single word")
            return self.slug_valid

        check_slug_wrapper = (self.register(check_slug),"%P","%V")

        def check_height(newval, op):
            errmsg_height.set("")
            try:
                test = float(newval)
                self.height_valid = test >= 0
                button_proceed.state(["!disabled"] if (self.slug_valid and self.height_valid) else ["disabled"])
            except:
                self.height_valid = False
                button_proceed.state(["disabled"])
            if op == "key":
                ok_so_far = self.height_valid or len(newval) == 0
                if not ok_so_far:
                    if len(newval) == 0:
                        errmsg_height.set("Height can not be empty")
                    else:
                        errmsg_height.set("Height must be a positive float")
                return ok_so_far
            if op == "focusout" and not self.height_valid:
                if len(newval) == 0:
                    errmsg_height.set("Height can not be empty")
                else:
                    errmsg_height.set("Height must be a positive float")
            return self.height_valid

        check_height_wrapper = (self.register(check_height),"%P","%V")

        def proceed():
            JSON_form.grab_release()
            JSON_form.lower()
            preJSON = {"slug": slug.get(), "category": category.get()}
            if preJSON["category"] == "room":
                preJSON["axisOrientation"] = axis_orientation.get()
                preJSON["floorUnit"] = floor_unit.get()
            file = asksaveasfile(filetypes=extensions, defaultextension=extensions, initialfile=f"{default_name}")
            if file:
                file.write(generate_json(preJSON, self.selection, float(height.get())))
                file.close()
                JSON_form.destroy()
            else:
                JSON_form.grab_set_global()
                JSON_form.attributes("-topmost", 1)

        frame_fields = ttk.Frame(JSON_form)

        slug = tk.StringVar()
        label_slug = ttk.Label(frame_fields, text="Slug")
        entry_slug = ttk.Entry(frame_fields, textvariable=slug,validate="all",validatecommand=check_slug_wrapper)

        errmsg_slug = tk.StringVar()
        label_errmsg_slug = ttk.Label(frame_fields, font="TkSmallCaptionFont", foreground="red", textvariable=errmsg_slug)

        height = tk.StringVar()
        label_height = ttk.Label(frame_fields, text="Height")
        entry_height = ttk.Entry(frame_fields, textvariable=height,validate="all",validatecommand=check_height_wrapper)

        errmsg_height = tk.StringVar()
        label_errmsg_height = ttk.Label(frame_fields, font="TkSmallCaptionFont", foreground="red", textvariable=errmsg_height)

        category = tk.StringVar()
        frame_category = ttk.Frame(frame_fields)
        category_label = ttk.Label(frame_category,text="Category")
        building_radiobutton = ttk.Radiobutton(frame_category, text="Building", variable=category, value="building", command=handle_category_change)
        room_radiobutton = ttk.Radiobutton(frame_category, text="Room", variable=category, value="room", command=handle_category_change)

        axis_orientation = tk.StringVar()
        frame_orient = ttk.Frame(frame_fields)
        orient_label = ttk.Label(frame_orient,text="Axis Orientation")        
        orient_default_radiobutton = ttk.Radiobutton(frame_orient, text="+x+y", variable=axis_orientation, value="+x+y")
        orient_minuxX_radiobutton = ttk.Radiobutton(frame_orient, text="-x+y", variable=axis_orientation, value="-x+y")
        orient_minusY_radiobutton = ttk.Radiobutton(frame_orient, text="+x-y", variable=axis_orientation, value="+x-y")
        orient_bothMinus_radiobutton = ttk.Radiobutton(frame_orient, text="-x-y", variable=axis_orientation, value="-x-y")

        floor_unit = tk.StringVar()
        frame_floor_unit = ttk.Frame(frame_fields)
        floor_unit_label = ttk.Label(frame_floor_unit,text="Floor unit")
        meter_radiobutton = ttk.Radiobutton(frame_floor_unit, text="Meter", variable=floor_unit, value="m")
        tile_radiobutton = ttk.Radiobutton(frame_floor_unit, text="Tile", variable=floor_unit, value="t")
        foot_radiobutton = ttk.Radiobutton(frame_floor_unit, text="Foot", variable=floor_unit, value="f")

        frame_button = ttk.Frame(JSON_form)

        button_proceed = ttk.Button(frame_button, text="Save", command=proceed, state="disabled")

        button_cancel = ttk.Button(frame_button, text="Cancel", command=JSON_form.destroy)

        label_slug.grid(row=0, column=0,sticky="w")
        entry_slug.grid(row=1, column=0,sticky="w")
        label_errmsg_slug.grid(row=2, column=0,sticky="w")
        label_height.grid(row=3, column=0,sticky="w")
        entry_height.grid(row=4, column=0,sticky="w")
        label_errmsg_height.grid(row=5, column=0,sticky="w")

        category.set("building")
        category_label.grid(row=0,column=0,sticky="w")
        building_radiobutton.grid(row=1, column=0,sticky="w")
        room_radiobutton.grid(row=2, column=0,sticky="w")
        frame_category.grid(row=6, column=0,sticky="w")

        axis_orientation.set("+x+y")
        orient_label.grid(row=0,column=0,sticky="w")
        orient_default_radiobutton.grid(row=1, column=0,sticky="w")
        orient_minuxX_radiobutton.grid(row=2, column=0,sticky="w")
        orient_minusY_radiobutton.grid(row=3, column=0,sticky="w")
        orient_bothMinus_radiobutton.grid(row=4, column=0,sticky="w")
        frame_orient.grid(row=7, column=0,sticky="w")

        floor_unit.set("m")
        floor_unit_label.grid(row=0,column=0,sticky="w")
        meter_radiobutton.grid(row=1, column=0,sticky="w")
        tile_radiobutton.grid(row=2, column=0,sticky="w")
        foot_radiobutton.grid(row=3, column=0,sticky="w")
        frame_floor_unit.grid(row=8, column=0,sticky="w")

        frame_fields.grid(row=0, column=0,sticky="w")

        button_cancel.grid(row=0, column=0,sticky="w")
        button_proceed.grid(row=0, column=1,sticky="e")

        frame_button.grid(row=1, column=0,sticky="w")
        
        handle_category_change()

    # Bouton séléction de points
    def selection_points(self):
        if not self.selecting_points:
            self.escape(None)
            self.selecting_points = True
            self.config(cursor="hand2")
            self.plus_border["bg"] = "black"
            self.choose_curs = self.ax.figure.canvas.mpl_connect("button_press_event", self.choose_point)
        else:
            self.selecting_points = False
            self.config(cursor="arrow")
            self.plus_border["bg"] = "#d9d9d9"
            self.ax.figure.canvas.mpl_disconnect(self.choose_curs)

    # Séléction des points
    def choose_point(self, event):
        if self.close:
            x = self.close[0]
            y = self.close[1]
            label = f"point n°{self.id_close}"
            if not self.id_close in self.id_selected:
                self.id_selected.append(self.id_close)
                self.box_points.insert(tk.END, label)
                self.selection.append([x, y])
                self.selected_points[label] = [x, y]
            else:
                idx = self.box_points.get(0, tk.END).index(label)
                self.box_points.delete(idx)
                self.id_selected.remove(self.id_close)
                self.selection.remove([x, y])
                del self.selected_points[label]
            self.highlight_selected(self.selection)

    # Draw polyline
    # Extrait les coordonées des points séléctionés dans l'ordre
    def extract_points(self):
        if len(self.selection) != 0:
            line = []
            for i in range(self.box_points.size()):
                item = self.box_points.get(i)
                line.append(self.selected_points[item])
            line.append(line[0])
            self.lines_to_draw = np.array([line])
            self.redefine_origin()
            if self.selected:
                self.selected.remove()
                self.selected = None
            self.box_points.delete(0, tk.END)
            self.selected_points = {}
            self.id_selected = []
            self.selection = []
            self.id_selected = []

    # Add point
    def on_click_add(self):
        if not self.add:
            self.escape(None)
            self.add_point_border["bg"] = "black"
            self.add_curs = self.ax.figure.canvas.mpl_connect("button_press_event", self.add_point)  # evenemnt sélection
            self.add = True
        else:
            self.add_point_border["bg"] = "#d9d9d9"
            self.ax.figure.canvas.mpl_disconnect(self.add_curs)
            self.add = False

    def add_point(self, event):
        x = event.xdata
        y = event.ydata
        if x and y:
            self.lines_to_draw.append(np.array([[x, y]]))
        self.plot_on_canvas(self.lines_to_draw)

    ####################################################

    ####### Fonctions de dessin ########################

    # Dessine les axes sous le curseur
    @cap_frequency(24)
    def cursor_hover(self, event):
        if event.inaxes == self.ax:
            # Récupérer les coordonnées du curseur
            x = event.xdata
            y = event.ydata

            # Mettre à jour les positions des lignes
            self.horizontal_line.set_ydata([y])
            self.vertical_line.set_xdata([x])

            # Afficher les lignes
            self.horizontal_line.set_visible(True)
            self.vertical_line.set_visible(True)

            # Actualiser le graphique
            self.canvas.draw_idle()

    # Cache les axes quand le cursueur n'est pas sur le canva
    def cursor_leave(self, event):
        # Cacher les lignes lorsque le curseur quitte le graphique
        self.horizontal_line.set_visible(False)
        self.vertical_line.set_visible(False)

        # Actualiser le graphique
        self.fig.canvas.draw()

    # Charge les points de n'importe quel objet contenu dans une couche
    def dessiner_selection(self):
        # On doit récupérer les différents objets a dessiner sous forme de liste de points à dessiner

        indices_objet_selectionnes = self.liste_objets.curselection()
        objects_to_draw = []
        for i in indices_objet_selectionnes:
            objects_to_draw.append(self.liste_objets.get(i))

        self.lines_to_draw = []

        for i in objects_to_draw:
            type_dessin = re.match(r"^(?!-{3})\S+", i)
            if type_dessin:
                type_dessin = type_dessin.group()
                number = int(re.search(r"(\S+)\s*$", i).group())

                if type_dessin == "LWPOLYLINE":  # Gestion des polylines
                    polyline = self.msp.query(f'LWPOLYLINE[layer=="{self.current_layer}"]').entities[number]
                    line = []
                    for vertice in polyline:
                        line.append([vertice[0], vertice[1]])
                    line.append(line[0])
                    line = np.array(line)
                    self.lines_to_draw.append(line)

                if type_dessin == "LINE":  # Gestion des lines
                    line = self.msp.query(f'LINE[layer=="{self.current_layer}"]').entities[number]
                    x_start = line.dxf.start[0]
                    y_start = line.dxf.start[1]
                    x_end = line.dxf.end[0]
                    y_end = line.dxf.end[1]
                    self.lines_to_draw.append(np.array([[x_start, y_start], [x_end, y_end]]))

                if type_dessin == "CIRCLE":  # Gestion des lines
                    circle = self.msp.query(f'CIRCLE[layer=="{self.current_layer}"]').entities[number]

                    center = circle.dxf.center
                    radius = circle.dxf.radius

                    points = np.linspace(0, 2 * np.pi, 25)
                    points = np.array([center[0] + radius * np.cos(points), center[1] + radius * np.sin(points)]).T
                    points_to_draw = []
                    self.lines_to_draw.append(points)

                if type_dessin == "INSERT":
                    insert = self.msp.query(f'INSERT[layer=="{self.current_layer}"]').entities[number]
                    block_name = insert.dxf.name

                    x = insert.dxf.insert.x
                    y = insert.dxf.insert.y
                    x_scale = insert.dxf.xscale
                    y_scale = insert.dxf.yscale
                    rotation = insert.dxf.rotation

                    # Récupérer le bloc de définition correspondant
                    block = self.doc.blocks.get(block_name)

                    if block is not None:
                        # Parcourir les entités du bloc de définition
                        for entity in block:
                            # Vérifier le type d'entité)
                            if entity.dxftype() == "LWPOLYLINE":
                                # Récupérer les points de la POLYLINE
                                points = entity.get_points()

                                # Appliquer les transformations d'insertion
                                transformed_points = []
                                for point in points:
                                    tx = point[0] * x_scale
                                    ty = point[1] * y_scale
                                    transformed_point = (tx, ty)
                                    transformed_points.append(transformed_point)
                                poly = Polygon(transformed_points, closed=True, fill=None, edgecolor="black")
                                points = poly.xy
                                rotation = np.deg2rad(rotation)
                                points = points @ np.array([[np.cos(rotation), -np.sin(rotation)], [np.sin(rotation), np.cos(rotation)]])
                                points[:, 0] += x
                                points[:, 1] += y
                                self.lines_to_draw.append(points)

                if type_dessin == "HATCH":
                    hatch = self.msp.query(f'HATCH[layer=="{self.current_layer}"]').entities[number]
                    # Récupérer les boucles du HATCH
                    loops = hatch.paths
                    for loop in loops:
                        # Récupérer les segments de chaque boucle
                        segments = loop.edges

                        for i in loop.edges:
                            if isinstance(i, ezdxf.entities.boundary_paths.LineEdge):
                                start = i.start
                                end = i.end
                                self.lines_to_draw.append(np.array([[start[0], start[1]], [end[0], end[1]]]))
                            else:
                                center = (i.center[0], i.center[1])
                                radius = i.radius
                                start_angle = np.deg2rad(i.start_angle)
                                end_angle = np.deg2rad(i.end_angle)
                                points = np.linspace(start_angle, end_angle, 25)
                                points = np.array([center[0] + radius * np.cos(points), center[1] + radius * np.sin(points)]).T
                                self.lines_to_draw.append(points)

                if type_dessin == "ARC":
                    circle = self.msp.query(f'ARC[layer=="{self.current_layer}"]').entities[number]

                    center = circle.dxf.center
                    radius = circle.dxf.radius
                    start_angle = np.deg2rad(circle.dxf.start_angle)
                    end_angle = np.deg2rad(circle.dxf.end_angle)
                    points = np.linspace(start_angle, end_angle, 25)
                    points = np.array([center[0] + radius * np.cos(points), center[1] + radius * np.sin(points)]).T
                    points_to_draw = []
                    self.lines_to_draw.append(points)

        # Remet les points dans un référentiel local et supprime les points superflus
        self.redefine_origin()

    # Dessine les points chargés sur le dessin
    def plot_on_canvas(self, lignes):
        self.ax.clear()
        nb_point = 1
        self.point_id = []
        id_last = 1
        for ligne in lignes:
            self.point_id.append(np.arange(ligne.shape[0]) + id_last)
            id_last += ligne.shape[0]
            self.ax.plot(ligne[:, 0], ligne[:, 1], c="black")
            self.ax.scatter(ligne[:, 0], ligne[:, 1], color="b", s=9)
            for i, vertice in enumerate(ligne):
                if i > 0 and list(vertice) == list(ligne[0, :]):
                    continue
                self.ax.annotate(str(i + nb_point), vertice)
            nb_point += len(ligne[:, 0])
        self.ax.set_aspect("equal")
        self.horizontal_line = self.ax.axhline(0, color="red", linestyle="--", visible=False, lw=1)
        self.vertical_line = self.ax.axvline(0, color="red", linestyle="--", visible=False, lw=1)
        self.canvas.draw()

    # Met en surbrillance le point le plus proche
    @cap_frequency(20)
    def closest_pt(self, event):
        if self.lines_to_draw != []:
            compte_pt = 0
            pt = -1
            d_min = 99999
            x = event.xdata
            y = event.ydata

            if x and y:
                for c, line in enumerate(self.lines_to_draw):
                    distance = np.sqrt((line[:, 0] - x) ** 2 + (line[:, 1] - y) ** 2)
                    d = np.min(distance)
                    compte_pt = np.shape(d)
                    if d < d_min:
                        d_min = d
                        point_actuel = line[np.argmin(distance), :]
                        id_actuel = self.point_id[c][np.argmin(distance)]
                        pt = np.argmin(distance)
                    compte_pt += np.shape(d)

            delta = 0.01 * (self.ax.get_xlim()[1] - self.ax.get_xlim()[0])

            if d_min < delta:
                self.close = list(point_actuel)
                self.id_close = id_actuel
                if not self.highlight:
                    self.highlight = self.ax.scatter(point_actuel[0], point_actuel[1], c="blue", s=80)

            elif d_min > delta:
                if self.highlight:
                    self.highlight.remove()
                    self.highlight = None
                    self.close = None
                    self.i_close = None
            self.canvas.draw_idle()

    # Met en surbrillance les points séléctionés
    def highlight_selected(self, list_selected):
        if self.selected:
            self.selected.remove()
        if len(list_selected) != 0:
            list_selected = np.array(list_selected)
            self.selected = None
            self.selected = self.ax.scatter(list_selected[:, 0], list_selected[:, 1], c="blue", s=80)
            self.canvas.draw()

    ####################################################

    ########### Divers #################################

    # Permet quand on clique sur une couche d'en charger les objets et quand on clique sur un objet de le dessiner
    def on_click(self, event):
        widget_under_cursor = event.widget.winfo_containing(event.x_root, event.y_root)
        if widget_under_cursor == self.liste_couches:
            self.afficher_selection()
        elif widget_under_cursor == self.liste_objets:
            self.dessiner_selection()

    # Affiche les objets d'une couche
    def afficher_selection(self):
        # Récupérer et afficher les différents objets de la couche séléctionée
        # On recupére la layer séléctionée

        indices_selectionnes = self.liste_couches.curselection()
        self.current_layer = self.liste_couches.get(indices_selectionnes)

        self.liste_objets.delete(0, tk.END)

        # On affiche les différents objets de la layer
        try:
            for i in self.layers[self.current_layer]:
                self.liste_objets.insert(tk.END, f"--- {i} ---")

                for k in range(0, self.layers[self.current_layer][i]):
                    self.liste_objets.insert(tk.END, f"{i} {k}")
        except:
            pass

        self.liste_objets.insert(tk.END, "")
        # On bloque les titres (types d'objet ex: ---LWPOLYLINE---, ---LINE---, etc...)
        for index in range(self.liste_objets.size()):
            item = self.liste_objets.get(index)
            if item.startswith("---") or item == "":
                self.liste_objets.itemconfigure(
                    index, selectbackground=self.liste_objets.cget("background"), selectforeground=self.liste_objets.cget("foreground")
                )

    # fenetre d'avertissement
    def warning(self, message):
        # Créer une fenêtre pop-up
        window = tk.Toplevel()
        window.title("Avertissement")

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculer les coordonnées pour centrer la fenêtre pop-up
        window_width = 300  # Largeur de la fenêtre pop-up
        window_height = 150  # Hauteur de la fenêtre pop-up
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)

        # Définir les coordonnées de la fenêtre pop-up
        window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Créer un label pour afficher le message d'avertissement
        label = tk.Label(window, text=message)
        label.pack(padx=10, pady=10)

        # Fonction pour fermer la fenêtre
        def close_window():
            window.destroy()

        # Créer un bouton "OK" pour fermer la fenêtre
        button_ok = tk.Button(window, text="OK", command=close_window)
        button_ok.pack(pady=10)

        # Définir la fenêtre comme une fenêtre modale
        window.transient(window.master)
        window.grab_set()
        window.focus_set()
        window.wait_window()

    # Permet que le kernel python s'arrete proprement quand fermeture de la fenetre
    def on_closing_window(self):
        self.destroy()
        sys.exit()

    # Escape from any selection or menu
    def escape(self, event):
        if self.rect:
            self.canvas.mpl_disconnect(self.cursor)
            self.rect = False
            self.label.destroy()
            self.axis_border["bg"] = "#d9d9d9"
            self.mesure_bouton.configure(state="normal")

        if self.mesure:
            self.mesure_border["bg"] = "#d9d9d9"
            self.canvas.mpl_disconnect(self.cursor)
            self.mesure = False
            self.label.destroy()
            self.canvas.draw_idle()
            self.axis_bouton.configure(state="normal")

        if self.selecting_points:
            self.selecting_points = False
            self.config(cursor="arrow")
            self.plus_border["bg"] = "#d9d9d9"

        if self.choose:
            self.button_border["bg"] = "#d9d9d9"
            self.ax.figure.canvas.mpl_disconnect(self.choose_curs)
            self.choose = False

        if self.add:
            self.add_point_border["bg"] = "#d9d9d9"
            self.ax.figure.canvas.mpl_disconnect(self.add_curs)
            self.add = False

    # Place the leftest point to 0 and the lower one too
    def redefine_origin(self):
        if len(self.lines_to_draw) != 0:
            new_lines_to_draw = []
            for ligne in self.lines_to_draw:
                self.x_min = 1e99
                self.y_min = 1e99
                if np.min(ligne[:, 0]) < self.x_min:
                    self.x_min = np.min(ligne[:, 0])
                if np.min(ligne[:, 1]) < self.y_min:
                    self.y_min = np.min(ligne[:, 1])
            for ligne in self.lines_to_draw:
                line = rdp(ligne, epsilon=0.2) - [self.x_min, self.y_min]
                new_lines_to_draw.append(line)
            self.lines_to_draw = new_lines_to_draw
            self.plot_on_canvas(self.lines_to_draw)


###################################################
if __name__ == "__main__":
    app = App()
