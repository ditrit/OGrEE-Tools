import tools
from classifiers import Classifiers
import torch.multiprocessing


if __name__ == '__main__':
    torch.multiprocessing.freeze_support()
    #SLOTNAME = "serveur/ibm-x3850x6.rear.png"
    #HEIGHT = 172.8
    #LENGTH = 482.0

    SLOTNAME = "serveur/dell-poweredge-r410-hs.rear.png"
    HEIGHT = 43.0
    LENGTH = 434.0

    #SLOTNAME = "serveur/dell-poweredge-2950-6lff.front.png"
    #HEIGHT = 86.4
    #LENGTH = 444.3

    #SLOTNAME = "serveur/ibm-x3650m4.rear.png"
    #HEIGHT = 86.5
    #LENGTH = 445.0

    #SLOTNAME = "serveur/dell-poweredge-r430.rear.png"
    #HEIGHT = 42.8
    #LENGTH = 662.4

    image = tools.imageload(SLOTNAME, "grey")
    #image = tools.impreprocess(image)
    ogreeTools = Classifiers(image, HEIGHT, LENGTH)
    ogreeTools.clvga_rs232()
    #ogreeTools.clrj45()
    #ogreeTools.clusb()
    # #ogreeTools.clsource()
    ogreeTools.describe()
    '''
    #rgbview(image)
    image_hsv = rgb2hsv(image)
    image_e = filters.sobel(image_hsv[:,:,-1])
    image_e = filters.gaussian(image_e,sigma = 0.5)
    hsvview(image_hsv)
    template = rgba2rgb(imread('image/rj45.png'))
    #template = imread('image/vga2.png')
    template = impreprocess(template)
    template_hsv = rgb2hsv(template)
    template_e = filters.sobel(template_hsv[:,:,-1])
    template_e = filters.gaussian(template_e,sigma = 1)
    templateMatch(image_e,template_e)
    '''