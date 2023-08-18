from skimage.color.colorconv import rgba2rgb, rgb2hsv, rgb2gray, hsv2rgb
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
from skimage.io import imread, imsave
from skimage.feature import match_template, peak_local_max
from skimage.feature import canny
from skimage import filters
from skimage import exposure
from skimage.transform import rescale, rotate
from skimage.transform import probabilistic_hough_line
from itertools import combinations
import torch
import json
# Functions for hierarchical clustering
from scipy.cluster.hierarchy import linkage
from scipy.cluster.hierarchy import fcluster
import multiprocessing
import sys

# special constant for all the function
RATIO = 781/85.4  # pixel/mm = 9.145
SIZETABLE = {'idrac': [14.0, 11.0, 11.0], 'usb': [13.0, 14.0, 5.5], 'vga': [16.0, 11.0, 8.0],
             'rs232': [16.0, 11.0, 8.0], 'slot_normal': [107.0, 312.0, 18.0], 'slot_lp': [65.0, 175.0, 18.0],
             'disk_lff': [101.0, 146.0, 26.0], 'disk_sff': [70.0, 101.0, 10.0], 'PSU': [90.0, 100.0, 40.0]}


def imageload(f, flag="color"):
    """
    Load image from file

    Args:
        f: file path under file "image"
        flag: "color" or grey

    Returns:
        image in ndarray(x,y)   when flag is 'grey'
        image in ndarray(x,y,3) when flag is 'color'
    """
    if flag == "color":
        flag = 0
    elif flag == "grey":
        flag = 1
    else:
        flag = 0
    fn = "image/" + f
    if flag == 1:
        img = imread(fn, 1)  # (H x W), [0, 255]
        print("3 channels RGB picture   ", f)
    else:
        img = imread(fn)    # (H x W x C), [0, 255], RGB
        if img.shape[-1] == 4:
            img = rgba2rgb(img)
            print("4 channels RGBS picture  ", f)
        else:
            pass
    return img


def preprocess(image: np.ndarray):
    """
    Adjust color balance. Will improve picture too bright or too dark
    No use now

    Args:
        image: x-coordinate(s) as a numpy array or scalar.

    Returns:
        ndarray type 3 channels image.
    """
    image[:, :, 0] = exposure.equalize_hist(image[:, :, 0])
    image[:, :, 1] = exposure.equalize_hist(image[:, :, 1])
    image[:, :, 2] = exposure.equalize_hist(image[:, :, 2])
    return image


def scaleim(slotname, height, ratio):
    """
    Scale image to the sample ratio in pixels

    Args:
        slotname: File handle of server
        height: slot height in mm
        ratio: number of pixels per mm

    Returns:
        ndarray type 3 channels image.
    """
    image = imageload(slotname, flag="color")
    image_s = rescale(image, height * ratio / image.shape[0], channel_axis=2)
    image_s = (image_s * 255.0).astype('uint8')
    return image_s


def rgbview(image: np.ndarray):
    """
    Show a rgb image on the screen, grey or color

    Args:
        image: a 2d ndarray(x,y) grey image, or 3d  ndarray(x,y,3) grey image

    Returns:
        plot objet displaying the image on the screen
    """
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
    elif len(image.shape) == 2:
        image_e = filters.sobel(image)
        fig, ax = plt.subplots(2, 1, figsize=(20, 8))
        ax[0].imshow(image, cmap='gray')
        ax[1].imshow(image_e, cmap='gray')
        ax[0].set_title('Colored Image', fontsize=15)
        ax[1].set_title('Grayscale Image', fontsize=15)
        plt.show()


def hsvview(image):
    """
    Show a hsv image on the screen, grey or color

    Args:
        image: a 2d ndarray(x,y) grey image, or 3d  ndarray(x,y,3) color image

    Returns:
        plot objet displaying the image on the screen
    """
    if image.shape[-1] == 3:
        image_rgb = hsv2rgb(image)
        image_e = filters.sobel(image[:, :, 2])
        fig, ax = plt.subplots(5, 1, figsize=(20, 8))
        ax[0].imshow(image[:, :, 0], cmap='gray')
        ax[1].imshow(image[:, :, 1], cmap='gray')
        ax[2].imshow(image[:, :, 2], cmap='gray')
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


