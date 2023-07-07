import json
import logging
import traceback
from base64 import b64encode
from os.path import basename, dirname, realpath
from time import time
from typing import Any

import requests
from numpy import ndarray

from AR.source.interfaces.IARConverter import (
    IARConverter,
    IncorrectResponseError,
    OgreeMessage,
)
from AR.source.ocr.LabelProcessing import ReaderCroppedAndFullImage
from AR.source.ODBC import GetPosition, GetRoomOrientation
from common.Utils import ReadConf
from Converter.source.classes.OGrEEToOGrEE import OGrEEToOGrEE
from Converter.source.fbx.FbxBuilder import CreateFBX

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())


defaultAROutputPath = realpath(f"{dirname(realpath(__file__))}/../../output")


class AROGrEEToOGrEE(OGrEEToOGrEE, IARConverter):
    """Convert data from OGrEE to OGrEE-AR

    :param OGrEEToOGrEE: Base class of OGrEE-to-OGrEE converters
    :type OGrEEToOGrEE: OGrEEToOGrEE
    :param IARConverter:  Interface of AR converters
    :type IARConverter: IARConverter
    """

    def __init__(
        self,
        url: str,
        headersGET: dict[str, Any],
        headersPOST: dict[str, Any],
        outputPath: str | None = None,
        AROutputPath: str | None = None,
        **kw,
    ) -> None:
        """_summary_

        :param url: OGrEE
        :type url: str
        :param headersGET: _description_
        :type headersGET: dict[str, Any]
        :param headersPOST: _description_
        :type headersPOST: dict[str, Any]
        :param outputPath: _description_, defaults to None
        :type outputPath: str | None, optional
        :param AROutputPath: _description_, defaults to None
        :type AROutputPath: str | None, optional
        """
        self.AROutputPath = (
            realpath(AROutputPath) if AROutputPath is not None else defaultAROutputPath
        )
        super().__init__(url, headersGET, headersPOST, outputPath, **kw)

    def GetDomain(self, domainName: str) -> dict[str, Any]:
        """Create a domain for OGrEE
        :param domainName: name of the domain
        :type domainName: str
        :return: dict describing an OgrEE domain
        :rtype: dict[str, Any]
        """
        return self.GetJSON(f"api/domains/{domainName}")["data"]

    def GetSite(self, siteName: str) -> dict[str, Any]:
        """Get site informations from OGrEE

        :param siteName: name of the location of the site in OGrEE
        :type siteName: str
        :raises IncorrectResponseError: if the site was not found in OGrEE
        :return: dict describing an OGrEE site
        :rtype: dict[str, Any]
        """
        return self.GetJSON(f"api/sites/{siteName}")["data"]

    def GetBuildingAndRoom(
        self, siteData: dict[str, Any], roomIdentifier: str
    ) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
        """Get building and room informations from OGrEE

        :param siteData: must contains "name", "id" and "domain"
        :type siteData: dict[str, Any]
        :param roomIdentifier: name of the room in OGrEE
        :type roomIdentifier: str
        :raises IncorrectResponseError: if the room was not found in OGrEE
        :return: two dicts describing an OGrEE building and room and a list of dict containing their templates if needed
        :rtype: tuple[dict[str, Any], dict[str, Any], list[dict[str,Any]]]
        """
        buildings = self.GetJSON(f"api/sites/{siteData['name']}/buildings")["data"][
            "objects"
        ]
        if len(buildings) == 0:
            raise IncorrectResponseError(
                self.url,
                f"api/sites/{siteData['name']}/buildings",
                message=f"No building found on api {self.url}",
            )
        roomsData = []
        for buildingData in buildings:
            roomsData = self.GetJSON(
                f"api/rooms?name={roomIdentifier}&parentId={buildingData['id']}"
            )["data"]["objects"]
            if len(roomsData) > 0:
                break

        if len(roomsData) == 0:
            raise IncorrectResponseError(
                self.url,
                f"api/sites/{siteData['name']}/buildings",
                message=f"No room with name {roomIdentifier} found in site {siteData['name']} on api {self.url}",
            )
        templates = []
        if buildingData["attributes"]["template"] != "":
            templates.append(
                self.GetJSON(
                    f"api/bldg-templates/{buildingData['attributes']['template']}"
                )
            )["data"]
        if roomsData[0]["attributes"]["template"] != "":
            templates.append(
                self.GetJSON(
                    f"api/bldg-templates/{roomsData[0]['attributes']['template']}"
                )
            )["data"]
        return (buildingData, roomsData[0], templates)

    def GetRack(
        self,
        roomData: dict[str, Any],
        rackName: str,
    ) -> tuple[dict[str, Any], list[dict[str, Any]], list[str]]:
        """Get rack informations from OGrEE

        :param roomData: must contains "name", "id" and "domain"
        :type roomData: dict[str, Any]
        :param rackName: name of the rack in OGrEE
        :type rackName: str
        :raises IncorrectResponseError: if the rack was not found in dcTracck
        :return: dict describing the rack and its children, a list of dict describing the templates needed, a list of fbx paths
        :rtype: tuple[dict[str, Any], list[dict[str, Any]],list[str]]
        """
        onlyRack = self.GetJSON(f"api/rooms/{roomData['id']}/racks/{rackName}")["data"]
        rackData = self.GetJSON(f"api/racks/{onlyRack['id']}/all")["data"]
        templates, fbx = self.GetTemplatesAndFbxRec(rackData)
        return rackData, templates, fbx

    def GetTemplatesAndFbxRec(
        self, objectData: dict[str, Any]
    ) -> tuple[list[dict[str, Any]], dict[str, str]]:
        """
        Recursively returns all children of the parent object and their templates

        :param dict[str,Any] parent_dctrack: parent object's data from dctrack
        :returns: a list of the templates, a list of fbx paths
        :rtype:  tuple[list[dict[str, Any]],dict[str,str]]
        """
        templates = []
        fbx = {}
        if objectData["attributes"]["template"] != "":
            template = self.GetJSON(
                f"api/obj-templates/{objectData['attributes']['template']}"
            )["data"]
            templates.append(template)
            if template["fbxModel"] != "":
                fbx[template["slug"] + ".fbx"] = self.DownloadFbx(template["fbxModel"])
        if "children" in objectData:
            for child in objectData["children"]:
                childrenTemplates, childrenFbx = self.GetTemplatesAndFbxRec(child)
                templates += childrenTemplates
                for childFbx in childrenFbx:
                    fbx[childFbx] = childrenFbx[childFbx]

        return templates, fbx
    
    def DownloadFbx(self, url: str) -> dict[str, str]:
        """download fbx from url

        :param url: fbx url
        :type url: str
        :return: fbx data in bytes or b"" if the file could not be downloaded
        :rtype: str
        """
        try:
            response = requests.get(url)
            response.raise_for_status()  # Check for any errors

            log.debug("File downloaded successfully.")
            return b64encode(response.content).decode("ascii")
        except Exception as e:
            log.error(f"Error downloading fbx from {url} : ", str(e))
            return ""

    def UpdateDomainRec(self,objectData:dict[str,Any],domain:str) -> dict[str,Any]:
        
        objectData["domain"] = domain
        if "children" in objectData:
            for i in range(len(objectData["children"])):
                objectData["children"][i] = self.UpdateDomainRec(objectData["children"][i],domain)
        return objectData


    def RackSearch(
        self, img: ndarray, domain : str, site : str, deviceType: str, debug: str = ""
    ) -> str:
        """Perform OCR on a picture for a rack label, gets its info from OGrEE and convert it to OGrEE format

        :param img: the picture where the rack label is
        :type img: ndarray
        :param customerAndSite: [CUSTOMER].[SITE]
        :type customerAndSite: str
        :param deviceType: "rack" or "mdi"
        :type deviceType: str
        :param debug: if not empty, the function will skip picture read and will use this argument value as "ROOMNAME.RACKNAME"
        :type debug: str
        :return: a serialised message of OGrEE format containing all the data required to load the rack on OGrEE-3D-AR
        :rtype: str
        """
        ocrResults = []
        label = None
        start = time()

        # Read RegexFile to have all infos
        pathToConfFile = f"{dirname(__file__)}/../../.conf.json"

        if debug:
            label = debug.split(".")  # debug

        else:
            regexp, roomList, type, background, colorRange = ReadConf(
                pathToConfFile, domain, site, deviceType
            )
            for i in range(len(regexp)):
                label, ocrResults = ReaderCroppedAndFullImage(
                    img,
                    regexp[i],
                    deviceType,
                    background[i],
                    colorRange,
                    ocrResults,
                )
                if "Missing" not in label:
                    break

        if label is None or len(label) == 0 or "Missing" in label:
            return "Rack label could not be read"

        try:
            domainData = self.GetDomain(domain)
            siteData = self.GetSite(site)
            buildingData, roomData, templates1 = self.GetBuildingAndRoom(
                siteData, label[0]
            )
            rackData, templates2, fbx = self.GetRack(roomData, label[1])
            siteData = self.UpdateDomainRec(siteData,domain)
            buildingData = self.UpdateDomainRec(buildingData,domain)
            roomData = self.UpdateDomainRec(roomData,domain)
            rackData = self.UpdateDomainRec(rackData,domain)
            # Setting the data to send to Unity App
            dictionary = {
                "domain": OgreeMessage.FormatDict(domainData),
                "domainName": domain,
                "site": OgreeMessage.FormatDict(siteData),
                "siteName": site,
                "building": OgreeMessage.FormatDict(buildingData),
                "buildingName": buildingData["name"],
                "room": OgreeMessage.FormatDict(roomData),
                "roomName": roomData["name"],
                "rack": OgreeMessage.FormatDict(rackData),
                "rackName": rackData["name"],
                "templates": json.dumps(
                    [json.dumps(t) for t in (templates1 + templates2)]
                ),
                "fbx": json.dumps(fbx),
            }
            # Serializing json
            json_object = json.dumps(dictionary, indent=4)

            # Debug
            dictionary = {
                "domain": domainData,
                "domainName": domain,
                "site": siteData,
                "siteName": site,
                "building": buildingData,
                "buildingName": buildingData["name"],
                "room": roomData,
                "roomName": roomData["name"],
                "rack": rackData,
                "rackName": rackData["name"],
                "templates": (templates1 + templates2),
                "fbx": {name: fbx[name][10] for name in fbx},
            }
            with open(f"{self.AROutputPath}/output.json", "w") as output:
                output.write(json.dumps(dictionary, indent=4))
            log.info(f"the json returned is in {self.AROutputPath}/output.json")
            log.info(f"Total time: {time() - start} s ")
            log.info("End of the processing.")
            return json_object

        except IncorrectResponseError as e:
            raise e

        except Exception as e:
            raise e

    def MakeFBX(self, data: dict[str, Any]) -> str:
        """Not needed"""
        pass

    def GetList(self):
        """Not implemented"""
        pass
