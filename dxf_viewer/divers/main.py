# -*- coding: utf-8 -*-
import os
import ezdxf
import sys
import numpy as np
from rdp import rdp
import pprint as pp
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import mplcursors

np.set_printoptions(precision=3, suppress=True)

def print_entity(e):
    print("LINE on layer: %s\n" % e.dxf.layer)
    print("start point: %s\n" % e.dxf.start)
    print("end point: %s\n" % e.dxf.end)

def print_entity2(e):
    print(e.dxf.layer, e.dxf.start, e.dxf.end )

def transform(vertices, new_center, axis1, axis2):
    mat = np.linalg.inv(np.array([axis1, axis2])) @ np.array([[1, 0], [0, 1]])
    transformed_vertices = (vertices - new_center) @ mat
    return transformed_vertices

def transform_single_axis(vertices, new_center, axis1, direct):
    if direct:
        axis2 = np.array([-axis1[1], axis1[0]])
    else:
        axis2 = np.array([axis1[1]], -axis1[0])
    return transform(vertices, new_center, axis1, axis2)
    
point1 = None
point2 = None
def on_click(event):
    global point1, point2

    if event.button == 1:  # Clic gauche
        if point1 is None:
            point1 = (event.xdata, event.ydata)
            print("Point 1 sélectionné :", point1)
        elif point2 is None:
            point2 = (event.xdata, event.ydata)
            print("Point 2 sélectionné :", point2)
            compute_distance()
            # Réinitialiser les points sélectionnés pour permettre de mesurer une nouvelle distance
            point1 = None
            point2 = None


def compute_distance():
    global point1, point2

    if point1 is not None and point2 is not None:
        distance = ((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2) ** 0.5
        print("Distance entre les deux points :", distance)



def plot(l, fig=True):
    

    if fig:
        fig, ax = plt.subplots()

    mplcursors.cursor(hover=True)
    cid = fig.canvas.mpl_connect('button_press_event', on_click)
    ax.plot(list(l[:, 0]) + [l[0, 0]], list(l[:, 1]) + [l[0, 1]])
    for i, vertice in enumerate(l):
        ax.annotate(str(i), vertice)
    plt.axis('equal')

def perp(a) :
    b = np.empty_like(a)
    b[0] = -a[1]
    b[1] = a[0]
    return b

def seg_intersect(a1, a2, b1, b2) :
    da = a2-a1
    db = b2-b1
    dp = a1-b1
    dap = perp(da)
    denom = np.dot( dap, db)
    num = np.dot( dap, dp )
    return (num / denom.astype(float))*db + b1

def envelope(polygon, dist):
    shifted_segments = []
    for i in range(len(polygon)):
        a, b = polygon[i], polygon[(i+1)%len(polygon)]
        dx = b[0] - a[0]
        dy = b[1] - a[1]
        normal = np.array([dy, -dx])
        normal /= np.linalg.norm(normal)
        shifted_segments.append((a + dist*normal, b + dist*normal))
    new_polygon = []
    for i in range(len(shifted_segments)):
        seg1 = shifted_segments[(i-1)%len(shifted_segments)]
        seg2 = shifted_segments[i]
        new_polygon.append(seg_intersect(seg1[0], seg1[1], seg2[0], seg2[1]))
    return np.array(new_polygon)

def get_circle(x, y, z):
    x, y, z = x[0]+x[1]*1j, y[0]+y[1]*1j, z[0]+z[1]*1j
    w = (z-x) / (y-x)
    c = (x-y)*(w-abs(w)**2)/2j/w.imag-x
    return -c.real, -c.imag, abs(c+x)

def array2dict(lst):
    res_dict = {}
    for i in range(0, len(lst), 1):
        res_dict[i] = lst[i]
    return res_dict

doc = ezdxf.readfile("../mgf.dxf")
msp = doc.modelspace()

object_type = set()

group = msp.groupby(dxfattrib="layer")
a = defaultdict(lambda: defaultdict(lambda: 0))

for layer, entities in group.items():
    for entity in entities:
        object_type.add(entity.dxftype())
        a[layer][entity.dxftype()] += 1
a = {k: dict(a[k]) for k in a}
# pp.pprint(a)

# print(object_type)

lines = []
all_vertices = []
layer='05-Bâti_contour'



for polyline in msp.query(f'LWPOLYLINE[layer=="{layer}"]'):
  line = []
  for vertice in polyline:
    line.append([vertice[0], vertice[1]])
    all_vertices.append([vertice[0], vertice[1]])
  
  line = np.array(line)


  lines.append(line)






plot(lines[0])

# # NORMALIZE POLYLINE + new center + new axis
# line = lines[0]
# #new_center = (line[22] + line[31])/2
# new_center = (line[9] + line[7])/2
# new_center = seg_intersect(line[7],line[9], line[13],line[11])

# #axis1 = line[31] - line[22]
# axis1 = line[7] - line[9]
# axis1 /= np.linalg.norm(axis1)
# new_line = transform_single_axis(line, new_center, axis1, True)
# print(new_line)


# plot(new_line)

# #
# # Reduce Points
# #
# simple_line = rdp(new_line, epsilon=0.2)
# print(len(new_line), len(simple_line))


# plot(simple_line)

# # convert Array into Dict
# dict_line = array2dict(simple_line)
# pp.pprint(dict_line)

# int_line = envelope(simple_line, 2.)


# plot(simple_line, False)

# #plot(int_line, False)
# lengths = []
# for i in range(len(simple_line)):
#     a, b = simple_line[i], simple_line[(i+1)%len(simple_line)]
#     dx, dy = b[0]-a[0], b[1]-a[1]
#     normal = np.array([dy, -dx])
#     normal /= np.linalg.norm(normal)
#     length = np.linalg.norm(a - b)
#     lengths.append(length)
#     if length > 5:
#         plt.annotate("%.2f" % length, (a+b)/2 - 3.*normal - 1., color='red')
# print(np.array(lengths))

# #centerx, centery, radius = get_circle(new_line[7], new_line[50], new_line[45])
# centerx, centery, radius = get_circle(new_line[16], new_line[18], new_line[21])
# print(centerx, centery, radius)

plt.show()

