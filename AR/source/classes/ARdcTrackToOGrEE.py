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
from Converter.source.classes.dcTrackToOGrEE import dcTrackToOGrEE
from Converter.source.fbx.FbxBuilder import CreateFBX

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())


defaultAROutputPath = realpath(f"{dirname(realpath(__file__))}/../../output")


class ARdcTrackToOGrEE(dcTrackToOGrEE, IARConverter):
    """Convert data from dcTrack to OGrEE-AR

    :param dcTrackToOGrEE: Base class of dcTrack-to-OGrEE converters
    :type dcTrackToOGrEE: dcTrackToOGrEE
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

        :param url: dcTrack
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
        """Create a domain for dcTrack
        :param domainName: name of the domain
        :type domainName: str
        :return: dict describing an OgrEE domain
        :rtype: dict[str, Any]
        """
        data = {"name": domainName, "id": domainName}
        return self.BuildDomain(data)

    def GetSite(self, locationName: str) -> dict[str, Any]:
        """Get site informations from dcTrack

        :param locationName: name of the location of the site in dcTrack
        :type locationName: str
        :raises IncorrectResponseError: if the site was not found in dcTrack
        :return: dict describing an OGrEE site
        :rtype: dict[str, Any]
        """
        payload = {
            "columns": [
                {
                    "name": "tiLocationName",
                    "filter": {"contains": f'"{locationName}"'},
                }
            ],
            "selectedColumns": ["name"],
        }
        searchResults = self.PostJSON("/api/v2/quicksearch/locations", payload)[
            "searchResults"
        ]
        if len(searchResults) == 0:
            raise IncorrectResponseError(
                self.url,
                "/api/v2/quicksearch/locations",
                message=f"Site {locationName} was not found on api {self.url}",
            )

        if len(searchResults) > 1:
            log.warning(
                f"Multiple locations found with the name {locationName}, taking the first one"
            )
        siteData = searchResults[0]
        siteData["attributes"] = {"orientation": "NW"}
        return self.BuildSite(siteData)

    def GetBuildingAndRoom(
        self, siteData: dict[str, Any], roomIdentifier: str
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Get building and room informations from dcTrack

        :param siteData: must contains "name", "id" and "domain"
        :type siteData: dict[str, Any]
        :param roomIdentifier: name of the room in dcTrack
        :type roomIdentifier: str
        :raises IncorrectResponseError: if the room was not found in dcTrack
        :return: two dicts describing an OGrEE building and room
        :rtype: tuple[dict[str, Any], dict[str, Any]]
        """
        buildingData = self.BuildBuilding(
            {
                "name": "building",  # ???
                "parentId": siteData["id"],
                "domain": siteData["domain"],
            }
        )

        payload = {
            "columns": [
                {
                    "name": "tiLocationName",
                    "filter": {"contains": f'"{roomIdentifier}"'},
                }
            ],
            "selectedColumns": ["name","id"],
        }
        searchResults = self.PostJSON("/api/v2/quicksearch/locations", payload)[
            "searchResults"
        ]
        if len(searchResults) == 0:
            raise IncorrectResponseError(
                self.url,
                "/api/v2/quicksearch/locations",
                message=f"Room {roomIdentifier} was not found in site {siteData['name']} on api {self.url}",
            )

        if len(searchResults) > 1:
            log.warning(
                f"Multiple rooms found with the name {roomIdentifier} in site {siteData['name']}, taking the first one"
            )
        roomDataJson = searchResults[0]
        roomOrientation = GetRoomOrientation(roomID=roomDataJson["id"])

        roomData = self.BuildRoom(
            {
                "name": roomDataJson["name"],
                "parentId": buildingData["id"],
                "domain": siteData["domain"],
                "attributes": {
                    "axisOrientation": ("+x" if roomOrientation[0] else "-x") + ("-y" if roomOrientation[0] else "+y"), 
                    "posXY": json.dumps({"x": 0.0, "y": 0.0}),  # ???
                    "posXYUnit": "m",
                    "size": json.dumps({"x": 21, "y": 39}),  # ???
                    "sizeUnit": "m",
                    "height": "4",  # ???
                    "heightUnit": "m",
                    "rotation": "0",
                    "template": "",
                    "technical": '{"left":5,"right":5,"top":0,"bottom":0}',
                    "floorUnit": "m",
                },
            }
        )
        return (buildingData, roomData)

    def GetRack(
        self,
        roomData: dict[str, Any],
        rackName: str,
    ) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, str]]:
        """Get rack informations from dcTrack

        :param roomData: must contains "name", "id" and "domain"
        :type roomData: dict[str, Any]
        :param rackName: name of the rack in dcTrack
        :type rackName: str
        :raises IncorrectResponseError: if the rack was not found in dcTracck
        :return: dict describing the rack and its children, a list of dict describing the templates needed and a dict of fbx models
        :rtype: tuple[dict[str, Any], list[dict[str, Any]], dict[str, str]]
        """
        payload = {
            "columns": [
                {"name": "tiName", "filter": {"contains": rackName}},
                {"name": "tiLocationName", "filter": {"eq": roomData["name"]}},
                {"name": "tiClass", "filter": {"contains": "Cabinet"}},
            ],
            "selectedColumns": [
                {"name": "id"},
                {"name": "tiName"},
                {"name": "tiClass"},
                {"name": "modelId"},
            ],
        }
        searchResults = self.PostJSON("api/v2/quicksearch/items", payload)[
            "searchResults"
        ]["items"]

        if len(searchResults) == 0:
            raise IncorrectResponseError(
                self.url,
                "/api/v2/quicksearch/items",
                message=f"Rack {rackName} was not found in room {roomData['name']} on api {self.url}",
            )

        if len(searchResults) > 1:
            log.warning(
                f"Multiple racks found with the name {rackName} in room {roomData['name']}, taking the first one"
            )

        rackDataJson = searchResults[0]

        rackModel = self.GetJSON(f"api/v2/models/{rackDataJson['modelId']}")
        rackModel["category"] = "rack"
        rackTemplate = self.BuildTemplate(rackModel)
        rackFBX = self.MakeFBX(rackModel)
        rackTemplate["fbxModel"] = "true" if rackFBX != "" else ""
        rackDataJson["sizeWDHmm"] = rackTemplate["sizeWDHmm"]
        rackDataJson["parentId"] = roomData["id"]
        rackDataJson["domain"] = roomData["domain"]
        rackDataJson["template"] = rackTemplate["slug"]
        rackData = self.BuildRack(rackDataJson)

        position = GetPosition(rackName=rackDataJson["tiName"])
        if position is not None:
            rackData["attributes"]["posXY"] = json.dumps(
                {
                    "x": position[0] / 1000,
                    "y": position[1] / 1000,
                }
            )
            rackData["attributes"]["posXYUnit"] = "m"
            if ((position[2] == "East" and roomData["attributes"]["axisOrientation"] == "-x+y") or (position[2] == "West" and roomData["attributes"]["axisOrientation"] == "+x+y")):
                rackData["attributes"]["orientation"] = "rear"
            else :
                rackData["attributes"]["orientation"] = "front"

        rackDataJson["id"] = rackData["id"]
        templates = [rackTemplate]
        fbxPaths = [rackFBX] if rackFBX != "" else []
        templatesChildren, children, fbxChildren = self.GetChildren(rackDataJson)
        templates += templatesChildren
        fbxPaths += fbxChildren
        rackData["children"] = children
        fbx = {}

        for path in fbxPaths:
            with open(path, "rb") as fbxFile:
                fbx[basename(path)] = b64encode(fbxFile.read()).decode("ascii")
        return rackData, templates, fbx

    def GetChildren(
        self, parent_dctrack: dict[str, Any]
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
        """
        Recursively returns all children of the parent object and their templates

        :param dict[str,Any] parent_dctrack: parent object's data from dctrack
        :returns: a list of the children, a list of their templates and a list of paths to their fbx models
        :rtype: tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]
        """
        templates = []
        childrenOgree = []
        fbx = []

        if parent_dctrack["tiClass"] == "Cabinet":
            childrenDctrack = self.PostJSON(
                "api/v2/quicksearch/items",
                {
                    "columns": [
                        {
                            "name": "cmbCabinet",
                            "filter": {"contains": parent_dctrack["tiName"]},
                        }
                    ],
                    "selectedColumns": [
                        {"name": "id"},
                        {"name": "modelId"},
                        {"name": "tiName"},
                        {"name": "tiMounting"},
                        {"name": "cmbUPosition"},
                        {"name": "radioCabinetSide"},
                        {"name": "radioDepthPosition"},
                        {"name": "tiClass"},
                        {"name": "cmbChassis"},
                    ],
                },
            )["searchResults"]["items"]
        else:
            childrenDctrack = self.PostJSON(
                "api/v2/quicksearch/items",
                {
                    "columns": [
                        {
                            "name": "cmbChassis",
                            "filter": {"contains": parent_dctrack["tiName"]},
                        }
                    ],
                    "selectedColumns": [
                        {"name": "id"},
                        {"name": "modelId"},
                        {"name": "tiName"},
                        {"name": "tiMounting"},
                        {"name": "cmbUPosition"},
                        {"name": "radioCabinetSide"},
                        {"name": "radioDepthPosition"},
                        {"name": "tiClass"},
                    ],
                },
            )["searchResults"]["items"]
        for childJson in childrenDctrack:
            if childJson["tiName"] == parent_dctrack["tiName"] or (
                parent_dctrack["tiClass"] == "Cabinet" and "cmbChassis" in childJson
            ):
                continue

            childModel = self.GetJSON(f"api/v2/models/{childJson['modelId']}")
            childfbx = self.MakeFBX(childModel)
            childModel["category"] = "device"
            childTemplate = self.BuildTemplate(childModel)
            childTemplate["fbxModel"] = "true" if childfbx != "" else ""
            templates.append(childTemplate)
            fbx.append(childfbx)

            childJson["parentId"] = parent_dctrack["id"]
            childJson["sizeWDHmm"] = childTemplate["sizeWDHmm"]
            childJson["template"] = childTemplate["slug"]
            childOgree = self.BuildDevice(childJson)

            # Check if child is mounted on U pos
            if "Rackable" in childJson["tiMounting"]:
                if str.isdigit(childJson["cmbUPosition"]):
                    childOgree["attributes"]["slot"] = f"u{childJson['cmbUPosition']}"
                else:
                    childOgree["attributes"]["posU"] = childJson["cmbUPosition"]

            # Check if child is mounted in PDU slot
            elif "ZeroU" in childJson["tiMounting"]:
                isInSlot = True
                # Rack side
                if "Left" in childJson["radioCabinetSide"]:
                    childOgree["attributes"]["slot"] = "pduLeft"
                elif "Right" in childJson["radioCabinetSide"]:
                    childOgree["attributes"]["slot"] = "pduRight"
                else:
                    isInSlot = False

                # Rack Depth
                if "Center" in childJson["radioDepthPosition"]:
                    childOgree["attributes"]["slot"] += "Center"
                elif "Front" in childJson["radioDepthPosition"]:
                    childOgree["attributes"]["slot"] += "Front"
                elif "Rear" in childJson["radioDepthPosition"]:
                    childOgree["attributes"]["slot"] += "Rear"
                else:
                    isInSlot = False

                if not isInSlot:
                    childOgree["attributes"]["posU"] = childJson["cmbUPosition"]

            # Default
            else:
                childOgree["attributes"]["posU"] = "0"

            childJson["id"] = childOgree["id"]
            templatesChildChildren, childChildren, fbxChildChildren = self.GetChildren(
                childJson
            )
            templates += templatesChildChildren
            fbx += fbxChildChildren
            childOgree["children"] = childChildren
            childrenOgree.append(childOgree)
        return templates, childrenOgree, fbx

    def RackSearch(
        self, img: ndarray, customerAndSite: str, deviceType: str, debug: bool = False
    ) -> str:
        """Perform OCR on a picture for a rack label, gets its info from dcTrack and convert it to OGrEE format

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

        regexp, roomList, type, background, colorRange = ReadConf(
            pathToConfFile, customer, site, deviceType
        )
        if debug:
            label = ["C8", "B12"]  # debug

        else:
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

        if len(label[0]) > 3:
            label[0] = label[0][3::]

        try:
            domainData = self.GetDomain(customer)
            siteData = self.GetSite(site)
            buildingData, roomData = self.GetBuildingAndRoom(siteData, label[0])
            rackData, templates, fbx = self.GetRack(roomData, label[1])
            # Setting the data to send to Unity App
            dictionary = {
                "domain" : OgreeMessage.FormatDict(domainData),
                "domainName" : customer,
                "site": OgreeMessage.FormatDict(siteData),
                "siteName": site,
                "building": OgreeMessage.FormatDict(buildingData),
                "buildingName": buildingData["name"],
                "room": OgreeMessage.FormatDict(roomData),
                "roomName": roomData["name"],
                "rack": OgreeMessage.FormatDict(rackData),
                "rackName": rackData["name"],
                "templates": json.dumps([json.dumps(t) for t in templates]),
                "fbx": json.dumps(fbx),
            }
            # Serializing json
            json_object = json.dumps(dictionary, indent=4)

            # Debug
            dictionary = {
                "domain" : domainData,
                "domainName" : customer,
                "site": siteData,
                "siteName": site,
                "building": buildingData,
                "buildingName": buildingData["name"],
                "room": roomData,
                "roomName": roomData["name"],
                "rack": rackData,
                "rackName": rackData["name"],
                "templates": templates,
                "fbx": {name: "bits" for name in fbx},
            }
            with open(f"{self.AROutputPath}/output.json", "w") as output:
                output.write(json.dumps(dictionary, indent=4))
            log.info(f"the json returned is in {self.AROutputPath}/output.json")
            log.info(f"Total time: {time() - start} s ")
            log.info("End of the processing.")
            return json_object

        except IncorrectResponseError as e:
            log.error(e)
            log.error(f"Required data may be missing on {e.url}")
            log.debug(traceback.format_exc())
            return e.__str__()

        except Exception as e:
            log.error(e)
            log.debug(traceback.format_exc())
            return e.__str__()

    def MakeFBX(self, data: dict[str, Any]) -> str:
        """Get pictures of a model from dcTrack then build a fbx model with them

        :param data: dcTrack model
        :type data: dict[str, Any]
        :return: the path to an fbx model or "" if no picture were found in dcTrack
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
