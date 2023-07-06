import logging
import sys
import os
import time
import re

import common.Utils as Utils
import AR.source.ocr.OCR as OCR
import AR.source.ocr.ShapeDetector as ShapeDetector

path = os.path.dirname(__file__)

#####################################################################################################################
#####################################################################################################################

def ReaderOneImageRecursive(img, regexp, type, ocrResults):
    """ Handles regexp by calling ogLblUtils, call ogLblOCR to perform OCR on the image provided """
    # Initialize var site, room, rack to avoid exceptions
    label = []
    matcher = re.compile(regexp, re.IGNORECASE)

    regexList = Utils.RegexSpliterRecursive(regexp)
    logging.debug(f"RegexList: {regexList}")

    # Perform OCR on the img with the specified technology
    current = time.time()
    if (ocrResults):
        results = ocrResults
    else:
        results = OCR.PerformOCR(img)
        ocrResults = results
    logging.debug(f"performed OCR in: {time.time() - current} s")
    current = time.time()

    lineNumber = 1
    logging.info("Reading the text on the image...")
    for (bbox, text, prob) in results:
        logging.debug(f"Read line {lineNumber}: {text}")
        lineNumber += 1

    # Case where the label is full (original regexp), we can do all the processing in one go (one text)
    for (bbox, text, prob) in results:
        text = OCR.ReplaceSymbol(text)
        test = OCR.ReturnMatch(text, matcher)
        if test is not None:
            label = Utils.RegexSpliterRecursive(test)
            logging.debug(f"Label = {label} (full label)")
            logging.debug(f"Performed rack label detection and correction in: {time.time() - current} s")
            return label, ocrResults

    counter = 0
    limit = 0
    for count, value in enumerate(regexList):
        flag = False
        matcher = re.compile(value, re.IGNORECASE)
        for (bbox, text, prob) in results:
            if counter >= limit:
                text = OCR.ReplaceSymbol(text)
                test = OCR.ReturnMatch(text, matcher)
                if test is not None:
                    label.append(test)
                    logging.debug(f"Match : Label = {label} after text {text} for regexp {value} (separated label)")
                    if not flag:
                        limit = counter
                    counter = 0
                    flag = True
                    break
                else:
                    logging.debug(f"Label = {label} after text {text} for regexp {value}, No Match (separated label)")
            counter += 1
        counter = 0
        if not flag:
            label.append("Missing")
        logging.debug(f"Label = {label} for regexp {value} (separated label)")
    logging.debug(f"Performed rack label detection and correction in: {time.time() - current} s")
    return label, ocrResults

#####################################################################################################################
#####################################################################################################################
def ReaderCroppedAndFullImage(img, regexp, type, background, range, ocrResults):
    """ Call ogLblShapeDetector to crop the image, call ReaderOneImageRecursive on the cropped image and on the full image if not succesfull to read the label. Returns a list containing all characters in the image satisfying the different part ot the regexp and a list containing all characters that were read on the image to be used if a new regexp is used on the same image. """
    start = time.time()
    current = start
    logging.debug(f"Try reading with regexp: {regexp} and background color: {background}")

    #Cropping the image
    croppedImage = ShapeDetector.ShapeAndColorDetector(img, background, range)

    logging.debug(f"Cropped image in: {time.time() - current} s")

    # Perform OCR + post-processing on the cropped_image to recover the name of the room and rack
    if (not ocrResults):
        label, ocrResults = ReaderOneImageRecursive(croppedImage, regexp, type, ocrResults)
    else:
        logging.debug(f"Using the already found text with ocr.")
        # Label was not found on cropped image so we try on whole image
        label, ocrResults = ReaderOneImageRecursive(croppedImage, regexp, type, ocrResults)
        return label, ocrResults

    # return label if it was found on the cropped image
    if 'Missing' not in label:
        return label, ocrResults
    else:
        logging.debug("Could not find rack label on cropped image. Trying on the full image.")

        # Label was not found on cropped image so we try on whole image
        label, ocrResults = ReaderOneImageRecursive(img, regexp, type, [])
    return label, ocrResults

#####################################################################################################################
#####################################################################################################################




