from skimage.feature import CENSURE,plot_matches,match_descriptors
from skimage.color.colorconv import rgba2rgb, rgb2hsv, rgb2gray, hsv2rgb
import matplotlib.pyplot as plt
import numpy as np
from skimage.io import imshow,imread,imsave
from skimage import filters
from skimage import exposure
from skimage.transform import resize
import tools
import matplotlib.pyplot as plt
'''
mask = tools.imageload('mask.png','grey')
mask = mask>0.5


#FILEHANDEL = "rs232/d9"
FILEHANDEL = "vga/vga"
SAVEHANDEL = "image/result/"
QUANTITY = 12
detector = CENSURE(min_scale=1, max_scale=7, mode='DoB', non_max_threshold=0.15, line_threshold=10)
#(min_scale=1, max_scale=7, mode='DoB', non_max_threshold=0.15, line_threshold=10)

for i in range(1,QUANTITY+1):

    path = FILEHANDEL + '{}'.format(str(i).zfill(3)) + '.png'
    img_orig = tools.imageload(path,'grey')
    img_orig = resize(img_orig, (109,289))
    #img_orig = exposure.equalize_hist(img_orig)
    img_vag = filters.gaussian(img_orig * mask,sigma=1)
    img_inv = -img_vag + 1

    detector.detect(img_vag)
    #detector.detect(img_inv)

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
'''


mask = tools.imageload('standard/mask.png','grey')
mask = mask>0.5
detector = CENSURE(min_scale=1, max_scale=7, mode='DoB', non_max_threshold=0.15, line_threshold=10)
path = 'standard/standard-vga.png'
img_std = tools.imageload(path, 'grey')
img_std = resize(img_std, (105, 290))
# img_orig = exposure.equalize_hist(img_orig)
img_std = filters.gaussian(img_std * mask, sigma=1.25)
img_istd = -img_std + 1

detector.detect(img_std)
keypoints_std = detector.keypoints

path = 'vga/vga001.png'
img = tools.imageload(path, 'grey')
img = resize(img, (105, 290))
# img_orig = exposure.equalize_hist(img_orig)
img = filters.gaussian(img * mask, sigma=1.25)
img_i = -img + 1

detector.detect(img)
keypoints_img = detector.keypoints

matches = match_descriptors(keypoints_std, keypoints_img, metric=None, p=2, cross_check=False)
#detector.detect(img_inv)

# Visualize the results.

fig, ax = plt.subplots(nrows=1, ncols=1)

plt.gray()

plot_matches(ax, img, img_std, keypoints_img, keypoints_std,matches,only_matches=False,alignment='vertical')
ax.axis("off")
ax.set_title("Inlier correspondences")
plt.show()


