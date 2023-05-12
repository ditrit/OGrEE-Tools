from skimage.color.colorconv import rgba2rgb, rgb2hsv, rgb2gray, hsv2rgb
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
from skimage.io import imshow, imread
from mpl_toolkits.mplot3d import Axes3D
from skimage.feature import match_template,peak_local_max,match_descriptors
from skimage import filters
from skimage import exposure
from skimage.transform import rescale,rotate



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
def greenwill(image):
    plt.imshow(image, cmap='gray')
    plt.axis('off')
    plt.colorbar()
    plt.show()

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
    ratio = 781/85.4  # pixel/mm
    image = rescale(image,x*ratio/image.shape[0])
    return image

def imfeature(image,detector):
    img_vag = filters.gaussian(image, sigma=1)
    img_inv = -img_vag + 1

    detector.detect(img_vag)
    f_dark = detector.keypoints if len(detector.keypoints) > 0 else np.array([[0,0]])  # à améliorer
    detector.detect(img_inv)
    f_light = detector.keypoints if len(detector.keypoints) > 0 else np.array([[0,0]])
    return f_dark,f_light

def patchsimilarity(pfeature,std_pattern):
    match = match_descriptors(pfeature, std_pattern, metric=None, p=2, cross_check=False)
    distance = -10*(std_pattern.shape[0]-match.shape[0])
    for i,j in match:
        distance += -np.linalg.norm(pfeature[i]-std_pattern[j])

    return distance

def imedge(image):
    return filters.sobel(image)

def templateMatch(image,template,threshold,mindis):
    image_e = filters.sobel(image)
    fig, ax = plt.subplots(2, 1, figsize=(10, 8))
    ax[0].imshow(image, cmap='gray')
    for _ in range(4):
        template = rotate(template, 90, resize=True)
        sample_mt = match_template(image_e, template)
        template_width, template_height = template.shape
        for x, y in peak_local_max(np.squeeze(sample_mt), threshold_abs=threshold,min_distance=mindis):
            rect = plt.Rectangle((y, x), template_height, template_width, color='r',
                                 fc='none')
            ax[0].add_patch(rect)
    ax[1].imshow(sample_mt, cmap='magma')
    ax[0].set_title('Grayscale', fontsize=15)
    ax[1].set_title('Template Matching', fontsize=15)
    plt.show()