def normaliseimage(image, shapemm):
    """
    Transform the size of the image under the same ratio

    Args:
        image: a 2d ndarray(x,y) grey image
        shapemm: the shape of the server in realty. Unit is measured in mm

    Returns:
        grey image in ndarray(x',y') with new and standard sample
    """
    # ------------  y
    # |          |
    # ------------
    # x
    # (x,y)
    image = rescale(image, shapemm[0]*RATIO/image.shape[0])
    return image


def imfeature(image, mask, detector):
    """
    Compute the feature point of image.

    Args:
        image: image of the server, back or face.
        mask: a black coverage that cover the extraneous images in view (e.g. screws, labels)
        detector: CENSURE class object predefined

    Returns:
        [n,2] ndarray of features' coordinates
    """
    def deloutfeature(feature, m):
        # delete features outside the mask
        idx = []
        for k in range(feature.shape[0]):
            if not m[feature[k, 0], feature[k, 1]]:
                idx.append(k)
        return np.delete(feature, idx, 0)
    image = image * mask
    img_vag = filters.gaussian(image, sigma=1)
    img_inv = -img_vag + 1
    detector.detect(img_vag)
    f_dark = detector.keypoints if len(detector.keypoints) > 0 else np.array([[0, 0]])
    f_dark = deloutfeature(f_dark, mask)
    detector.detect(img_inv)
    f_light = detector.keypoints if len(detector.keypoints) > 0 else np.array([[0, 0]])
    f_light = deloutfeature(f_light, mask)
    return f_dark, f_light


def patchsimilarity(pfeatures, std):
    """
    Compare the similarity between patch's feature and standard model by their features.

    Args:
        pfeatures: features of the patch.
        std: features of the standard patch model.

    Returns:
        Return a value of similarity (>0, but not strictly <1) .
    """
    penalty = 0
    if pfeatures[0, 0] == 0 or pfeatures[0, 1] == 0:
        pfeatures = np.ones(std.shape)
    elif pfeatures.shape[0] < std.shape[0]:
        penalty = std.shape[0] - pfeatures.shape[0]
        pfeatures = np.vstack((pfeatures, np.ones([penalty, 2])))
    elif pfeatures.shape[0] > std.shape[0]:
        penalty = pfeatures.shape[0] - std.shape[0]
        pfeatures = pfeatures[:std.shape[0], :]
    px = pfeatures / np.array([np.sum(pfeatures[:, 0]), np.sum(pfeatures[:, 1])])
    pstd = std / np.array([np.sum(std[:, 0]), np.sum(std[:, 1])])
    re = -np.sum(px * np.log(px / pstd)) + 0.1 * penalty
    return re


