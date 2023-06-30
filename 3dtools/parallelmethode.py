import torch
import numpy as np
from skimage import filters


def creatdata(mx,my,ACCURACY,image):
    matrix = np.ones([mx * my, 105, 290], dtype="float")
    img_vag = filters.gaussian(image, sigma=1)
    for i in range(mx):
        for j in range(my):
            matrix[i * mx + my, :, :] = img_vag[i * ACCURACY:i * ACCURACY + 105, j * ACCURACY:j * ACCURACY + 290]
    return matrix

class Pin:
    def proba(self, x, y):
        """
        Compute the value of a 2D Gaussian distribution at given x, y coordinates.

        Args:
            x: coordinate on x axis.
            y: coordinate on y axis.

        Returns:
            a float similarity value, the bigger, the more similar
        """
        return self.pin_simi(x, y)

    def value(self):
        return self.pin_simi[]

    def __init__(self, x_center, y_center):
        SIGMA = 40.0

        self.x_center = x_center
        self.y_center = y_center
        coeff = 1 / (2 * np.pi * np.square(SIGMA))*100
        self.pin_simi = lambda x, y: \
            coeff * np.exp(-0.5*(np.square(x-x_center)/SIGMA**2+np.square(y-y_center)/SIGMA**2))


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
    penality = 1#0.9**abs(pfeatures.shape[0] - len(std))
    for i in range(pfeatures.shape[0]):  # à améliorer l'efficacité
        sim += sum([p.proba(pfeatures[i, 0], pfeatures[i, 1]) for p in std])
    '''
    match = match_descriptors(pfeature, std_pattern, metric=None, p=2, cross_check=False)
    distance = -10*(std_pattern.shape[0]-match.shape[0])
    for i,j in match:
        distance += -np.linalg.norm(pfeature[i]-std_pattern[j])
    distance = distance- 10 * abs(pfeature.shape[0] - std_pattern.shape[0])
    return distance
    '''
    return sim * penality

class parapara():
    def imfeature(self,image):
        """
        Compute the value of a 2D Gaussian distribution at given x, y coordinates.

        Args:
            image: image of the server, back or face.
            mask: a black coverage that cover the extraneous images in view (e.g. screws, labels)
            detector: CENSURE class object predefined

        Returns:
            [n,2] ndarray of features' coordinates
        """

        def del_outfeature(feature, m):
            # delete features appeared in mask
            idx = []
            for k in range(feature.shape[0]):
                if not m[feature[k, 0], feature[k, 1]]:
                    idx.append(k)
            return np.delete(feature, idx, 0)

        self.detector.detect(torch.mm(image, self.mask))
        feature = self.detector.keypoints if len(self.detector.keypoints) > 0 else np.array([[0, 0]])  # à améliorer
        feature = del_outfeature(feature, self.mask)

        print(image[40, 40])

        return gaussiansimilarity(feature, self.describer)

    def __init__(self,detector,mask,describer):
        self.detector = detector
        self.mask = mask
        self.describer = describer

