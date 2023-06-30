from skimage.color.colorconv import rgba2rgb, rgb2hsv, rgb2gray, hsv2rgb
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
from skimage.io import imshow, imread
from skimage.feature import match_template, peak_local_max
from skimage.feature import canny
from skimage import filters
from skimage import exposure
from skimage.transform import rescale, rotate
from skimage.transform import probabilistic_hough_line
from itertools import combinations
import json
import torch

# special constant for all the function
RATIO = 781/85.4  # pixel/mm = 9.145


def imageload(f, flag="color"):
    """
    Compute the value of a 2D Gaussian distribution at given x, y coordinates.

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
    else:
        img = imread(fn)    # (H x W x C), [0, 255], RGB
        if img.shape[-1] == 4:
            img = rgba2rgb(img)
            print("4 channels picture  ", f)
        else:
            pass
    return img


def preprocess(image: np.ndarray):
    """
    Compute the value of a 2D Gaussian distribution at given x, y coordinates.

    Args:
        image: x-coordinate(s) as a numpy array or scalar.

    Returns:
        Value(s) of the 2D Gaussian distribution at the given coordinates.
    """
    image[:, :, 0] = exposure.equalize_hist(image[:, :, 0])
    image[:, :, 1] = exposure.equalize_hist(image[:, :, 1])
    image[:, :, 2] = exposure.equalize_hist(image[:, :, 2])
    return image


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
    elif image.shape[-1] == 1:
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
        grey image in ndarray(x',y') with new and standard shape
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
    Compute the value of a 2D Gaussian distribution at given x, y coordinates.

    Args:
        image: image of the server, back or face.
        mask: a black coverage that cover the extraneous images in view (e.g. screws, labels)
        detector: CENSURE class object predefined

    Returns:
        [n,2] ndarray of features' coordinates
    """
    def deloutfeature(feature, m):
        # delete features appeared in mask
        idx = []
        for k in range(feature.shape[0]):
            if not m[feature[k, 0], feature[k, 1]]:
                idx.append(k)
        return np.delete(feature, idx, 0)
    image = image * mask
    #image = torch.mm(image, mask)
    img_vag = filters.gaussian(image, sigma=1)
    img_inv = -img_vag + 1
    detector.detect(img_vag)
    f_dark = detector.keypoints if len(detector.keypoints) > 0 else np.array([[0, 0]])  # à améliorer
    f_dark = deloutfeature(f_dark, mask)
    detector.detect(img_inv)
    f_light = detector.keypoints if len(detector.keypoints) > 0 else np.array([[0, 0]])
    f_light = deloutfeature(f_light, mask)
    return f_dark, f_light