# Pour Gaussian similarity
class Pins:
    def destribution(self):
        """
        return the value of a 2D Gaussian distribution for outside execution.

        Returns:
            ndarray matrix of pins distribution
        """
        return self.z

    def gaussian_2d(self, width):
        """
        Compute the value of a 2D Gaussian distribution at given x, y coordinates.

        Args:
            width: Maximum range of normal distribution, for limit the calculation.
                   avoids computing the normal distribution of individual pins over the entire space

        Returns:
            ndarray of the 2D Gaussian distribution at the given coordinates.
        """
        x = np.linspace(0, width-1, width)
        y = np.linspace(0, width-1, width)
        X, Y = np.meshgrid(x, y)
        pos = np.dstack((X, Y))
        inv_sigma = np.linalg.inv(self.MAT_SIGMA)
        exponent = np.exp(-0.5 * np.einsum('...k,kl,...l->...', pos - width//2, inv_sigma, pos - width//2))
        return 1/self.num * exponent

    def __init__(self, idxs, mode, shape=np.array([95, 180]), width=41):
        if mode == 'vga':
            self.num = 15
            self.sigma = 55
        elif mode == 'rs232':
            self.num = 9
            self.sigma = 75
        self.MAT_SIGMA = np.array([[self.sigma, 0], [0, self.sigma]])
        self.z = np.zeros(shape+width-1)
        self._pin = self.gaussian_2d(width)
        for h, w in idxs:
            self.z[h:h+width, w:w+width] += self._pin
        bias = width // 2
        self.z = self.z[bias:shape[0]+bias, bias:shape[1] + bias]


def p_modsimilarity(ls):
    # A sub function used for para calculation
    return modsimilarity(ls[0], ls[1])


def paramatch(ACCURACY, im_des, angle, fdes):
    def gen_patch():
        for i in range(mx):
            print("\r", end="")
            print("%d° searching progress:"%angle, " {}%: ".format(int(i/mx*100)), "▋" * int(i * 50 / mx), end="")
            sys.stdout.flush()
            for j in range(my):
                # Take a patch
                p = im_des[i*ACCURACY:i*ACCURACY+connect_h, j*ACCURACY:j*ACCURACY+connect_w]
                yield [p, fdes]
        print("\r", end="")
        print("%d° searching progress:"%angle, " {}%: ".format(100), "▋" * 50, end="")

    connect_h = fdes.shape[0]
    connect_w = fdes.shape[1]
    mx = (im_des.shape[0]-connect_h+1)//ACCURACY
    my = (im_des.shape[1]-connect_w+1)//ACCURACY
    num_processes = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=num_processes)
    result = []
    gen = gen_patch()
    while True:
        task_data = []
        try:
            for _ in range(num_processes):
                task_data.append(next(gen))
        except StopIteration:
            result.extend(pool.map(p_modsimilarity, task_data))
            break
        result.extend(pool.map(p_modsimilarity, task_data))
    pool.close()
    pool.join()

    print('\n')
    tmp = np.array(result)
    sim_matrix = tmp.reshape(mx, my)
    d_list = peak_local_max((sim_matrix-np.min(sim_matrix))/(np.max(sim_matrix)-np.min(sim_matrix)),
                            threshold_abs=0.97, min_distance=1)
    d_result = [(h*ACCURACY, w*ACCURACY, angle, sim_matrix[h, w]) for h, w in d_list if sim_matrix[h, w] > 0.40]
    return d_result


def modsimilarity(x, y):
    """
    Compare the similarity between patch and standard model by their features using 2D Gaussian pins model.

    Args:
        x: features of the patch.
        y: features of the standard patch model.

    Returns:
        Return pfeatures value of similarity (>0, but not strictly <1) .
    """
    if np.all(x == 0.0):
        return 0.0
    else:
        '''
        # Compute the FFT
        fft_x = np.fft.fft2(x)
        fft_y = np.fft.fft2(y)

        # Compute the correlation coefficient in the frequency domain
        cross_power_spectrum = np.real(np.conj(fft_x) * fft_y)
        auto_power_spectrum_x = np.real(np.conj(fft_x) * fft_x)
        auto_power_spectrum_y = np.real(np.conj(fft_y) * fft_y)

        correlation_coefficient = np.sum(cross_power_spectrum) / np.sqrt(
            np.sum(auto_power_spectrum_x) * np.sum(auto_power_spectrum_y))
        '''
        dx = (x - np.mean(x))*256
        dy = (y - np.mean(y))*256
        correlation_coefficient = np.multiply(dx, dy).sum() / np.sqrt(np.multiply(dx, dx).sum() * np.multiply(dy, dy).sum())

    return correlation_coefficient


def composantfilter(compos, hw):
    """
    Input the list of one type components, filter the components who have lower similarity.
    Merge parts that overlap in adjacent regions

    Args:
        compos: list of one type components, list of [x, y, angle, sim].
        hw: size pixels of height + width.

    Returns:
        Return list of components filtered.
    """
    if len(compos) <= 1:
        return compos
    compos_matrix = np.unique(np.array(compos), axis=0)
    sim = compos_matrix[:, 3]
    tmp = []
    # delete whose similarity too low
    for i in range(sim.size):
        if sim[i] < 0.07:
            tmp.append(i)
    compos_matrix = np.delete(compos_matrix, tmp, 0)
    if compos_matrix.shape[0] <= 1:
        return compos_matrix.tolist()
    # hypothetical test
    sim = compos_matrix[:, 3]
    mse = np.sqrt(np.var(sim))  # Mean squared error
    tmp = []
    for i in range(sim.size):
        if sim[i] < max(sim)-np.clip(0.12-mse, 0, 0.1):
            tmp.append(i)
    compos_matrix = np.delete(compos_matrix, tmp, 0)
    if compos_matrix.shape[0] <= 1:
        return compos_matrix.tolist()
    # clustering the component
    Z = linkage(compos_matrix[:, :2], 'ward')
    cluster_assignments = fcluster(Z, hw*0.1, criterion='distance')
    cluster_centers = [compos_matrix[cluster_assignments == cluster].mean(axis=0) for cluster in
                       range(1, max(cluster_assignments) + 1)]
    result = [[int(i[0]), int(i[1]), int(i[2]//90*90), i[3]]for i in cluster_centers]
    '''
    destribution = np.zeros([int(np.max(compos_matrix[:,0])-np.min(compos_matrix[:,0])+1),
                             int(np.max(compos_matrix[:,1])-np.min(compos_matrix[:,1])+1)],dtype=bool)
    compos_pos = np.zeros(destribution.shape,dtype=int)
    for idx in compos_matrix[:, :2]:
        destribution[int(idx[0]-np.min(compos_matrix[:,0])), int(idx[1]-np.min(compos_matrix[:,1]))] = True
    filter = (int((0.1 * h) // 2 * 2 + 1), int((0.1 * w) // 2 * 2 + 1))
    destribution = np.pad(destribution, (filter[0]//2,filter[1]//2), mode='constant', constant_values=(False, False))
    for i in range(compos_pos.shape[0]):
        for j in range(compos_pos.shape[1]):
            compos_pos[i,j] = np.count_nonzero(destribution[i:i+filter[0],j:j+filter[1]])
    print(compos_pos)
    '''
    return result


def imedge(image):
    """
    Compute the image edge.

    Args:
        image: 2d grey scale nd.array image

    Returns:
        image edge nd.array in the same size
        filters.sobel(image) returns the result of convolution, no normalisation
        canny(image, 1) returns the edge in picture, and the edge is normalised in 1 pixel.
            Parameter 1 is sigma in gussian filter
    """
    edge = filters.sobel(image)
    return (edge - np.min(edge))/(np.max(edge)-np.min(edge))
    # return canny(image, 1)


def klentropy(x, std):
    # K-L entropy, no use now
    # calcul similarity by l-l entropy
    penalty = 0
    if x.shape[0] < std.shape[0]:
        penalty = std.shape[0]-x.shape[0]
        x = np.vstack(x, x[:penalty, :])
    elif x.shape[0] > std.shape[0]:
        penalty = x.shape[0]-std.shape[0]
        x = x[:std.shape[0], :]
    px = x / np.array([np.sum(x[:, 0]), np.sum(x[:, 1])])
    pstd = std / np.array([np.sum(std[:, 0]), np.sum(std[:, 1])])
    return -np.sum(px * np.log(px / pstd)) + 0.1 * penalty


def find_rectangle1(image_g, height, length, line_gap=10):
    """
    Find the rectangle of given shape and the height is longer than width. Represent by 1 in function name.

    Args:
        image_g: 2d grey scale ndarray image.
        height: height of the power block.
        length: length of the power block.
        line_gap: parameter in probabilistic_hough_line function. the bigger, the function combine thin lines together

    Returns:
        A list of tuples of coordinates of the four points of rectangle
    """
    rectangles = []
    edge = canny(image_g, 1)
    # find straight vertical lines that in the image
    angle = np.array([0.0])
    # probabilistic_hough_line is a useful methode that can find lines of defined length, angle
    lines = {a for a in probabilistic_hough_line(edge, threshold=10, line_length=int(height * 0.9), line_gap=line_gap,
                                                 theta=angle) if abs(a[0][1] - a[1][1]) < int(height * 1.1)}
    # N.B.: It is strange that the order of (height,width) changed to (width, height) after probabilistic_hough_line,
    # but matplot lib can give the true output.

    linedisplay(edge, lines)
    # compare each pairs to find out rectangle
    lines_ = {a for a in probabilistic_hough_line(edge, threshold=10, line_length=int(length * 0.8),
                                                 line_gap=line_gap, theta=np.array([0.5*np.pi])) if
             abs(a[0][0] - a[1][0]) < int(length * 1.2)}
    linedisplay(edge, lines_)
    DEVIATION = 14  # Unit measured in pixel. i.e.3mm
    for (p2, p1), (p3, p4) in combinations(lines, 2):
        # p2--------p4  x
        # |          |
        # p1--------p3
        # y
        # (x,y)

        # make points in order
        if p2[1] > p1[1]:
            p2, p1 = p1, p2
        if p4[1] > p3[1]:
            p3, p4 = p4, p3
        if p4[0] < p2[0]:
            p2, p4 = p4, p2
            p1, p3 = p3, p1
        l1 = p1[1] - p2[1]
        l2 = p3[1] - p4[1]

        # Parallelogram
        if abs(l1 - l2) < 0.5*DEVIATION:
            # rectangle within length
            if abs(p4[0] - p3[0]) < 0.5*DEVIATION:
                for ln in lines_:
                    if hit_inzone(ln, (p2, p1)) and hit_inzone(ln, (p3, p4)):
                        rectangles.append(p2)
                        break
    return rectangles


# for usb
def find_rectangle_(image_g, length, height, line_gap=10):
    """
    Find the rectangle of given shape and the width is longer than height. Represent by _ in function name.

    Args:
        image_g: 2d grey scale ndarray image.
        length: length of the power block.
        height: height of the power block.
        line_gap: parameter in probabilistic_hough_line function. the bigger, the function combine thin lines together

    Returns:
        A list of tuples of coordinates of the four points of rectangle
    """
    rectangles = []
    edge = canny(image_g, 1)
    # find straight vertical lines that in the image
    angle = np.array([0.5*np.pi])
    # probabilistic_hough_line is a useful methode that can find lines of defined length, angle
    lines = {a for a in probabilistic_hough_line(edge, threshold=5, line_length=int(length * 0.9), line_gap=line_gap,
                                                 theta=angle) if abs(a[0][0] - a[1][0]) < int(length * 1.1)}
    # N.B.: It is strange that the order of (height,width) changed to (width, height) after probabilistic_hough_line,
    # but matplot lib can give the true output.

    linedisplay(edge, lines)
    # compare each pairs to find out rectangle
    lines1 = {a for a in probabilistic_hough_line(edge, threshold=5, line_length=int(height * 0.8),
                                                  line_gap=line_gap, theta=np.array([0.0]))
              if abs(a[0][1] - a[1][1]) < int(height * 1.2)}
    linedisplay(edge, lines1)
    # Parallelogram
    DEVIATION = 18.28  # Unit measured in pixel. i.e.2.0mm
    for (p1, p2), (p3, p4) in combinations(lines, 2):
        # p1--------p2  x
        # |          |
        # p4--------p3
        # y
        # (x,y)

        # make points in order
        if p1[0] > p2[0]:
            p1, p2 = p2, p1
        if p4[0] > p3[0]:
            p3, p4 = p4, p3
        if p4[1] < p1[1]:
            p1, p4 = p4, p1
            p2, p3 = p3, p2
        l1 = p2[1] - p1[1]
        l2 = p3[1] - p4[1]
        # Parallelogram
        if abs(l1 - l2) < 0.5*DEVIATION:
            # rectangle within length
            if abs(p3[0] - p2[0]) < 0.5*DEVIATION:
                if abs(abs(p4[1] - p1[1]) - height) < DEVIATION:
                    for ln in lines1:
                        if hit_inzone(ln, (p1, p2)) and hit_inzone(ln, (p4, p3)):
                            rectangles.append(p1)
                            break
    return rectangles


def hit_inzone(l0, l1, r=7):
    """
    Determine whether the two line have one endpoint commune.
    Both endpoints are considered the same if they are within the agreed neighborhood

    Args:
        l0: tuple (a0,b0)
        l1: tuple (a1,b1)
        r: radius of zone, unit is pixel.
    Returns:
        1 or 0 whether the p1 is in  zone of p0
    """

    def distance(p0, p1):
        return np.sqrt((p0[0] - p1[0]) ** 2 + (p0[1] - p1[1]) ** 2)
    for i in l0:
        for j in l1:
            if distance(i, j) < r:
                return 1
    return 0


def in_rectangle(point, rect):
    """
    Determine if a point p is in a rectangle

    Args:
        point: the coordinate of the point
        rect: a tuple of four points of a rectangle.

    Returns:
        1 or 0 whether the point is in this rectangle
    """
    point = (point[1], point[0])  # to make the coordinate into (wigth,height)
    p1, p2, p3, p4 = rect[0], rect[1], rect[2], rect[3]
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


def linedisplay(image, lines):
    """
    Display lines detected in the image.

    Args:
        image: 2d grey scale nd.array image.
        lines: a list of tuple of two points of lines.

    Returns:
        matplot UI on the screen.
    """

    # Generating figure 2
    fig, axes = plt.subplots(2, 1, figsize=(15, 8), sharex=True, sharey=True)
    ax = axes.ravel()

    ax[0].imshow(image, cmap=cm.gray)
    ax[0].set_title('Input image')

    ax[1].imshow(image * 0)
    for line in lines:
        p0, p1 = line
        ax[1].plot((p0[0], p1[0]), (p0[1], p1[1]))
    ax[1].set_xlim((0, image.shape[1]))
    ax[1].set_ylim((image.shape[0], 0))
    ax[1].set_title('Probabilistic Hough')

    for a in ax:
        a.set_axis_off()

    plt.tight_layout()
    plt.savefig('api/tmpline.png')
    plt.show()


def template_match(image, template, threshold, mindis):
    """
    Compute the value of a 2D Gaussian distribution at given x, y coordinates.

    Args:
        image: 2d nd.array image.
        template: 2d numpy.ndarray patch image.
        threshold: absolute threshold in peak_localmax that only peaks higher than this can be kept.
        mindis: the distance minimum between peaks. But it not perform like the real distance in pixels,
                maybe just a parameter.

    Returns:
        Points of the upper left corner, in(height, length, angle, similarity).
    """
    image = filters.gaussian(image, sigma=1.5)
    positions = []
    template_height, template_weight = template.shape
    for _ in range(2):
        sample_mt = match_template(image, template)
        tmp = peak_local_max(np.squeeze(sample_mt), threshold_abs=threshold, min_distance=mindis).tolist()
        if tmp:
            positions += [(x, y, 180*_, sample_mt[x, y]) for x, y in tmp]   # (height, width, angle, similarity)
        template = rotate(template, 180, resize=True)
    if not positions:
        positions = [(0, 0, 0, -1)]
    # drawcomponents(image, positions, template_weight, template_height)
    return positions


def drawcomponents(image, positions, template_width, template_height, sample_mt=0):
    """
    Draw the component box on the server image.

    Args:
        image: 2d nd.array grey scale image.
        positions: positions of components.
        template_width: template width
        template_height: template height
        sample_mt: similarity matrix for drawing heat map

    Returns:
        matplot UI on the screen.
    """
    if sample_mt is 0:
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111)
        ax.imshow(image, cmap='gray')
        for x, y, n, sim in positions:    # (height, width, angle, similarity)
            w, h = template_width, template_height
            for _ in range(n//90):
                w, h = h, w
            rect = plt.Rectangle((y, x), w, h, color='r', fc='none')
            ax.add_patch(rect)
        ax.set_title('Grayscale', fontsize=15)
        plt.savefig('api/tmpcompo.png')
        plt.show()
    else:
        fig, ax = plt.subplots(2, 1, figsize=(10, 8))
        ax[0].imshow(image, cmap='gray')
        for x, y, n, sim in positions:
            w, h = template_width, template_height
            for _ in range(n//90):
                w, h = h, w
            rect = plt.Rectangle((x, y), w, h, color='r',
                                 fc='none')
            ax[0].add_patch(rect)
        ax[0].set_title('Grayscale', fontsize=15)
        ax[1].imshow(sample_mt, cmap='magma')
        ax[1].set_title('Template Matching', fontsize=15)
        plt.savefig('api/tmpcompo.png')
        plt.show()


def jsondump(file_path, jsonraw):
    with open(file_path, "w") as json_file:
        json.dump(jsonraw, json_file)


def imagesave(image, path):
    imsave(image, path)


