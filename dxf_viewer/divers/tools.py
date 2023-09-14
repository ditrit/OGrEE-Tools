import numpy as np
import time
from tkinter import *

def transform(vertices, new_center, axis1, axis2):
    mat = np.linalg.inv(np.array([axis1, axis2])) @ np.array([[1, 0], [0, 1]])
    transformed_vertices = (vertices - new_center) @ mat
    return transformed_vertices

def transform_single_axis(vertices, new_center, axis1, direct):
    if direct:
        axis2 = np.array([-axis1[1], axis1[0]])
    else:
        axis2 = np.array([axis1[1]], -axis1[0])
    return transform(vertices, new_center, -axis1, axis2)


class ZoomPan:
    def __init__(self):
        self.press = None
        self.cur_xlim = None
        self.cur_ylim = None
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        self.xpress = None
        self.ypress = None

    def zoom_factory(self, ax, base_scale=1.25):
        def zoom(event):
            cur_xlim = ax.get_xlim()
            cur_ylim = ax.get_ylim()
            xdata = event.xdata
            ydata = event.ydata
            if event.button == 'up':
                scale_factor = 1 / base_scale
            elif event.button == 'down':
                scale_factor = base_scale
            else:
                scale_factor = 1
            try:
                new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
                new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor
                relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
                rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])
                ax.set_xlim([xdata - new_width * (1 - relx), xdata + new_width * relx])
                ax.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * rely])
                ax.figure.canvas.draw()
            except :
                pass

        def pan(event):
            if event.button == 2:
                if self.press is None:
                    self.press = event.x, event.y, ax.get_xlim(), ax.get_ylim()
                else:
                    dx = event.x - self.press[0]
                    dy = event.y - self.press[1]
                    ax.set_xlim([self.press[2][0] - dx, self.press[2][1] - dx])
                    ax.set_ylim([self.press[3][0] - dy, self.press[3][1] - dy])
                    ax.figure.canvas.draw()

        def release(event):
            if event.button == 2:
                self.press = None
                
        fig = ax.get_figure()
        fig.canvas.mpl_connect('scroll_event', zoom)
        fig.canvas.mpl_connect('button_press_event', pan)
        fig.canvas.mpl_connect('button_release_event', release)

        return zoom, pan, release



def cap_frequency(max_calls_per_second):
    min_interval = 1.0 / max_calls_per_second
    last_call_time = 0.0

    def decorator(func):
        def wrapper(*args, **kwargs):
            nonlocal last_call_time
            current_time = time.time()
            elapsed_time = current_time - last_call_time
            if elapsed_time >= min_interval:
                result = func(*args, **kwargs)
                last_call_time = current_time
                return result
        return wrapper

    return decorator


class ToolTip(object):

    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 30
        y = y + cy + self.widget.winfo_rooty() + 30
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(tw, text=self.text, justify=LEFT,
                      background="#ffffe0", relief=SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def CreateToolTip(widget, text):
    toolTip = ToolTip(widget)
    def enter(event):
        toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)

def generate_json(name,points):
    points = list(points[0])
    json_response = {"points":[]}
    for i in points:
        json_response["points"].append(list(i))
    return str(json_response)

def get_file_name(file_path):
    file_path_components = file_path.split('/')
    file_name_and_extension = file_path_components[-1].rsplit('.', 1)
    return file_name_and_extension[0]