def patchsimilarity(pfeatures, std):
    """
    Compare the similarity between patch and standard model by their features.

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
    def proba(self, idx):
        """
        Compute the value of a 2D Gaussian distribution at given x, y coordinates.

        Args:
            x: coordinate on x axis.
            y: coordinate on y axis.

        Returns:
            a float similarity value, the bigger, the more similar
        """
        return self.z[idx[0], idx[1]]

    def gaussian_2d(self,x, y, mu):
        """
        Compute the value of a 2D Gaussian distribution at given x, y coordinates.

        Args:
            x: x-coordinate(s) as a numpy array or scalar.
            y: y-coordinate(s) as a numpy array or scalar.
            mu: Mean of the Gaussian distribution as a 2-element numpy array [mu_x, mu_y].
            sigma: Covariance matrix of the Gaussian distribution as a 2x2 numpy array.

        Returns:
            Value(s) of the 2D Gaussian distribution at the given coordinates.
        """
        X, Y = np.meshgrid(x, y)
        pos = np.dstack((X, Y))
        inv_sigma = np.linalg.inv(self.SIGMA)
        exponent = np.exp(-0.5 * np.einsum('...k,kl,...l->...', pos - mu, inv_sigma, pos - mu))
        return 1/self.num * exponent

    def __init__(self, idxs):
        x = np.linspace(0, 289, 290)
        y = np.linspace(0, 104, 105)
        self.SIGMA = np.array([[100, 0], [0, 100]])
        peaks = [{'mu': np.array([i[0], i[1]])} for i in idxs]
        self.z = np.zeros((len(y), len(x)))
        self.num = len(idxs)
        for peak in peaks:
            self.z += self.gaussian_2d(x, y, peak['mu'])


def gaussiansimilarity(pfeatures, std):
    """
    Compare the similarity between patch and standard model by their features using 2D Gaussian pins model.

    Args:
        pfeatures: features of the patch.
        std: features of the standard patch model.

    Returns:
        Return a value of similarity (>0, but not strictly <1) .
    """
    sim = 0
    penality = 0.9**abs(pfeatures.shape[0] - std.num)
    sim += sum([std.proba(i) for i in pfeatures.tolist()])
    #if sim>0.5:
    #    print(sim)
    '''
    match = match_descriptors(pfeature, std_pattern, metric=None, p=2, cross_check=False)
    distance = -10*(std_pattern.shape[0]-match.shape[0])
    for i,j in match:
        distance += -np.linalg.norm(pfeature[i]-std_pattern[j])
    distance = distance- 10 * abs(pfeature.shape[0] - std_pattern.shape[0])
    return distance
    '''
    return sim * penality


def imedge(image):
    """
    Compute the image edge.

    Args:
        image: 2d grey scale nd.array image

    Returns:
        image edge nd.array in the same size
    """
    return filters.sobel(image) > 0.05
    #return canny(image, 1)


def test(a):
    print(a.shape)
    return torch.max(a)

# K-L entropy
def klentropy(x, std):
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


# for power block
def find_rectangle1(image_g, height, length, line_gap=10):
    """
    Compute the value of a 2D Gaussian distribution at given x, y coordinates.

    Args:
        image_g: 2d grey scale nd.array image.
        length: length of the power block.
        height: height of the power block.
        line_gap: parameter in probabilistic_hough_line function. the bigger, the function combine thin lines together

    Returns:
        A list of tuples of coordinates of the four points of rectangle
    """
    rectangles = []
    edge = canny(image_g, 1)
    # find straight vertical lines that in the image
    angle = np.array([0.0])
    # probabilistic_hough_line(image, threshold=10, line_length=50, line_gap=10, theta=None, seed=None)
    lines = {a for a in probabilistic_hough_line(edge, threshold=10, line_length=int(height * 0.94), line_gap=line_gap,
                                                 theta=angle) if abs(a[0][1] - a[1][1]) < int(height * 1.06)}
    # N.B.: It is strange that the order of (height,width) changed to (width, height) after probabilistic_hough_line,
    # but matplot lib can give the true output.

    linedisplay(image_g, lines)
    # compare each pairs to find out rectangle
    lines_ = {a for a in probabilistic_hough_line(edge, threshold=10, line_length=int(length * 0.8),
                                                 line_gap=line_gap, theta=np.array([0.5*np.pi])) if
             abs(a[0][0] - a[1][0]) < int(length * 1.2)}
    linedisplay(image_g, lines_)
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
                        rectangles.append((p2[0], p2[1], 90))
                        break
    return rectangles


# for usb
def find_rectangle_(image_g, length, height, line_gap=10):
    """
    Compute the value of a 2D Gaussian distribution at given x, y coordinates.

    Args:
        image_g: 2d grey scale nd.array image.
        height: length of the power block.
        length: height of the power block.
        line_gap: parameter in probabilistic_hough_line function. the bigger, the function combine thin lines together

    Returns:
        A list of tuples of coordinates of the four points of rectangle
    """
    rectangles = []
    edge = canny(image_g, 1)
    # find straight vertical lines that in the image
    angle = np.array([0.5*np.pi])
    # probabilistic_hough_line(image, threshold=10, line_length=50, line_gap=10, theta=None, seed=None)
    lines = {a for a in probabilistic_hough_line(edge, threshold=10, line_length=int(length * 0.9), line_gap=line_gap,
                                                 theta=angle) if abs(a[0][0] - a[1][0]) < int(length * 1.1)}
    # N.B.: It is strange that the order of (height,width) changed to (width, height) after probabilistic_hough_line,
    # but matplot lib can give the true output.

    linedisplay(image_g, lines)
    # compare each pairs to find out rectangle
    lines1 = {a for a in probabilistic_hough_line(edge, threshold=10, line_length=int(height * 0.8),
                                                  line_gap=line_gap, theta=np.array([0.0]))
              if abs(a[0][1] - a[1][1]) < int(height * 1.2)}
    linedisplay(image_g, lines1)
    # Parallelogram
    DEVIATION = 14  # Unit measured in pixel. i.e.1.8mm
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
                            rectangles.append((p1[0], p1[1], 0))
                            break

    return rectangles


def hit_inzone(l0, l1, r=7):
    """
    Compute the value of a 2D Gaussian distribution at given x, y coordinates.

    Args:
        l0: tuple (a0,b0)
        l1: tuple (a1,b1)
        r: radius of zone
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


