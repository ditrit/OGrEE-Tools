import re
import cv2
import easyocr

# Configuration language of the OCR, use norwegian to have the Ø symbol
reader = easyocr.Reader(['no', 'fr'])

#####################################################################################################################
#####################################################################################################################

def cleanup_text(text):
    """strip out non-ASCII text so we can draw the text on the image using OpenCV"""
    return "".join([c if ord(c) < 128 else "" for c in text]).strip()

#####################################################################################################################
#####################################################################################################################

def PerformOCR(img):
    """ Use easyOcr module to perform OCR on the provided image. Returns a tuple containing the characters read and their position. """
    # perform OCR on the image provided
    results = reader.readtext(img)
    return results

#####################################################################################################################
#####################################################################################################################

def ReplaceSymbol(text):
    """Replace the 'Ø' charachter with an '0'"""
    # Remove blank spaces in the text and turn Ø into 0
    text = text.replace("Ø", "0")
    return text

#####################################################################################################################
#####################################################################################################################

def ReturnMatch(text, labelMatcher):
    """ Match a text with a regexp. Returns a string containing the match. If none returns None. """
    match = None
    test = labelMatcher.findall(text)
    if test:
        match = test[0]
    return match

#####################################################################################################################
#####################################################################################################################