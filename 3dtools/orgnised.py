from skimage.color.colorconv import rgba2rgb
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import numpy as np
from skimage.io import imshow, imread
from skimage.color import rgb2gray,rgba2rgb
from mpl_toolkits.mplot3d import Axes3D
from skimage.feature import match_template
from skimage.feature import peak_local_max
from skimage import data, io, filters, transform

def templateMatch(image,template):
  fig, ax = plt.subplots(2,1,figsize=(10,8))
  ax[0].imshow(image_g,cmap='gray')
  for _ in range(4):
    template = transform.rotate(template,90,resize=True)
    sample_mt = match_template(image, template)
    template_width, template_height = template.shape
    for x, y in peak_local_max(np.squeeze(sample_mt), threshold_abs=0.7):
      rect = plt.Rectangle((y, x), template_height, template_width, color='r',
                            fc='none')
      ax[0].add_patch(rect)
  ax[1].imshow(sample_mt,cmap='magma')
  ax[0].set_title('Grayscale',fontsize=15)
  ax[1].set_title('Template Matching',fontsize=15)
  plt.show()


image = rgba2rgb(imread('image/dell-poweredge-r740xd.rear.png'))           # (H x W x C), [0, 255], RGB
image_g = rgb2gray(image)
image_e = filters.sobel(image_g)
image_hsv = rgb2hsv
'''
fig, ax = plt.subplots(3,1,figsize=(10,8))
ax[0].imshow(image)
ax[1].imshow(image_g,cmap='gray')
ax[2].imshow(image_e,cmap='gray')
ax[0].set_title('Colored Image',fontsize=15)
ax[1].set_title('Grayscale Image',fontsize=15)
ax[2].set_title('Sobel edge',fontsize=15)
plt.show()
plt.close(fig)
'''
template = rgba2rgb(imread('image/rj45-90.png'))
template_g = rgb2gray(template)
template_e = filters.sobel(template_g)

templateMatch(image_e,template_e)