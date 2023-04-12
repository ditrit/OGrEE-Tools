"""
**Can be run independently with args to read a label in a photo**
"""
import cv2
import glob
import os
import sys
import argparse
from PIL import Image
import logging
import mimetypes
import re
import numpy
from AR.source.classes.ARdcTrackToOGrEE import ARdcTrackToOGrEE
import label_regular.modules.ogLblUtils as Utils

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
reg = "image"
regImage = re.compile(reg)
# Parameter set in Unity and sent to the API. Hard coded here for standalone use.
deviceType = "rack"

#####################################################################################################################
#####################################################################################################################


def RackSearch(img: numpy.ndarray, customerAndSite: str, deviceType: str) -> str:
    """
    Read the config file, then call the correct Converter to get necessary data from the image

    :param numpy.ndarray img: a numpy array containing an image in bytes
    :param str customerAndSite: the name of the customer/tenant and the site where the rack is in the format {customer}.{site}
    :param str deviceType: either "rack" or "mdi"
    :returns: a serialised dictionnary of serialised OgreeMessage's instances
    :rtype: str
    """
    pathToEnvFile = f"{os.path.dirname(__file__)}/.env.json"
    url, headers, database = Utils.ReadEnv(pathToEnvFile)
    converter = ARdcTrackToOGrEE(url, headers, {"Content-Type": "application/json"})
    return converter.RackSearch(img, customerAndSite, deviceType)


def ObjectList():
    """
    **Not yet implemented**
    =======================
    Get all children of an object in a database (ie all sites of a tenant, all racks of a room,...)
    """
    pass


#####################################################################################################################
#####################################################################################################################


if __name__ == "__main__":
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"

    # COMMAND OPTIONS
    parser = argparse.ArgumentParser(
        description="Perform OCR from data (image + tenant) sent from Hololens"
    )

    parser.add_argument(
        "--mode",
        choices=["file", "imagedir"],
        help="""Specify if we use a single image or an image directory as input""",
        required=True,
    )

    parser.add_argument(
        "--path", help="""Specify the path of the input""", required=True
    )

    parser.add_argument("--site", help="""[CUSTOMER].[SITE]""", required=True)

    parser.add_argument(
        "--verbose",
        choices=["INFO", "WARNING", "ERROR", "DEBUG"],
        help="""Specify the verbose level""",
        default="DEBUG",
    )

    # Parse Args START //////////
    args = vars(parser.parse_args())
    numeric_level = getattr(logging, args["verbose"].upper())
    logging.basicConfig(
        filename=os.path.dirname(os.path.abspath(__file__)) + "/server.log",
        format=f"%(asctime)s %(levelname)s %(name)s : %(message)s",
        level=numeric_level,
    )

    mode = args["mode"]
    path = args["path"]
    tenantAndSite = args["site"]

    if mode == "file":
        img_test = args["path"]
        if mimetypes.guess_type(img_test)[0] is not None:
            if regImage.findall(mimetypes.guess_type(img_test)[0]):
                log.info("Beginning the processing of an image in mode: image\n")
                testValidity = Image.open(path)
                try:
                    testValidity.verify()
                    img = cv2.imread(path)
                except Exception:
                    log.error("Invalid image, please verify the content")
                    sys.exit()
                RackSearch(img, tenantAndSite, deviceType)

    if mode == "imagedir":
        for img_test in glob.glob(path + "/*"):
            if mimetypes.guess_type(img_test)[0] is not None:
                if regImage.findall(mimetypes.guess_type(img_test)[0]):
                    log.info("Beginning the processing of an image in mode: imagedir\n")
                    testValidity = Image.open(img_test)
                    try:
                        testValidity.verify()
                        img = cv2.imread(img_test)
                    except Exception:
                        log.error("Invalid image, please verify the content")
                        sys.exit()
                    RackSearch(img, tenantAndSite, deviceType)