def in_rectangle(point, p):
    """
    Compute the value of a 2D Gaussian distribution at given x, y coordinates.

    Args:
        point: the position of C14 interface.
        p: a tuple of four points of a rectangle.

    Returns:
        1 or 0 whether the point is in this rectangle
    """
    point = (point[1], point[0])  # to make the coordinate into (wigth,height)
    p1, p2, p3, p4 = p[0], p[1], p[2], p[3]
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
    plt.show()


def template_match(image, template, threshold, mindis):
    """
    Compute the value of a 2D Gaussian distribution at given x, y coordinates.

    Args:
        image: 2d nd.array image.
        template: 2d nd.array patch image.
        threshold: absolute threshold in peak_localmax that only peaks higher than this can be kept.
        mindis: the distance minimum between peaks. But it not perform like the real distance in pixels,
                maybe just a parameter.

    Returns:
        Points of the upper left corner.
    """
    image = filters.gaussian(image, sigma=1.5)
    positions = []
    template_height, template_weight = template.shape
    for _ in range(4):
        template = rotate(template, 90, resize=True)
        sample_mt = match_template(image, template)
        tmp = peak_local_max(np.squeeze(sample_mt), threshold_abs=threshold, min_distance=mindis).tolist()
        if tmp:
            positions += [(x, y, 270-90*_) for x, y in tmp]
    drawcomponents(image, positions, template_weight, template_height)
    return positions



def drawcomponents(image, positions, template_width, template_height, sample_mt=0):
    """
    Compute the value of a 2D Gaussian distribution at given x, y coordinates.

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
        for x, y, n in positions:
            w, h = template_width, template_height
            for _ in range(n//90):
                w, h = h, w
            rect = plt.Rectangle((x, y), w, h, color='r',
                                 fc='none')
            ax.add_patch(rect)
        ax.set_title('Grayscale', fontsize=15)
    else:
        fig, ax = plt.subplots(2, 1, figsize=(10, 8))
        ax[0].imshow(image, cmap='gray')
        for x, y, n in positions:
            w, h = template_width, template_height
            for _ in range(n//90):
                w, h = h, w
            rect = plt.Rectangle((x, y), w, h, color='r',
                                 fc='none')
            ax[0].add_patch(rect)
        ax[0].set_title('Grayscale', fontsize=15)
        ax[1].imshow(sample_mt, cmap='magma')
        ax[1].set_title('Template Matching', fontsize=15)
    plt.show()


def calibrateear(components, shapepix, shapemm):
    """
        Determing is there a pair of ears in the image.
        If so, the components' position will be recalculated if they are posed in a non-ear server.

    Args:
        components: x-coordinate(s) as a numpy array or scalar.
        shapepix: image's shape in pixel.
        shapemm: server's shape in reality(without ears) in mm.

    Returns:
        The coordinates without ears.
    """
    ear = 0.5*(shapepix[1]-shapepix[0]*shapemm[1]/shapemm[0])
    if ear < 0:
        return components
    else:
        newpos = dict()
        for i in components:
            value = components[i]
            key = (i[0], int(i[1]-ear))
            newpos[key] = value
        return newpos


def jsonwrite(coordinate, path):
    """
    Generate the JSON text about one component.

    Args:
        coordinate: Coordinate of a component.
        path: path of the model component json file

    Returns:
        json text
    """
    with open(path, 'r+') as file:
        depth = 0  # en pixel
        p = json.load(file)
        posWDH = [int(coordinate[0]/RATIO), int(depth/RATIO), int(coordinate[1]/RATIO)]
        p.update({"elemPos": posWDH})
        file.close()
        print(p)
        return p
