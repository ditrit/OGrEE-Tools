import tools
from classifiers import Classifiers


SLOTNAME = "serveur/ibm-x3850x6.rear.png"
HEIGHT = 172.8
LENGTH = 482.0
#SLOTNAME = "serveur/ibm-x3650m4.rear.png"
#HEIGHT = 281.9
#LENGTH = 482.0

image = tools.imageload(SLOTNAME,"grey")
#image = tools.impreprocess(image)
ogreeTools = Classifiers(image,HEIGHT,LENGTH)
#ogreeTools.clvga_rs232()
ogreeTools.clrj45()
#ogreeTools.clc14()
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