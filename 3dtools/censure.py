from skimage.feature import CENSURE
from skimage.color.colorconv import rgba2rgb, rgb2hsv, rgb2gray, hsv2rgb
import matplotlib.pyplot as plt
import numpy as np
from skimage.io import imshow,imread,imsave
from skimage import filters
from skimage import exposure
from skimage.transform import resize
import tools
import matplotlib.pyplot as plt
mask = tools.imageload('mask.png','grey')
mask = mask>0.5


FILEHANDEL = "rs232/d9"
#FILEHANDEL = "vga/vga"
SAVEHANDEL = "image/result/"
QUANTITY = 10
detector = CENSURE(min_scale=1, max_scale=7, mode='DoB', non_max_threshold=0.15, line_threshold=10)
#(min_scale=1, max_scale=7, mode='DoB', non_max_threshold=0.15, line_threshold=10)

for i in range(1,QUANTITY+1):

    path = FILEHANDEL + '{}'.format(str(i).zfill(3)) + '.png'
    img_orig = tools.imageload(path,'grey')
    #img_orig = exposure.equalize_hist(img_orig)
    mask = resize(mask, img_orig.shape)
    img_vag = filters.gaussian(img_orig * mask,sigma=1)
    img_inv = -(img_vag )+1
    #detector.detect(img_vag)
    detector.detect(img_inv)
    #dst = (dst * 255.0).astype('uint8')
    #imsave(SAVEHANDEL + '{}'.format(str(i).zfill(3)) + '.png', img_orig)
    plt.figure(linewidth=4)
    ax = plt.gca()
    ax.imshow(img_vag, cmap=plt.cm.gray)

    ax.scatter(detector.keypoints[:, 1], detector.keypoints[:, 0],
                  2 ** detector.scales, facecolors='none', edgecolors='r')
    ax.axis('off')
    path = SAVEHANDEL + '{}'.format(str(i).zfill(3)) + '.png'
    plt.savefig(path)

#ax.set_facecolor('lightgreen') # 设置视图背景颜⾊

# 2、图例
#plt.legend(['Sin','Cos'],fontsize = 18,loc = 'center',ncol = 2,bbox_to_anchor =[0,1.05,1,0.2])
# plt.tight_layout() # ⾃动调整布局空间，就不会出现图⽚保存不完整


