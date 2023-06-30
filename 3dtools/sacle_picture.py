import numpy as np
import pandas as pd
import os
import tools
from skimage.io import imsave
from skimage.transform import rescale

FILEHANDEL = "YOLO_serveur/raw/"
SAVEHANDEL = "D:/Work/OGREE/image/YOLO_serveur/pixel2.5/"
RATIO = 2.0

size = pd.read_excel("image/name_list.xlsx").set_index('File')
files = os.listdir("image/"+FILEHANDEL)
for i in files:
    image = tools.imageload(FILEHANDEL+i, flag="color")
    image_s = rescale(image, size.loc[i, 'Height'] * RATIO / image.shape[0],channel_axis=2)
    image_s = (image_s * 255.0).astype('uint8')
    path = SAVEHANDEL + i
    imsave(path, image_s)

