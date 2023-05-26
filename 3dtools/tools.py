from skimage.color.colorconv import rgba2rgb, rgb2hsv, rgb2gray, hsv2rgb
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
from skimage.io import imshow, imread
from mpl_toolkits.mplot3d import Axes3D
from skimage.feature import match_template,peak_local_max,match_descriptors
from skimage.feature import canny
from skimage import filters
from skimage import exposure
from skimage.transform import rescale,rotate
from skimage.transform import probabilistic_hough_line
from itertools import combinations
import math

RATIO = 781/85.4  # pixel/mm = 9.145

def imageload(f,flag="color"):
    if flag == "color":
        flag = 0
    elif flag == "grey":
        flag = 1
    else:
        flag = 0
    fn = "image/" + f
    if flag == 1:
        img = imread(fn, 1)  # (H x W x C), [0, 255], RGB
    else:
        tmp = imread(fn)    # (H x W x C), [0, 255], RGB
        if tmp.shape[-1] == 4:
            img = rgba2rgb(tmp)
            print("4 channels picture  ",f)
        else:
            pass


    '''
    plt.figure("hist", figsize=(8, 8))
    arr = img.flatten()
    plt.subplot(411)
    plt.imshow(img, plt.cm.gray)  # 原始图像
    plt.subplot(412)
    plt.hist(arr, bins=256, edgecolor='None', facecolor='red')  # 原始图像直方图

    arr1 = img1.flatten()
    plt.subplot(413)
    plt.imshow(img1, plt.cm.gray)  # 均衡化图像
    plt.subplot(414)
    plt.hist(arr1, bins=256, edgecolor='None', facecolor='red')  # 均衡化直方图

    plt.show()
    '''
    return img

def impreprocess(image):
    image[:, :, 0] = exposure.equalize_hist(image[:, :, 0])
    image[:, :, 1] = exposure.equalize_hist(image[:, :, 1])
    image[:, :, 2] = exposure.equalize_hist(image[:, :, 2])
    return image

def rgbview(image):
    if image.shape[-1] == 3:
        image_g = rgb2gray(image)
        image_e = filters.sobel(image_g)

        fig, ax = plt.subplots(3, 1, figsize=(20, 8))
        ax[0].imshow(image, cmap='gray')
        ax[1].imshow(image_g, cmap='gray')
        ax[2].imshow(image_e, cmap='gray')
        ax[0].set_title('Colored Image', fontsize=15)
        ax[1].set_title('Grayscale Image', fontsize=15)
        ax[2].set_title('Sobel edge', fontsize=15)
        plt.show()
    elif image.shape[-1] == 1:
        image_e = filters.sobel(image)
        fig, ax = plt.subplots(2, 1, figsize=(20, 8))
        ax[0].imshow(image, cmap='gray')
        ax[1].imshow(image_e, cmap='gray')
        ax[0].set_title('Colored Image', fontsize=15)
        ax[1].set_title('Grayscale Image', fontsize=15)
        plt.show()

def hsvview(image):
    if image.shape[-1] == 3:
        image_rgb = hsv2rgb(image)
        image_e = filters.sobel(image[:,:,2])
        fig, ax = plt.subplots(5, 1, figsize=(20, 8))
        ax[0].imshow(image[:,:,0],cmap='gray')
        ax[1].imshow(image[:,:,1],cmap='gray')
        ax[2].imshow(image[:,:,2],cmap='gray')
        ax[3].imshow(image_rgb)
        ax[4].imshow(image_e, cmap='gray')
        ax[0].set_title('Colored Image', fontsize=15)
        ax[1].set_title('Grayscale Image', fontsize=15)
        ax[2].set_title('Sobel edge', fontsize=15)
        plt.show()
    elif image.shape[-1] == 1:
        image_e = filters.sobel(image)
        fig, ax = plt.subplots(2, 1, figsize=(20, 8))
        ax[0].imshow(image, cmap='gray')
        ax[1].imshow(image_e, cmap='gray')
        ax[0].set_title('Colored Image', fontsize=15)
        ax[1].set_title('Grayscale Image', fontsize=15)
        plt.show()

def normaliseimage(image, x,y):
    image = rescale(image,x*RATIO/image.shape[0])
    return image

def imfeature(image,detector):
    img_vag = filters.gaussian(image, sigma=1)
    img_inv = -img_vag + 1
    detector.detect(img_vag)
    f_dark = detector.keypoints if len(detector.keypoints) > 0 else np.array([[0,0]])  # à améliorer
    detector.detect(img_inv)
    f_light = detector.keypoints if len(detector.keypoints) > 0 else np.array([[0,0]])
    return f_dark,f_light

def patchsimilarity(pfeature,std):
    if pfeature[0,0]==0 or pfeature[0,1]==0:
        pfeature = np.ones(std.shape)
    elif pfeature.shape[0] < std.shape[0]:
        penalty = std.shape[0]-pfeature.shape[0]
        pfeature = np.vstack((pfeature,np.ones([penalty,2])))
    elif pfeature.shape[0] > std.shape[0]:
        penalty = pfeature.shape[0]-std.shape[0]
        pfeature = pfeature[:std.shape[0],:]
    px = pfeature / np.array([np.sum(pfeature[:,0]),np.sum(pfeature[:,1])])
    pstd = std / np.array([np.sum(std[:, 0]), np.sum(std[:, 1])])
    re = -np.sum(px * np.log(px / pstd))
    return re

