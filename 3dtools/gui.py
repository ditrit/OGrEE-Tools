import sys
import tools
from classifiers import Classifiers
from pathlib import Path
import api.yoloapi
from skimage.io import imsave
from os import remove

from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter import messagebox, scrolledtext, ttk
from PIL import Image, ImageTk


class Stdout_to_window(object):
    def __init__(self, widget):
        self.widget = widget

    def write(self, message):
        self.widget.configure(state="normal")
        if message == "\r":
            self.widget.delete(self.widget.index("end-1c linestart"), "end-1c")
        else:
            self.widget.insert(END, message)
        self.widget.configure(state="disabled")
        self.widget.see(END)

    def flush(self):
        self.widget.update_idletasks()


class Gui():
    # Resizes the image so it fits the space on screen
    def resize_image(self, image):
        if image.height > image.width:
            image = image.rotate(90)

        if image.width > 760:
            w = 760
            self.image_ratio = w / image.width
            h = int(self.image_ratio * image.height)
            return image.resize((w, h))

        else:
            self.image_ratio = 1
            return image


    # Opens a single image (front OR back face)
    def open_one_image(self):
        try:
            file = askopenfilename(initialdir="", filetypes=[("PNG image", "*.png"), ("JPEG image", "*.jpg"), ("All files", "*")])
            if file:
                print("\n" + 94 * "=" + "\n")

                self.options["servername"] = file
                self.options["path"] = 'api/tmp' + self.options["servername"].split('/')[-1]
                imsave(self.options["path"], tools.scaleim(self.options["servername"], self.options["height"], 2.0))

                image = Image.open(self.options["path"])
                image = self.resize_image(image)
                photo = ImageTk.PhotoImage(image)
                self.image_labels[0].config(image=photo)
                self.image_labels[0].image = photo
                self.image_labels[0].grid(columnspan=3, rowspan=2, column=2, row=4, padx=(20, 20), pady=(20, 20))
                self.image_labels[1].grid_remove()

                is_rear = messagebox.askyesno("Server face", "Is this image of the REAR face of the device?", icon="question")
                self.options["face"] = "rear" if is_rear else "front"

                self.classifiers = [Classifiers(self.options["servername"], self.options["height"], self.options["width"], self.options["face"])]

                print(f"\nNew image opened: {file.split('/')[-1]}.")

        except FileNotFoundError:
            messagebox.showerror("File not found", f"The file '{file}' could not be found.")


    # Opens two images (front AND back face)
    def open_two_images(self):
        self.open_one_image()

        try:
            file = askopenfilename(initialdir="", filetypes=[("PNG image", "*.png"), ("JPEG image", "*.jpg"), ("All files", "*")])
            if file:
                print("\n" + 94 * "=" + "\n")

                self.options["height_2"], self.options["width_2"] = self.options["height"], self.options["width"]

                self.options["servername_2"] = file
                self.options["path_2"] = 'api/tmp' + self.options["servername_2"].split('/')[-1]
                imsave(self.options["path_2"], tools.scaleim(self.options["servername_2"], self.options["height_2"], 2.0))

                image = Image.open(self.options["path_2"])
                image = self.resize_image(image)
                photo = ImageTk.PhotoImage(image)
                self.image_labels[1].config(image=photo)
                self.image_labels[1].image = photo
                self.image_labels[1].grid(columnspan=3, rowspan=2, column=2, row=5, padx=(20, 20), pady=(20, 20))
                self.image_labels[0].grid(columnspan=3, rowspan=2, column=2, row=3, padx=(20, 20), pady=(20, 20))

                self.options["face_2"] = "front" if self.options["face"] == "rear" else "rear"
                self.classifiers.append(Classifiers(self.options["servername_2"], self.options["height_2"], self.options["width_2"], self.options["face_2"]))

                print(f"\nNew image opened: {file.split('/')[-1]}.")

        except FileNotFoundError:
            messagebox.showerror("File not found", f"The file '{file}' could not be found.")


    # Reloads the images so new updates are shown
    def update_images(self):
        image = Image.open(self.options["path"])
        image = self.resize_image(image)
        photo = ImageTk.PhotoImage(image)
        self.image_labels[0].config(image=photo)
        self.image_labels[0].image = photo

        if bool(self.image_labels[1].winfo_ismapped()):
            image = Image.open(self.options["path_2"])
            image = self.resize_image(image)
            photo = ImageTk.PhotoImage(image)
            self.image_labels[1].config(image=photo)
            self.image_labels[1].image = photo


    # Calculates the hitboxes for each component in the images
    def calculate_hitboxes(self):
        self.hitboxes = [{}, {}]

        for i in range(len(self.classifiers)):
            sizetable = self.classifiers[i].sizetable
            num = 0
            for k in self.classifiers[i].components:
                name, compotype, angle, _ = self.classifiers[i].components[k]
                composhape = sizetable[compotype] if angle == 0 else sizetable[compotype][::-1]
                pt1 = (int(k[0]), int(k[1]))
                pt2 = (int(pt1[0] + composhape[2] * tools.RATIO), int(pt1[1] + composhape[0] * tools.RATIO))
                self.hitboxes[i][name + str(num)] = {"pt1": pt1, "pt2": pt2}
                num += 1


    # Detects slots, disks and PSUs
    def detect_all(self):
        def detect(classifier, face, servername, path):
            print(f"\n{face.title()} face:")
            if any([compotype == "slot_normal" or compotype == "slot_lp" or compotype == "disk_lff" or compotype == "disk_sff" or compotype == "PSU" for (_, compotype, *_) in classifier.components.values()]):
                print(f"  - Some components have already been detected. Try detecting each component individually.")
            else:
                self.options["classes"] = None
                pred = api.yoloapi.run(self.options["weights"], path, self.options["data"], self.options["imgsz"], self.options["conf_thres"], self.options["iou_thres"], self.options["max_det"], self.options["device"], self.options["view_img"],
                        self.options["save_txt"], self.options["save_conf"], self.options["save_crop"], self.options["nosave"], self.options["classes"], self.options["agnostic_nms"], self.options["augment"], self.options["visualize"], self.options["update"],
                        self.options["project"], self.options["name"], self.options["exist_ok"], self.options["line_thickness"], self.options["hide_labels"], self.options["hide_conf"], self.options["half"], self.options["dnn"], self.options["vid_stride"])
                # pred: a list of tensor, each tensor represent a picture
                classifier.dl_addComponents(pred.cpu())
                tools.drawcomponents_gui(servername, path, classifier.components)

        print("\n" + 94 * "=" + "\n")
        print("Detecting slots, disks and power...")
        sys.stdout.flush()

        detect(self.classifiers[0], self.options["face"], self.options["servername"], self.options["path"])
        if len(self.classifiers) == 2:
            detect(self.classifiers[1], self.options["face_2"], self.options["servername_2"], self.options["path_2"])

        self.update_images()
        self.calculate_hitboxes()


    # Detects slots
    def detect_slot(self):
        def detect(classifier, face, servername, path):
            print(f"\n{face.title()} face:")
            self.options["classes"] = [0, 1]
            if any([compotype == "slot_normal" or compotype == "slot_lp" for (_, compotype, *_) in classifier.components.values()]):
                print(f"  - Slots have already been detected.")
            else:
                pred = api.yoloapi.run(self.options["weights"], path, self.options["data"], self.options["imgsz"], self.options["conf_thres"], self.options["iou_thres"], self.options["max_det"], self.options["device"], self.options["view_img"],
                        self.options["save_txt"], self.options["save_conf"], self.options["save_crop"], self.options["nosave"], self.options["classes"], self.options["agnostic_nms"], self.options["augment"], self.options["visualize"], self.options["update"],
                        self.options["project"], self.options["name"], self.options["exist_ok"], self.options["line_thickness"], self.options["hide_labels"], self.options["hide_conf"], self.options["half"], self.options["dnn"], self.options["vid_stride"])
                # pred: a list of tensor, each tensor represent a picture
                classifier.dl_addComponents(pred.cpu())
                tools.drawcomponents_gui(servername, path, classifier.components)

        print("\n" + 94 * "=" + "\n")
        print("Detecting slots...")
        sys.stdout.flush()

        detect(self.classifiers[0], self.options["face"], self.options["servername"], self.options["path"])
        if len(self.classifiers) == 2:
            detect(self.classifiers[1], self.options["face_2"], self.options["servername_2"], self.options["path_2"])

        self.update_images()
        self.calculate_hitboxes()


    # Detects disks
    def detect_disk(self):
        def detect(classifier, face, servername, path):
            print(f"\n{face.title()} face:")
            if any([compotype == "disk_lff" or compotype == "disk_sff" for (_, compotype, *_) in classifier.components.values()]):
                print(f"  - Disks have already been detected.")
            else:
                self.options["classes"] = [2, 3]
                pred = api.yoloapi.run(self.options["weights"], path, self.options["data"], self.options["imgsz"], self.options["conf_thres"], self.options["iou_thres"], self.options["max_det"], self.options["device"], self.options["view_img"],
                        self.options["save_txt"], self.options["save_conf"], self.options["save_crop"], self.options["nosave"], self.options["classes"], self.options["agnostic_nms"], self.options["augment"], self.options["visualize"], self.options["update"],
                        self.options["project"], self.options["name"], self.options["exist_ok"], self.options["line_thickness"], self.options["hide_labels"], self.options["hide_conf"], self.options["half"], self.options["dnn"], self.options["vid_stride"])
                # pred: a list of tensor, each tensor represent a picture
                classifier.dl_addComponents(pred.cpu())
                tools.drawcomponents_gui(servername, path, classifier.components)

        print("\n" + 94 * "=" + "\n")
        print("Detecting disks...")
        sys.stdout.flush()

        detect(self.classifiers[0], self.options["face"], self.options["servername"], self.options["path"])
        if len(self.classifiers) == 2:
            detect(self.classifiers[1], self.options["face_2"], self.options["servername_2"], self.options["path_2"])

        self.update_images()
        self.calculate_hitboxes()


    # Detects PSUs
    def detect_psu(self):
        def detect(classifier, face, servername, path):
            print(f"\n{face.title()} face:")
            if any([compotype == "PSU" for (_, compotype, *_) in classifier.components.values()]):
                print(f"  - PSUs have already been detected.")
            else:
                self.options["classes"] = 4
                pred = api.yoloapi.run(self.options["weights"], path, self.options["data"], self.options["imgsz"], self.options["conf_thres"], self.options["iou_thres"], self.options["max_det"], self.options["device"], self.options["view_img"],
                        self.options["save_txt"], self.options["save_conf"], self.options["save_crop"], self.options["nosave"], self.options["classes"], self.options["agnostic_nms"], self.options["augment"], self.options["visualize"], self.options["update"],
                        self.options["project"], self.options["name"], self.options["exist_ok"], self.options["line_thickness"], self.options["hide_labels"], self.options["hide_conf"], self.options["half"], self.options["dnn"], self.options["vid_stride"])
                # pred: a list of tensor, each tensor represent a picture
                classifier.dl_addComponents(pred.cpu())
                tools.drawcomponents_gui(servername, path, classifier.components)

        print("\n" + 94 * "=" + "\n")
        print("Detecting PSU...")
        sys.stdout.flush()

        detect(self.classifiers[0], self.options["face"], self.options["servername"], self.options["path"])
        if len(self.classifiers) == 2:
            detect(self.classifiers[1], self.options["face_2"], self.options["servername_2"], self.options["path_2"])

        self.update_images()
        self.calculate_hitboxes()


    # Detects serial ports
    def detect_serial(self):
        def detect(classifier, face, servername, path):
            print(f"\n{face.title()} face:")
            if any([compotype == "rs232" for (_, compotype, *_) in classifier.components.values()]):
                print(f"  - Serial ports have already been detected.")
            else:
                classifier.clvga_rs232('male')
                tools.drawcomponents_gui(servername, path, classifier.components)

        print("\n" + 94 * "=" + "\n")
        print("Detecting serial ports...")
        sys.stdout.flush()

        detect(self.classifiers[0], self.options["face"], self.options["servername"], self.options["path"])
        if len(self.classifiers) == 2:
            detect(self.classifiers[1], self.options["face_2"], self.options["servername_2"], self.options["path_2"])

        self.update_images()
        self.calculate_hitboxes()


    # Detects VGA ports
    def detect_vga(self):
        def detect(classifier, face, servername, path):
            print(f"\n{face.title()} face:")
            if any([compotype == "vga" for (_, compotype, *_) in classifier.components.values()]):
                print(f"  - VGA ports have already been detected.")
            else:
                classifier.clvga_rs232('female')
                tools.drawcomponents_gui(servername, path, classifier.components)

        print("\n" + 94 * "=" + "\n")
        print("Detecting VGA ports...")
        sys.stdout.flush()

        detect(self.classifiers[0], self.options["face"], self.options["servername"], self.options["path"])
        if len(self.classifiers) == 2:
            detect(self.classifiers[1], self.options["face_2"], self.options["servername_2"], self.options["path_2"])

        self.update_images()
        self.calculate_hitboxes()


    # Detects BMC ports
    def detect_bmc(self):
        def detect(classifier, face, servername, path):
            print(f"\n{face.title()} face:")
            if any([compotype == "idrac" for (_, compotype, *_) in classifier.components.values()]):
                print("  - BMC interfaces have already been detected.")
            else:
                classifier.clidrac()
                tools.drawcomponents_gui(servername, path, classifier.components)

        print("\n" + 94 * "=" + "\n")
        print("Detecting BMC interfaces...")
        sys.stdout.flush()

        detect(self.classifiers[0], self.options["face"], self.options["servername"], self.options["path"])
        if len(self.classifiers) == 2:
            detect(self.classifiers[1], self.options["face_2"], self.options["servername_2"], self.options["path_2"])

        self.update_images()
        self.calculate_hitboxes()


    # Detects USB ports
    def detect_usb(self):
        def detect(classifier, face, servername, path):
            print(f"\n{face.title()} face:")
            if any([compotype == "usb" for (_, compotype, *_) in classifier.components.values()]):
                print("  - USB ports have already been detected.")
            else:
                classifier.clusb()
                tools.drawcomponents_gui(servername, path, classifier.components)

        print("\n" + 94 * "=" + "\n")
        print("Detecting USB ports...")
        sys.stdout.flush()

        detect(self.classifiers[0], self.options["face"], self.options["servername"], self.options["path"])
        if len(self.classifiers) == 2:
            detect(self.classifiers[1], self.options["face_2"], self.options["servername_2"], self.options["path_2"])

        self.update_images()
        self.calculate_hitboxes()


    # Unselects component and resets variables
    def reset(self, event=None):
        self.component_name_var.set("")
        self.component_type_var.set("")
        self.component_depth_var.set("")
        self.component_wh_var.set("")
        self.click_pt1 = None
        self.selected_component = None

        tools.drawcomponents_gui(self.options["servername"], self.options["path"], self.classifiers[0].components)
        if len(self.classifiers) == 2:
            tools.drawcomponents_gui(self.options["servername_2"], self.options["path_2"], self.classifiers[1].components)
        self.update_images()


    # Adjusts click variables to top left and bottom right corners of rectangle
    def adjust_rectangle(self):
        y1, x1 = self.click_pt1
        y2, x2 = self.click_pt2

        if x1 >= x2 and y1 <= y2:
            self.click_pt1 = (y1, x2)
            self.click_pt2 = (y2, x1)
        elif x1 <= x2 and y1 >= y2:
            self.click_pt1 = (y2, x1)
            self.click_pt2 = (y1, x2)
        elif x1 >= x2 and y1 >= y2:
            self.click_pt1, self.click_pt2 = self.click_pt2, self.click_pt1


    # Updates or creates a new component
    def save_component(self):
        if self.component_name_var.get() == "":
            print("\n" + 94 * "=" + "\n")
            print("ERROR: invalid component name.")
        elif self.component_type_var.get() == "":
            print("\n" + 94 * "=" + "\n")
            print("ERROR: invalid component type.")
        elif self.component_depth_var.get() == "":
            print("\n" + 94 * "=" + "\n")
            print("ERROR: invalid component depth.")
        elif self.image_label_selected == "top":
            if self.click_pt1 in self.classifiers[0].components:
                prev_component = self.classifiers[0].components[self.click_pt1]
                component = (self.component_name_var.get(), self.component_type_var.get(), prev_component[2], prev_component[3])
                self.classifiers[0].components[self.click_pt1] = component

                size = self.classifiers[0].sizetable[prev_component[1]]
                new_size = [size[0], round(float(self.component_depth_var.get()), 1), size[2]]
                for classifier in self.classifiers:
                    classifier.sizetable[component[1]] = new_size
                tools.SIZETABLE[component[1]] = new_size

                self.reset()
                self.calculate_hitboxes()

                print("\n" + 94 * "=" + "\n")
                print(f"Saved changes to component {component[0]} of type {component[1]}.")
            elif self.selected_component in self.classifiers[0].components:
                prev_component = self.classifiers[0].components.pop(self.selected_component)
                if self.click_pt2[1] - self.click_pt1[1] < self.click_pt2[0] - self.click_pt1[0]:
                    angle = 90
                else:
                    angle = 0
                component = (self.component_name_var.get(), self.component_type_var.get(), angle, prev_component[3])
                self.classifiers[0].components[self.click_pt1] = component

                size = [round((self.click_pt2[1] - self.click_pt1[1]) / tools.RATIO, 1), round(float(self.component_depth_var.get()), 1), round((self.click_pt2[0] - self.click_pt1[0]) / tools.RATIO, 1)]
                if angle != 0:
                    size = size[::-1]
                for classifier in self.classifiers:
                    classifier.sizetable[component[1]] = size
                tools.SIZETABLE[component[1]] = size

                self.reset()
                self.calculate_hitboxes()

                print("\n" + 94 * "=" + "\n")
                print(f"Saved changes to component {component[0]} of type {component[1]}.")
            else:
                if self.click_pt2[1] - self.click_pt1[1] < self.click_pt2[0] - self.click_pt1[0]:
                    angle = 90
                else:
                    angle = 0
                component = (self.component_name_var.get(), self.component_type_var.get(), angle, 1)
                self.classifiers[0].components[self.click_pt1] = component

                size = [round((self.click_pt2[1] - self.click_pt1[1]) / tools.RATIO, 1), round(float(self.component_depth_var.get()), 1), round((self.click_pt2[0] - self.click_pt1[0]) / tools.RATIO, 1)]
                if angle != 0:
                    size = size[::-1]
                for classifier in self.classifiers:
                    classifier.sizetable[component[1]] = size
                tools.SIZETABLE[component[1]] = size

                self.reset()
                self.calculate_hitboxes()

                self.component_type_entry.config(values=list(tools.SIZETABLE.keys()))

                print("\n" + 94 * "=" + "\n")
                print(f"Created new component {component[0]} of type {component[1]}.")
        else:
            if self.click_pt1 in self.classifiers[1].components:
                prev_component = self.classifiers[1].components[self.click_pt1]
                component = (self.component_name_var.get(), self.component_type_var.get(), prev_component[2], prev_component[3])
                self.classifiers[1].components[self.click_pt1] = component

                size = self.classifiers[1].sizetable[prev_component[1]]
                new_size = [size[0], round(float(self.component_depth_var.get()), 1), size[2]]
                for classifier in self.classifiers:
                    classifier.sizetable[component[1]] = new_size
                tools.SIZETABLE[component[1]] = new_size

                self.reset()
                self.calculate_hitboxes()

                print("\n" + 94 * "=" + "\n")
                print(f"Saved changes to component {component[0]} of type {component[1]}.")
            elif self.selected_component in self.classifiers[1].components:
                prev_component = self.classifiers[1].components.pop(self.selected_component)
                if self.click_pt2[1] - self.click_pt1[1] < self.click_pt2[0] - self.click_pt1[0]:
                    angle = 90
                else:
                    angle = 0
                component = (self.component_name_var.get(), self.component_type_var.get(), angle, prev_component[3])
                self.classifiers[1].components[self.click_pt1] = component

                size = [round((self.click_pt2[1] - self.click_pt1[1]) / tools.RATIO, 1), round(float(self.component_depth_var.get()), 1), round((self.click_pt2[0] - self.click_pt1[0]) / tools.RATIO, 1)]
                if angle != 0:
                    size = size[::-1]
                for classifier in self.classifiers:
                    classifier.sizetable[component[1]] = size
                tools.SIZETABLE[component[1]] = size

                self.reset()
                self.calculate_hitboxes()

                print("\n" + 94 * "=" + "\n")
                print(f"Saved changes to component {component[0]} of type {component[1]}.")
            else:
                if self.click_pt2[1] - self.click_pt1[1] < self.click_pt2[0] - self.click_pt1[0]:
                    angle = 90
                else:
                    angle = 0
                component = (self.component_name_var.get(), self.component_type_var.get(), angle, 1)
                self.classifiers[1].components[self.click_pt1] = component

                size = [round((self.click_pt2[1] - self.click_pt1[1]) / tools.RATIO, 1), round(float(self.component_depth_var.get()), 1), round((self.click_pt2[0] - self.click_pt1[0]) / tools.RATIO, 1)]
                if angle != 0:
                    size = size[::-1]
                for classifier in self.classifiers:
                    classifier.sizetable[component[1]] = size
                tools.SIZETABLE[component[1]] = size

                self.reset()
                self.calculate_hitboxes()

                self.component_type_entry.config(values=list(tools.SIZETABLE.keys()))

                print("\n" + 94 * "=" + "\n")
                print(f"Created new component {component[0]} of type {component[1]}.")


    # Deletes the selected component
    def delete_component(self, event=None):
        if self.image_label_selected == "top":
            if self.click_pt1 in self.classifiers[0].components:
                component = self.classifiers[0].components.pop(self.click_pt1)
                print("\n" + 94 * "=" + "\n")
                print(f"Deleted component {component[0]} of type {component[1]}.")
            elif self.selected_component in self.classifiers[0].components:
                component = self.classifiers[0].components.pop(self.selected_component)
                print("\n" + 94 * "=" + "\n")
                print(f"Deleted component {component[0]} of type {component[1]}.")
        else:
            if self.click_pt1 in self.classifiers[1].components:
                component = self.classifiers[1].components.pop(self.click_pt1)
                print("\n" + 94 * "=" + "\n")
                print(f"Deleted component {component[0]} of type {component[1]}.")
            elif self.selected_component in self.classifiers[1].components:
                component = self.classifiers[1].components.pop(self.selected_component)
                print("\n" + 94 * "=" + "\n")
                print(f"Deleted component {component[0]} of type {component[1]}.")

        self.reset()
        self.calculate_hitboxes()


    # Updates variables based on selected component
    def component_selected(self, event=None):
        if self.component_type_var.get() in tools.SIZETABLE:
            composhape = tools.SIZETABLE[self.component_type_var.get()]
            self.component_depth_var.set(composhape[1])
            self.component_wh_var.set(f"W = {composhape[0]}, H = {composhape[2]}")
            self.root.update_idletasks()


    # Draws blue rectangle following the cursor
    def follow(self, event, name):
        pt2 = (int(event.y / self.image_ratio), int(event.x / self.image_ratio))
        height = round(abs(pt2[0] - self.click_pt1[0]) / tools.RATIO, 1)
        width = round(abs(pt2[1] - self.click_pt1[1]) / tools.RATIO, 1)
        if height > width:
            height, width = width, height
        self.component_wh_var.set(f"W = {width}, H = {height}")

        if name == "top":
            tools.drawcomponents_gui(self.options["servername"], self.options["path"], self.classifiers[0].components, self.selected_component)
            tools.draw_tmp_rectangle(self.options["path"], (self.click_pt1[1], self.click_pt1[0]), (pt2[1], pt2[0]), (147, 69, 52), self.component_type_var.get())

        else:
            tools.drawcomponents_gui(self.options["servername_2"], self.options["path_2"], self.classifiers[1].components, self.selected_component)
            tools.draw_tmp_rectangle(self.options["path_2"], (self.click_pt1[1], self.click_pt1[0]), (pt2[1], pt2[0]), (147, 69, 52), self.component_type_var.get())

        self.update_images()


    # Registers the spot where the image was clicked
    def click(self, event, name):
        self.click_pt1 = (int(event.y / self.image_ratio), int(event.x / self.image_ratio))

        if name == "top":
            self.image_labels[0].bind("<Motion>", lambda event: self.follow(event, name))
        else:
            self.image_labels[1].bind("<Motion>", lambda event: self.follow(event, name))


    # Registers the spot where the click was released and checks for the selected component
    def release(self, event, name):
        self.click_pt2 = (int(event.y / self.image_ratio), int(event.x / self.image_ratio))
        self.image_label_selected = name

        if name == "top":
            self.image_labels[0].unbind("<Motion>")
            self.image_labels[0].focus_set()

            if self.click_pt1 == self.click_pt2:
                for _, v in self.hitboxes[0].items():
                    if self.click_pt1[0] >= v["pt1"][0] and self.click_pt1[0] <= v["pt2"][0] and self.click_pt1[1] >= v["pt1"][1] and self.click_pt1[1] <= v["pt2"][1]:
                        self.click_pt1 = v["pt1"]
                        self.selected_component = self.click_pt1
                        self.component_name_var.set(self.classifiers[0].components[self.click_pt1][0])
                        self.component_type_var.set(self.classifiers[0].components[self.click_pt1][1])
                        self.component_depth_var.set(self.classifiers[0].sizetable[self.classifiers[0].components[self.click_pt1][1]][1])
                        self.component_selected()

                        tools.drawcomponents_gui(self.options["servername"], self.options["path"], self.classifiers[0].components, self.click_pt1)
                        tools.draw_tmp_rectangle(self.options["path"], (v["pt1"][1], v["pt1"][0]), (v["pt2"][1], v["pt2"][0]), (133, 0, 82), self.classifiers[0].components[self.click_pt1][1])
                        self.update_images()

                        break
                else:
                    if self.component_type_var.get() in tools.SIZETABLE:
                        composhape = tools.SIZETABLE[self.component_type_var.get()]
                        self.click_pt2 = (int(self.click_pt1[0] + composhape[2] * tools.RATIO), int(self.click_pt1[1] + composhape[0] * tools.RATIO))
                        tools.drawcomponents_gui(self.options["servername"], self.options["path"], self.classifiers[0].components, self.selected_component)
                        tools.draw_tmp_rectangle(self.options["path"], (self.click_pt1[1], self.click_pt1[0]), (self.click_pt2[1], self.click_pt2[0]), (133, 0, 82), self.component_type_var.get())
                        self.update_images()
                    else:
                        self.reset()
            else:
                if self.selected_component not in self.classifiers[0].components:
                    self.selected_component = None

                if self.selected_component is None:
                    self.adjust_rectangle()
                    tools.drawcomponents_gui(self.options["servername"], self.options["path"], self.classifiers[0].components)
                    tools.draw_tmp_rectangle(self.options["path"], (self.click_pt1[1], self.click_pt1[0]), (self.click_pt2[1], self.click_pt2[0]), (147, 69, 52), self.component_type_var.get())
                    self.update_images()
                else:
                    self.adjust_rectangle()
                    tools.drawcomponents_gui(self.options["servername"], self.options["path"], self.classifiers[0].components, self.selected_component)
                    tools.draw_tmp_rectangle(self.options["path"], (self.click_pt1[1], self.click_pt1[0]), (self.click_pt2[1], self.click_pt2[0]), (133, 0, 82), self.classifiers[0].components[self.selected_component][1])
                    self.update_images()

        else:
            self.image_labels[1].unbind("<Motion>")
            self.image_labels[1].focus_set()

            if self.click_pt1 == self.click_pt2:
                for _, v in self.hitboxes[1].items():
                    if self.click_pt1[0] >= v["pt1"][0] and self.click_pt1[0] <= v["pt2"][0] and self.click_pt1[1] >= v["pt1"][1] and self.click_pt1[1] <= v["pt2"][1]:
                        self.click_pt1 = v["pt1"]
                        self.selected_component = self.click_pt1
                        self.component_name_var.set(self.classifiers[1].components[self.click_pt1][0])
                        self.component_type_var.set(self.classifiers[1].components[self.click_pt1][1])
                        self.component_depth_var.set(self.classifiers[1].sizetable[self.classifiers[1].components[self.click_pt1][1]][1])
                        self.component_selected()

                        tools.drawcomponents_gui(self.options["servername_2"], self.options["path_2"], self.classifiers[1].components, self.click_pt1)
                        tools.draw_tmp_rectangle(self.options["path_2"], (v["pt1"][1], v["pt1"][0]), (v["pt2"][1], v["pt2"][0]), (133, 0, 82), self.classifiers[1].components[self.click_pt1][1])
                        self.update_images()

                        break
                else:
                    if self.component_type_var.get() in tools.SIZETABLE:
                        composhape = tools.SIZETABLE[self.component_type_var.get()]
                        self.click_pt2 = (int(self.click_pt1[0] + composhape[2] * tools.RATIO), int(self.click_pt1[1] + composhape[0] * tools.RATIO))
                        tools.drawcomponents_gui(self.options["servername_2"], self.options["path_2"], self.classifiers[1].components, self.selected_component)
                        tools.draw_tmp_rectangle(self.options["path_2"], (self.click_pt1[1], self.click_pt1[0]), (self.click_pt2[1], self.click_pt2[0]), (133, 0, 82), self.component_type_var.get())
                        self.update_images()
                    else:
                        self.reset()
            else:
                if self.selected_component not in self.classifiers[1].components:
                    self.selected_component = None

                if self.selected_component is None:
                    self.adjust_rectangle()
                    tools.drawcomponents_gui(self.options["servername_2"], self.options["path_2"], self.classifiers[1].components)
                    tools.draw_tmp_rectangle(self.options["path_2"], (self.click_pt1[1], self.click_pt1[0]), (self.click_pt2[1], self.click_pt2[0]), (147, 69, 52), self.component_type_var.get())
                    self.update_images()
                else:
                    self.adjust_rectangle()
                    tools.drawcomponents_gui(self.options["servername_2"], self.options["path_2"], self.classifiers[1].components, self.selected_component)
                    tools.draw_tmp_rectangle(self.options["path_2"], (self.click_pt1[1], self.click_pt1[0]), (self.click_pt2[1], self.click_pt2[0]), (133, 0, 82), self.classifiers[1].components[self.selected_component][1])
                    self.update_images()


    # Redraws the editing window
    def return_to_editing(self):
        # Removes the JSON widgets
        for widget in self.json_widgets:
            widget.grid_remove()

        # Redraws the editing widgets
        for widget in self.editing_widgets:
            widget.grid()

        for label in self.image_labels:
            label.bind("<Button-1>", lambda event: self.click(event, str(event.widget).split(".")[-1]))
            label.bind("<ButtonRelease-1>", lambda event: self.release(event, str(event.widget).split(".")[-1]))
            label.bind("<BackSpace>", self.delete_component)
            label.bind("<Delete>", self.delete_component)
            label.bind("<Escape>", self.reset)

        self.reset()
        self.calculate_hitboxes()

        print("\n" + 94 * "=" + "\n")
        print("Click 'Return to detection' if you wish to automatically detect another component.")
        print("Click inside a rectangle on the image to select a component and edit its name, type and depth.")
        print("Click on the top left corner after selecting a component to adjust its position.")
        print("You can also draw a new rectangle to adjust its size. Press 'Esc' to unselect a component.")
        print("You can create a new component by drawing its rectangle or by placing it (if type selected).")
        print("Don't forget to enter a name, type and depth for the new component.")
        print("Use the buttons to save your changes or to delete a component after selecting it.")
        print("When you're done, click 'Finish editing' to proceed.")


    # Redraws the detection window
    def return_to_detection(self):
        # Removes the editing widgets
        for widget in self.editing_widgets:
            widget.grid_remove()

        # Redraws the detection widgets
        for widget in self.detection_widgets:
            widget.grid()

        for label in self.image_labels:
            label.unbind("<Button-1>")
            label.unbind("<ButtonRelease-1>")
            label.unbind("<BackSpace>")
            label.unbind("<Delete>")
            label.unbind("<Escape>")

        self.reset()
        self.calculate_hitboxes()

        print("\n" + 94 * "=" + "\n")
        print("Click 'Open one image' or 'Open two images' to choose new images.")
        print("Click one of the 'Detect ...' buttons to start detecting components.")
        print("When you're done, click 'Finish detection' to proceed.\n")


    # Deletes temporary files and closes the window
    def close_window(self):
        if messagebox.askokcancel("Quit", "Are you sure you want to quit?\nAll progress will be lost."):
            remove(self.options["path"])
            if len(self.classifiers) == 2:
                remove(self.options["path_2"])
            self.root.destroy()
            sys.stdout = self.prev_stdout


    # Saves the JSON file(s) and closes the window
    def save_and_exit(self):
        file_1 = self.options["servername"].split('/')[-1].split('.')[0] + ("_rear" if self.options["face"] == "rear" else "_front")

        if len(self.classifiers) == 2:
            file_2 = self.options["servername_2"].split('/')[-1].split('.')[0] + ("_front" if self.options["face_2"] == "front" else "_rear")
            if messagebox.askokcancel("Files saved", f"{file_1}.json and {file_2}.json files saved in '/api/'\n\nThank you for using OGrEE-Tools/3dtools!"):
                self.classifiers[0].savejson()
                self.classifiers[1].savejson()
                remove(self.options["path"])
                remove(self.options["path_2"])
                self.root.destroy()
                sys.stdout = self.prev_stdout
        else:
            if messagebox.askokcancel("File saved", f"{file_1}.json file saved in '/api/'\n\nThank you for using OGrEE-Tools/3dtools!"):
                self.classifiers[0].savejson()
                remove(self.options["path"])
                self.root.destroy()
                sys.stdout = self.prev_stdout


    # Creates the JSON window
    def create_json_window(self):
        # Removes editing widgets
        for widget in self.editing_widgets:
            widget.grid_remove()

        for label in self.image_labels:
            label.unbind("<Button-1>")
            label.unbind("<ButtonRelease-1>")
            label.unbind("<BackSpace>")
            label.unbind("<Delete>")
            label.unbind("<Escape>")

        # JSON text on top leftmost columns
        self.json_text = scrolledtext.ScrolledText(self.root, bg="black", fg="white", font=("Courier", 14), width=47, height=31)
        self.json_text.grid(columnspan=2, rowspan=5, column=0, row=3, pady=(20, 20))

        # Buttons on bottom leftmost columns
        self.return_to_editing_button = Button(self.root, text="Return to editing", command=self.return_to_editing, fg="black", height=4, width=40)
        self.return_to_editing_button.grid(columnspan=2, column=0, row=8)

        self.save_and_exit_button = Button(self.root, text="Save and exit", command=self.save_and_exit, fg="black", height=4, width=40)
        self.save_and_exit_button.grid(columnspan=2, column=0, row=9)

        self.json_widgets = [self.return_to_editing_button, self.save_and_exit_button, self.json_text]

        print("\n" + 94 * "=" + "\n")
        print("Click 'Return to editing' if you wish to edit another component.")
        print("Click 'Save and exit' to save the JSON file and exit.")

        self.classifiers[0].cutears()
        json_raw = f"{self.options['face'].title()} face:\n"
        json_raw += self.classifiers[0].writejson()

        if len(self.classifiers) == 2:
            self.classifiers[1].cutears()
            json_raw += "\n\n" + 47 * "=" + "\n\n" + f"{self.options['face_2'].title()} face:\n" + self.classifiers[1].writejson()

        self.reset()
        self.calculate_hitboxes()

        self.json_text.config(state=NORMAL)
        self.json_text.insert(END, json_raw)
        self.json_text.see(END)
        self.json_text.config(state=DISABLED)


    # Creates the editing window
    def create_editing_window(self):
        # Removes detection widgets
        for widget in self.detection_widgets:
            widget.grid_remove()

        # Component variables on top leftmost columns
        self.component_name_label = Label(self.root, text="Component name:", bg="white", fg="black", height=4)
        self.component_name_label.grid(column=0, row=3)

        self.component_name_entry = Entry(self.root, textvariable=self.component_name_var, bg="white", fg="black", width=14)
        self.component_name_entry.grid(column=1, row=3)

        self.component_type_label = Label(self.root, text="Component type:", bg="white", fg="black", height=4)
        self.component_type_label.grid(column=0, row=4)

        self.values = list(tools.SIZETABLE.keys())
        self.component_type_entry = ttk.Combobox(self.root, textvariable=self.component_type_var, values=self.values, background="white", foreground="black", width=13)
        self.component_type_entry.grid(column=1, row=4)
        self.component_type_entry.bind("<<ComboboxSelected>>", self.component_selected)

        self.component_depth_label = Label(self.root, text="Component depth (mm):", bg="white", fg="black", height=4)
        self.component_depth_label.grid(column=0, row=5)

        self.component_depth_entry = Entry(self.root, textvariable=self.component_depth_var, bg="white", fg="black", width=14)
        self.component_depth_entry.grid(column=1, row=5)

        self.component_wh_label_l = Label(self.root, text="Component width, height (mm):", bg="white", fg="black", height=4)
        self.component_wh_label_l.grid(column=0, row=6)

        self.component_wh_label_r = Label(self.root, textvariable=self.component_wh_var, anchor="w", bg="white", fg="black", height=4, width=14)
        self.component_wh_label_r.grid(column=1, row=6)

        # Buttons on bottom leftmost columns
        self.save_component_button = Button(self.root, text="Save component", command=self.save_component, fg="black", height=4, width=14)
        self.save_component_button.grid(column=0, row=7)

        self.delete_component_button = Button(self.root, text="Delete component", command=self.delete_component, fg="black", height=4, width=14)
        self.delete_component_button.grid(column=1, row=7)

        self.return_to_detection_button = Button(self.root, text="Return to detection", command=self.return_to_detection, fg="black", height=4, width=40)
        self.return_to_detection_button.grid(columnspan=2, column=0, row=8)

        self.finish_editing = Button(self.root, text="Finish editing", command=self.create_json_window, fg="black", height=4, width=40)
        self.finish_editing.grid(columnspan=2, column=0, row=9)

        self.editing_widgets = [self.component_name_label, self.component_name_entry, self.component_type_label, self.component_type_entry, self.component_depth_label, self.component_depth_entry, self.component_wh_label_l, self.component_wh_label_r, self.save_component_button, self.delete_component_button, self.return_to_detection_button, self.finish_editing]

        for label in self.image_labels:
            label.bind("<Button-1>", lambda event: self.click(event, str(event.widget).split(".")[-1]))
            label.bind("<ButtonRelease-1>", lambda event: self.release(event, str(event.widget).split(".")[-1]))
            label.bind("<BackSpace>", self.delete_component)
            label.bind("<Delete>", self.delete_component)
            label.bind("<Escape>", self.reset)

        self.reset()
        self.image_label_selected = "top"

        print("\n" + 94 * "=" + "\n")
        print("Click 'Return to detection' if you wish to automatically detect another component.")
        print("Click inside a rectangle on the image to select a component and edit its name, type and depth.")
        print("Click on the top left corner after selecting a component to adjust its position.")
        print("You can also draw a new rectangle to adjust its size. Press 'Esc' to unselect a component.")
        print("You can create a new component by drawing its rectangle or by placing it (if type selected).")
        print("Don't forget to enter a name, type and depth for the new component.")
        print("Use the buttons to save your changes or to delete a component after selecting it.")
        print("When you're done, click 'Finish editing' to proceed.")


    # Creates the detection window
    def create_detection_window(self):
        # Window
        self.root = Tk()
        self.root.title("OGrEE-Tools/3dtools")
        self.root.geometry("1280x720")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.close_window)
        self.root.createcommand("::tk::mac::Quit", self.close_window)
        self.root.bind('<Control-x>', self.close_window)

        # black header with white text
        self.header = Frame(self.root, width=1280, height=40, bg="black")
        self.header.grid(columnspan=5, rowspan=3, row=0, column=0)

        self.header_text = Label(self.root, text="OGrEE-Tools/3dtools", bg="black", fg="white", font=("Helvetica, 20"), justify="center")
        self.header_text.grid(columnspan=5, row=1)

        # Main content
        self.main_content = Frame(self.root, width=1280, height=680, bg="white")
        self.main_content.grid(columnspan=5, rowspan=7, row=3, column=0)

        # Buttons on two leftmost columns
        self.open_one_image_button = Button(self.root, text="Open one image\n(rear OR front)", command=self.open_one_image, fg="black", height=4, width=40)
        self.open_one_image_button.grid(columnspan=2, column=0, row=3)

        self.open_two_images_button = Button(self.root, text="Open two images\n(rear AND front)", command=self.open_two_images, fg="black", height=4, width=40)
        self.open_two_images_button.grid(columnspan=2, column=0, row=4)

        self.detect_all_button = Button(self.root, text="Detect all\n(slots + disks + PSU)", command=self.detect_all, fg="black", height=4, width=14)
        self.detect_all_button.grid(column=0, row=5)

        self.detect_slot_button = Button(self.root, text="Detect slots", command=self.detect_slot, fg="black", height=4, width=14)
        self.detect_slot_button.grid(column=1, row=5)

        self.detect_disk_button = Button(self.root, text="Detect disks", command=self.detect_disk, fg="black", height=4, width=14)
        self.detect_disk_button.grid(column=0, row=6)

        self.detect_psu_button = Button(self.root, text="Detect PSU", command=self.detect_psu, fg="black", height=4, width=14)
        self.detect_psu_button.grid(column=1, row=6)

        self.detect_serial_button = Button(self.root, text="Detect serial ports\n(DB9 connector)", command=self.detect_serial, fg="black", height=4, width=14)
        self.detect_serial_button.grid(column=0, row=7)

        self.detect_vga_button = Button(self.root, text="Detect VGA ports\n(DB15 connector)", command=self.detect_vga, fg="black", height=4, width=14)
        self.detect_vga_button.grid(column=1, row=7)

        self.detect_bmc_button = Button(self.root, text="Detect BMC", command=self.detect_bmc, fg="black", height=4, width=14)
        self.detect_bmc_button.grid(column=0, row=8)

        self.detect_usb_button = Button(self.root, text="Detect USB ports", command=self.detect_usb, fg="black", height=4, width=14)
        self.detect_usb_button.grid(column=1, row=8)

        self.create_editing_window_button = Button(self.root, text="Finish detection", command=self.create_editing_window, fg="black", height=4, width=40)
        self.create_editing_window_button.grid(columnspan=2, column=0, row=9)

        self.detection_widgets = [self.open_one_image_button, self.open_two_images_button, self.detect_all_button, self.detect_slot_button, self.detect_disk_button, self.detect_psu_button, self.detect_serial_button, self.detect_vga_button, self.detect_bmc_button, self.detect_usb_button, self.create_editing_window_button]

        # Output text on bottom rightmost columns
        self.output = scrolledtext.ScrolledText(self.root, bg="black", fg="white", font=("Courier", 14), width=94, height=19)
        self.output.grid(columnspan=3, rowspan=3, column=2, row=7)

        self.prev_stdout = sys.stdout
        sys.stdout = Stdout_to_window(self.output)

        print("\n" + 94 * "=" + "\n")
        print("Welcome to OGrEE-Tools/3dtools!")
        print("Click 'Open one image' or 'Open two images' to choose new images.")
        print("Click one of the 'Detect ...' buttons to start detecting components.")
        print("When you're done, click 'Finish detection' to proceed.\n")
        print(94 * "=" + "\n")

        # Images on top rightmost columns
        self.top_image_label = Label(self.root, name="top")
        self.top_image_label.grid(columnspan=3, rowspan=2, column=2, row=4, padx=(20, 20), pady=(20, 20))

        self.bot_image_label = Label(self.root, name="bot")
        # bot_image_label.grid(columnspan=3, rowspan=2, column=2, row=5, padx=(20, 20), pady=(20, 20))

        self.image_labels = [self.top_image_label, self.bot_image_label]
        self.image_label_selected = "top"

        imsave(self.options["path"], tools.scaleim(self.options["servername"], self.options["height"], 2.0))
        self.update_images()

        self.component_name_var = StringVar(self.root)
        self.component_type_var = StringVar(self.root)
        self.component_depth_var = StringVar(self.root)
        self.component_wh_var = StringVar(self.root)
        self.click_pt1 = None
        self.selected_component = None
        self.hitboxes = [{}, {}]

        self.root.after(100, lambda:print(f"\nNew image opened: {self.options['servername'].split('/')[-1]}."))


    # Starts the GUI
    def __init__(self, options):
        self.FILE = Path(__file__).resolve()
        self.ROOT = self.FILE.parents[0]
        self.yROOT = self.ROOT / 'yolov5'  # YOLOv5 root directory
        # '''
        # if str(self.ROOT) not in sys.path:
        #     sys.path.append(str(self.ROOT))  # add ROOT to PATH
        # self.ROOT = Path(os.path.relpath(self.ROOT, Path.cwd()))  # relative
        # '''

        self.options = options
        self.options["path"] = 'api/tmp' + self.options["servername"].split('/')[-1]
        self.options["data"] =self.ROOT / 'yolov5/data/serveur122.yaml'
        self.options["imgsz"] = (192, 768)
        self.options["max_det"] = 400
        self.options["agnostic_nms"] = False
        self.options["update"] = False
        self.options["half"] = False
        self.options["dnn"] = False
        self.options["vid_stride"] = 1

        self.create_detection_window()
        self.classifiers = [Classifiers(self.options["servername"], self.options["height"], self.options["width"], self.options["face"])]


# Creates and runs the GUI
def run_gui(opt):
    gui = Gui(vars(opt))
    mainloop()
