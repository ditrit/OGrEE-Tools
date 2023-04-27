from tools import *


slotname = "ibm-x3630m4-2lff.rear.png"
image = imageload(slotname,"color")
image = impreprocess(image)
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