# Pour Gaussian similarity
class Pin:
    def proba(self,x,y):
        return self.pin_simi(x,y)
    def __init__(self,x_center,y_center):
        SIGMA = 10.0
        self.x_center = x_center
        self.y_center = y_center
        coeff = 1 / (2 * np.pi * np.square(SIGMA))
        self.pin_simi = lambda x,y: coeff * np.exp(-0.5*(np.square(x-x_center)/SIGMA**2+np.square(y-y_center)/SIGMA**2))

def gaussiansimilarity(pfeature,std):
    re = 0
    for i in range(pfeature.shape[0]):  # à améliorer l'efficacité
        re += sum([p.proba(pfeature[i,0], pfeature[i,1]) for p in std])
    return re
'''
match = match_descriptors(pfeature, std_pattern, metric=None, p=2, cross_check=False)
distance = -10*(std_pattern.shape[0]-match.shape[0])
for i,j in match:
    distance += -np.linalg.norm(pfeature[i]-std_pattern[j])
distance = distance- 10 * abs(pfeature.shape[0] - std_pattern.shape[0])
return distance
'''

def imedge(image):  #####################################################
    return filters.sobel(image)

# K-L entropy
def klentropy(x,std):
    if x.shape[0] < std.shape[0]:
        penalty = std.shape[0]-x.shape[0]
        x = np.vstack(x,x[:penalty,:])
    elif x.shape[0] > std.shape[0]:
        penalty = x.shape[0]-std.shape[0]
        x = x[:std.shape[0],:]
    px = x / np.array([np.sum(x[:,0]),np.sum(x[:,1])])
    pstd = std / np.array([np.sum(std[:, 0]), np.sum(std[:, 1])])
    return -np.sum(px * np.log(px / pstd))

# for power block
def findRectangle(image_g, length, height, line_gap=10):
    rectangles = []
    edge = canny(image_g, 1)
    # find straight vertical lines that in the image
    angle = np.array([0.0])
    ###image, threshold=10, line_length=50, line_gap=10, theta=None, seed=None
    lines = {a:abs(a[0][1] - a[1][1]) for a in probabilistic_hough_line(
                edge, threshold=10, line_length=int(height * 0.9),line_gap=line_gap, theta=angle) if abs(a[0][1] - a[1][1]) < int(height * 1.1)}
    # compare each pairs to find out rectangle
    # Parallelogram
    DEVIATION = 45.3  # pixels. i.e.5mm
    for (p1, p2), (p3, p4) in combinations(lines, 2):
        # p1--------p4  x
        # |          |
        # p2--------p3
        # y
        # (x,y)

        # make points in order
        if p1[1] > p2[1]:
            p1, p2 = p2, p1
        if p4[1] > p3[1]:
            p3, p4 = p4, p3
        if p4[1] < p1[1]:
            p1, p4 = p4, p1
            p2, p3 = p3, p2
        l1 = p2[1] - p1[1]
        l2 = p3[1] - p4[1]
        # Parallelogram
        if abs(l1 - l2) < DEVIATION:
            # rectangle within length
            if abs(p4[0] - p3[0]) < DEVIATION:
                if abs(abs(p3[0] - p2[0]) - length) < DEVIATION:
                    rectangles.append((p1,p2,p3,p4))
    return rectangles

def inRectangle(point, p):
    p1,p2,p3,p4 = p[0],p[1],p[2],p[3]
    rectvect = np.array([(p2[0] - p1[0], p2[1] - p1[1]),
                         (p3[0] - p2[0], p3[1] - p2[1]),
                         (p4[0] - p3[0], p4[1] - p3[1]),
                         (p1[0] - p4[0], p1[1] - p4[1])])
    pointvect = np.array([(point[0] - p1[0], point[1] - p1[1]),
                          (point[0] - p2[0], point[1] - p2[1]),
                          (point[0] - p3[0], point[1] - p3[1]),
                          (point[0] - p4[0], point[1] - p4[1])])
    flag = [np.sign(np.cross(pointvect[i, :], rectvect[i, :])) for i in range(4)]
    if flag[0] == flag[1] and flag[1] == flag[2] and flag[2] == flag[3]:
        return 1
    return 0


def templateMatch(image,template,threshold,mindis):
    image_e = filters.sobel(image)
    fig, ax = plt.subplots(2, 1, figsize=(10, 8))
    ax[0].imshow(image, cmap='gray')
    positions = []
    for _ in range(4):
        template = rotate(template, 90, resize=True)
        sample_mt = match_template(image_e, template)
        template_width, template_height = template.shape
        positions.append(peak_local_max(np.squeeze(sample_mt), threshold_abs=threshold,min_distance=mindis) ) ######### to be complete for angles
    for x, y in positions[1]:   ######### to be complet
        rect = plt.Rectangle((y, x), template_height, template_width, color='r',
                             fc='none')
        ax[0].add_patch(rect)
    ax[1].imshow(sample_mt, cmap='magma')
    ax[0].set_title('Grayscale', fontsize=15)
    ax[1].set_title('Template Matching', fontsize=15)
    plt.show()
    return positions[1]   ##### tobe complet

def pixel2mm(coordonne):
    return coordonne/