"""
**Start an http server on localhost:5002**
"""
import argparse
import logging
import os
import socket
import time
import traceback

import cv2
import numpy as np
from flask import Flask, request
from gevent.pywsgi import WSGIServer

import common.Utils as Utils
from AR.source.classes.ARdcTrackToOGrEE import ARdcTrackToOGrEE
from AR.source.classes.AROGrEEToOGrEE import AROGrEEToOGrEE

IP = "0.0.0.0"
PORT = 5002

# set the project root directory as the static folder
app = Flask(__name__)
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())

#####################################################################################################################
#####################################################################################################################


@app.route("/picture", methods=["POST"])
def ReadPicture()->str:
    """
    Reads incoming data from Unity and call ogLabelReader to process it.
    Returns a json containing tenant,site,building,room and rack if the request was to read a label
    
    :returns: a serialised JSON containing the requested data
    :rtype: str
    """
    try:
            # content to get form parameter
            log.info("Beginning the processing of the image...")
            img = request.files["labelRack"].read()
            deviceType = request.form["deviceType"]

            # Convert byte-like image into a numpy array, then into an array usable with opencv
            nparr = np.frombuffer(img, np.ubyte)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            env = Utils.ReadEnv(os.path.realpath(f"{os.path.dirname(__file__)}/../.env.json"))
            if env["database"].lower() == "dctrack":
                converter = ARdcTrackToOGrEE(env["api_url"], env["headers"], {"Content-Type": "application/json"})
            else :
                converter = AROGrEEToOGrEE(env["api_url"], env["headers"], {"Content-Type": "application/json"})
            return converter.RackSearch(img, env["domain"],env["site"], deviceType,args["debug"])
    except Exception:
        traceback.print_exc()
        return traceback.format_exc()

#####################################################################################################################
#####################################################################################################################


@app.route("/list", methods=["POST"])
def GetList()->str:
    """
    Reads incoming data from Unity and call ogLabelReader to process it.
    Returns a list of the names of the children of an object if the request was to get them
    
    :returns: a serialised JSON containing the requested data
    :rtype: str
    """
    return ""


#####################################################################################################################
#####################################################################################################################


@app.route("/", methods=["GET"])
def GetTest()->str:
    """
    Allows to test the connexion

    :returns: the message "connected to the OGrEE-CONVERTER"
    :rtype: str
    """
    return "connected to the OGrEE-CONVERTER"


#####################################################################################################################
#####################################################################################################################
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Perform OCR from data (image + tenant) sent from Hololens"
    )
    parser.add_argument(
        "--verbose",
        choices=["INFO", "WARNING", "ERROR", "DEBUG"],
        help="""Specify the verbose level""",
        default="INFO",
    )
    parser.add_argument(
        "--debug",
        help="""debugging""",
        action="store_true",
    )
    args = vars(parser.parse_args())
    numeric_level = getattr(logging, args["verbose"].upper())
    logging.basicConfig(
        filename=os.path.dirname(os.path.abspath(__file__)) + "/server.log",
        format=f"%(asctime)s %(levelname)s %(name)s : %(message)s",
        level=numeric_level,
    )
    
    print(f"server running on {socket.gethostbyname(socket.gethostname())}:{PORT}")
    http_server = WSGIServer((IP, PORT), app)
    http_server.serve_forever()
