import logging
import cv2
import numpy as np
import sys
import re

#####################################################################################################################
#####################################################################################################################

def ShapeAndColorDetector(img, background, range):
    """ Perform HSV mapping on the provided image using a hexa color code or a predefined color. Crop the image according to this mask. Returns the new image. """
    masks = []
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    if background:
        for color in background:
            match = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color)
            # Set the range for the color to keep
            if color == 'orange':
                hue_min, sat_min, val_min = 7, 149, 141
                hue_max, sat_max, val_max = 20, 255, 255

            elif color == 'white':
                hue_min, sat_min, val_min = 0, 0, 245
                hue_max, sat_max, val_max = 255, 40, 255

            elif color == 'yellow':
                hue_min, sat_min, val_min = 24, 100, 141
                hue_max, sat_max, val_max = 30, 255, 255

            elif color == 'red':

                hue_min, sat_min, val_min = 0, 100, 141
                hue_max, sat_max, val_max = 10, 255, 255

            elif match:
                RGB = HexaToRGB(color)
                BGR = np.uint8([[[RGB[2], RGB[1], RGB[0]]]])
                HSV = cv2.cvtColor(BGR, cv2.COLOR_BGR2HSV)
                lowerBoundH = HSV[0][0][0] - range
                upperBoundH = HSV[0][0][0] + range
                hue_min, sat_min, val_min = lowerBoundH, 50, 50
                hue_max, sat_max, val_max = upperBoundH, 255, 255

            else:
                logging.error("Invalid Hexa code or color not in the following list: 'orange', 'white, 'yellow', 'red' (ShapeAndColorDetector in ShapeDetector.py)")
                sys.exit()

            lower = np.array([hue_min, sat_min, val_min])
            upper = np.array([hue_max, sat_max, val_max])
            masks.append((lower, upper))
    else:
        logging.error("The color list is empty (ShapeAndColorDetector in ShapeDetector.py)")
        sys.exit()

    #Initialize the bounds of our cropped image
    x_min, y_min, x_max, y_max = 5000, 5000, 0, 0

    for (lower, upper) in masks:

        #Create the mask to determine the contour
        mask = cv2.inRange(hsv, lower, upper)
        contours, hei = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        #Loop over all contours, add rectangle near detected area, set the bounds
        for c in contours:
            area = cv2.contourArea(c)
            if area > 500:
                x, y, w, h = cv2.boundingRect(c)
                if x < x_min:
                    x_min = x
                if y < y_min:
                    y_min = y
                if x + w > x_max:
                    x_max = x + w
                if y + h > y_max:
                    y_max = y + h

    #Create cropped image
    cropped_image = img[y_min:y_max, x_min:x_max]

    if cropped_image.any():
        return cropped_image
    else:
        return img

#####################################################################################################################
#####################################################################################################################

def HexaToRGB(hexa):
    """ Take a hexa color code and convert it to RGB. Returns a tuple with the RGB code. """
    h = hexa.lstrip('#')
    RGB = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    return RGB

#####################################################################################################################
#####################################################################################################################