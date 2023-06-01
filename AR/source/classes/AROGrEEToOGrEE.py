import json
import logging
import traceback
from base64 import b64encode
from os.path import basename, dirname, realpath
from time import time
from typing import Any

from numpy import ndarray

from AR.source.interfaces.IARConverter import (
    IARConverter,
    IncorrectResponseError,
    OgreeMessage,
)
from AR.source.ocr.LabelProcessing import ReaderCroppedAndFullImage
from AR.source.ODBC import GetPosition, GetRoomOrientation
from common.Utils import CustomerAndSiteSpliter, ReadConf
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
        return self.GetJSON(f"/api/domains/{domainName}")["data"]

    def GetSite(self, siteName: str) -> dict[str, Any]:
        """Get site informations from OGrEE

        :param siteName: name of the location of the site in OGrEE
        :type siteName: str
        :raises IncorrectResponseError: if the site was not found in OGrEE
        :return: dict describing an OGrEE site
        :rtype: dict[str, Any]
        """
        return self.GetJSON(f"/api/sites/{siteName}")["data"]

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
        buildings = self.GetJSON(f"/api/sites/{siteData['name']}/buildings")["data"][
            "objects"
        ]
        if len(buildings) == 0:
            raise IncorrectResponseError(
                self.url,
                f"/api/sites/{siteData['name']}/buildings",
                message=f"No building found on api {self.url}",
            )
        roomsData = []
        for buildingData in buildings:
            roomsData = self.GetJSON(
                f"/api/rooms?name={roomIdentifier}&parentId={buildingData['id']}"
            )["data"]["objects"]
            if len(roomsData) > 0:
                break

        if len(roomsData) == 0:
            raise IncorrectResponseError(
                self.url,
                f"/api/sites/{siteData['name']}/buildings",
                message=f"No room with name {roomIdentifier} found in site {siteData['name']} on api {self.url}",
            )
        templates = []
        if buildingData["attributes"]["template"] != "":
            templates.append(
                self.GetJSON(
                    f"/api/bldg-templates/{buildingData['attributes']['template']}"
                )
            )["data"]
        if roomsData[0]["attributes"]["template"] != "":
            templates.append(
                self.GetJSON(
                    f"/api/bldg-templates/{roomsData[0]['attributes']['template']}"
                )
            )["data"]
        return (buildingData, roomsData[0], templates)

    def GetRack(
        self,
        roomData: dict[str, Any],
        rackName: str,
    ) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        """Get rack informations from OGrEE

        :param roomData: must contains "name", "id" and "domain"
        :type roomData: dict[str, Any]
        :param rackName: name of the rack in OGrEE
        :type rackName: str
        :raises IncorrectResponseError: if the rack was not found in dcTracck
        :return: dict describing the rack and its children, a list of dict describing the templates needed
        :rtype: tuple[dict[str, Any], list[dict[str, Any]]]
        """
        onlyRack = self.GetJSON(f"/api/rooms/{roomData['id']}/racks/{rackName}")["data"]
        rackData = self.GetJSON(f"/api/racks/{onlyRack['id']}/all")["data"]
        templates = self.GetTemplatesRec(rackData)
        return rackData, templates

    def GetTemplatesRec(self, objectData: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Recursively returns all children of the parent object and their templates

        :param dict[str,Any] parent_dctrack: parent object's data from dctrack
        :returns: a list of the children, a list of their templates
        :rtype: tuple[list[dict[str, Any]], list[dict[str, Any]]]
        """
        templates = []

        if objectData["attributes"]["template"] != "":
            templates.append(
                self.GetJSON(
                    f"/api/obj-templates/{objectData['attributes']['template']}"
                )
            )
        if "children" in objectData:
            for child in objectData["children"]:
                templates += self.GetTemplatesRec(child)

        return templates

    def RackSearch(
        self, img: ndarray, customerAndSite: str, deviceType: str, debug: bool = False
    ) -> str:
        """Perform OCR on a picture for a rack label, gets its info from OGrEE and convert it to OGrEE format

        :param img: the picture where the rack label is
        :type img: ndarray
        :param customerAndSite: [CUSTOMER].[SITE]
        :type customerAndSite: str
        :param deviceType: "rack" or "mdi"
        :type deviceType: str
        :return: a serialised message of OGrEE format containing all the data required to load the rack on OGrEE-3D-AR
        :rtype: str
        """
        ocrResults = []
        label = None

        start = time()
        # Split the customer name and the site name
        customer, site = CustomerAndSiteSpliter(customerAndSite)

        # Read RegexFile to have all infos
        pathToConfFile = f"{dirname(__file__)}/../../.conf.json"

        if debug:
            label = ["A106A", "pinq01"]  # debug

        else:
            regexp, roomList, type, background, colorRange = ReadConf(
                pathToConfFile, customer, site, deviceType
            )
            for i in range(len(regexp)):
                site, label, ocrResults = ReaderCroppedAndFullImage(
                    img,
                    site,
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
            domainData = self.GetDomain(customer)
            siteData = self.GetSite(site)
            buildingData, roomData, templates1 = self.GetBuildingAndRoom(
                siteData, label[0]
            )
            rackData, templates2 = self.GetRack(roomData, label[1])
            # Setting the data to send to Unity App
            dictionary = {
                "domain": OgreeMessage.FormatDict(domainData),
                "domainName": customer,
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
                "fbx": {},
            }
            # Serializing json
            json_object = json.dumps(dictionary, indent=4)

            # Debug
            dictionary = {
                "domain": domainData,
                "domainName": customer,
                "site": siteData,
                "siteName": site,
                "building": buildingData,
                "buildingName": buildingData["name"],
                "room": roomData,
                "roomName": roomData["name"],
                "rack": rackData,
                "rackName": rackData["name"],
                "templates": (templates1 + templates2),
                "fbx": {},
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
        """Get pictures of a model from OGrEE then build a fbx model with them

        :param data: OGrEE model
        :type data: dict[str, Any]
        :return: the path to an fbx model or "" if no picture were found in OGrEE
        :rtype: str
        """
        endpointBack = f"/gdcitdz/images/devices/rearpngimages/{data['modelId']}_R.png"
        endpointFront = (
            f"/gdcitdz/images/devices/frontpngimages/{data['modelId']}_F.png"
        )
        frontPic = self.GetFile(endpointFront)
        backPic = self.GetFile(endpointBack)
        frontPath = f"{self.outputPath}/pictures/{data['model']}-front.png"
        backPath = f"{self.outputPath}/pictures/{data['model']}-back.png"
        if frontPic != b"":
            with open(frontPath, "wb") as newPic:
                newPic.write(frontPic)
        if backPic != b"":
            with open(backPath, "wb") as newPic:
                newPic.write(backPic)
        if frontPic == b"" and backPic == b"":
            return ""
        return CreateFBX(
            width=data["dimWidth"] / 10,
            height=data["dimHeight"] / 10,
            depth=data["dimDepth"] / 10,
            front=frontPath if frontPic != b"" else "",
            back=backPath if backPic != b"" else "",
            name=data["model"].replace(" ", "-").replace(".", "-").lower(),
        )

    def GetList(self):
        """Not implemented"""
        pass
