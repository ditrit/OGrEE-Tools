import json
from copy import deepcopy
from os import listdir
from os.path import dirname, isfile, join, realpath
from typing import Any

from common.Utils import GetAllComponents
from Converter.source.classes.BaseConverter import BaseConverter
from Converter.source.interfaces.IToOGrEE import IToOGrEE

defaultOutputPath = realpath(f"{dirname(realpath(__file__))}/../../output/OGrEE")


class dcTrackToOGrEE(IToOGrEE, BaseConverter):
    """Convert data from dcTrack to OGrEE

    :param IToOGrEE: Interface of to-OGrEE converters
    :type IToOGrEE: ItoOGrEE
    :param BaseConverter: Base class of all converters
    :type BaseConverter: BaseConverter
    """

    def __init__(
        self,
        url: str,
        headersGET: dict[str, Any],
        headersPOST: dict[str, Any],
        outputPath: str | None = None,
        **kw,
    ) -> None:
        """

        :param url: API url of the source
        :type url: str
        :param headersGET: headers of the GET requests
        :type headersGET: dict[str, Any]
        :param headersPOST: headers of the POST requests
        :type headersPOST: dict[str, Any]
        :param outputPath: where the data will be saved, defaults to Converter/output/OGrEE
        :type outputPath: str | None, optional
        """
        self.outputPath = (
            realpath(outputPath) if outputPath is not None else defaultOutputPath
        )
        self.templatePath = realpath(f"{self.outputPath}/templates")
        super().__init__(url=url, headersGET=headersGET, headersPOST=headersPOST, **kw)

    def BuildDomain(self, data: dict[str, Any]) -> dict[str, Any]:
        """Build a domain from dcTrack data

        :param data: dcTrack data,
            - must contains "name"
            - can contains "description", "id", "attributes" and "children" keys
            - all other keys will be ignored
        :type data: dict[str, Any]
        :return: a dict describing an OGrEE domain
        :rtype: dict[str, Any]
        """
        return {
            "name": data["name"],
            "id": data["id"] if "id" in data else data["name"],
            "parentId": None,
            "category": "domain",
            "description": data["description"] if "description" in data else [],
            "domain": data["name"],
            "attributes": data["attributes"]
            if "attributes" in data
            else {"color": "ffffff"},
            "children": data["children"] if "children" in data else [],
        }

    def BuildSite(self, data: dict[str, Any]) -> dict[str, Any]:
        """Build a site from dcTrack data

        :param data: dcTrack data,
            - must contains "name"
            - can contains "description", "parentId", "domain", "attributes" and "children" keys
            - all other keys will be ignored
        :type data: dict[str, Any]
        :return: a dict describing an OGrEE site
        :rtype: dict[str, Any]
        """
        result = {
            "name": data["name"],
            "parentId": data["parentId"] if "parentId" in data else None,
            "category": "site",
            "description": data["description"] if "description" in data else [],
            "domain": data["domain"]
            if "domain" in data
            else data["parentId"]
            if "parentId" in data
            else None,
            "attributes": data["attributes"] if "attributes" in data else {},
            "children": data["children"] if "children" in data else [],
        }
        result["id"] = f"{result['parentId']}.{result['name']}"
        result["hierarchyName"] = f"{result['parentId']}.{result['name']}"
        return result

    def BuildBuilding(self, data: dict[str, Any]) -> dict[str, Any]:
        """Build a building from dcTrack data

        :param data: dcTrack data,
            - must contains "name"
            - can contains "description", "parentId", "domain", "attributes" and "children" keys
            - all other keys will be ignored
        :type data: dict[str, Any]
        :return: a dict describing an OGrEE building
        :rtype: dict[str, Any]
        """
        result = {
            "name": data["name"],
            "parentId": data["parentId"] if "parentId" in data else None,
            "category": "building",
            "description": data["description"] if "description" in data else [],
            "domain": data["domain"] if "domain" in data else None,
            "attributes": data["attributes"]
            if "attributes" in data
            else {
                "posXY": json.dumps({"x": 0.0, "y": 0.0}),  # ???
                "posXYUnit": "m",
                "size": json.dumps({"x": 100.0, "y": 100.0}),  # ???
                "sizeUnit": "m",
                "height": "5",  # ???
                "heightUnit": "m",
                "rotation": "0",
            },
            "children": data["children"] if "children" in data else None,
        }
        result["id"] = f"{result['parentId']}.{result['name']}"
        result["hierarchyName"] = f"{result['parentId']}.{result['name']}"
        return result

    def BuildRoom(self, data: dict[str, Any]) -> dict[str, Any]:
        """Build a room from dcTrack data

        :param data: dcTrack data,
            - must contains "name"
            - can contains "description", "parentId", "domain", "attributes" and "children" keys
            - all other keys will be ignored
        :type data: dict[str, Any]
        :return: a dict describing an OGrEE room
        :rtype: dict[str, Any]
        """
        result = {
            "name": data["name"],
            "parentId": data["parentId"] if "parentId" in data else None,
            "category": "room",
            "description": data["description"] if "description" in data else [],
            "domain": data["domain"] if "domain" in data else None,
            "attributes": data["attributes"]
            if "attributes" in data
            else {
                "axisOrientation": "+x+y",
                "rotation": "0",
                "posXY": json.dumps({"x": 0.0, "y": 0.0}),  # ???
                "posXYUnit": "m",
                "size": json.dumps({"x": 100.0, "y": 100.0}),  # ???
                "sizeUnit": "m",
                "height": "4",  # ???
                "heightUnit": "m",
                "template": "",
                "floorUnit": "t",
            },
            "children": data["children"] if "children" in data else [],
        }
        result["id"] = f"{result['parentId']}.{result['name']}"
        result["hierarchyName"] = f"{result['parentId']}.{result['name']}"
        return result

    def BuildRack(self, data: dict[str, Any]) -> dict[str, Any]:
        """Build a rack from dcTrack data

        :param data: dcTrack data,
            - must contains "tiName" and "sizeWDHmm"
            - can contains "description", "parentId", "domain", "attributes","template" and "children" keys
            - all other keys will be ignored
        :type data: dict[str, Any]
        :return: a dict describing an OGrEE rack
        :rtype: dict[str, Any]
        """
        result = {
            "name": data["tiName"],
            "parentId": data["parentId"] if "parentId" in data else None,
            "category": "rack",
            "description": data["description"] if "description" in data else [],
            "domain": data["domain"] if "domain" in data else None,
            "attributes": {
                "orientation": "front",  # ???
                "posXY": json.dumps({"x": 0.0, "y": 0.0}),  # ???
                "posXYUnit": "t",
                "size": json.dumps(
                    {
                        "x": float(data["sizeWDHmm"][0]) / 10,
                        "y": float(data["sizeWDHmm"][1]) / 10,
                    }
                ),
                "sizeUnit": "cm",
                "height": str(float(data["sizeWDHmm"][2]) / 10),
                "heightUnit": "cm",
                "template": data["template"] if "template" in data else "",
            },
            "children": data["children"] if "children" in data else [],
        }
        result["id"] = f"{result['parentId']}.{result['name']}"
        result["hierarchyName"] = f"{result['parentId']}.{result['name']}"
        return result

    def BuildDevice(self, data: dict[str, Any]) -> dict[str, Any]:
        """Build a device from dcTdevice data

        :param data: dcTrack data,
            - must contains "tiName", "tiMounting", "cmbUPosition" (if "tiMounting"'s value is "Rackable"), "radioCabinetSide" and "radioDepthPosition" (if "tiMounting"'s value is "ZeroU") and "sizeWDHmm"
            - can contains "description", "parentId", "domain", "attributes","template", and "children" keys
            - all other keys will be ignored
        :type data: dict[str, Any]
        :return: a dict describing an OGrEE rack
        :rtype: dict[str, Any]
        """
        result = {
            "name": data["tiName"],
            "parentId": data["parentId"] if "parentId" in data else None,
            "category": "device",
            "description": [],
            "domain": data["domain"] if "domain" in data else None,
            "attributes": {
                "orientation": "front",  # Needs more precision
                "size": json.dumps(
                    {
                        "x": data["sizeWDHmm"][0],
                        "y": data["sizeWDHmm"][1],
                    }
                ),
                "sizeUnit": "mm",
                "height": data["sizeWDHmm"][2],
                "heightUnit": "mm",
                "template": data["template"] if "template" in data else "",
                "posU": "",
                "slot": "",
            },
            "children": data["children"] if "children" in data else [],
        }
        result["id"] = f"{result['parentId']}.{result['name']}"
        result["hierarchyName"] = f"{result['parentId']}.{result['name']}"

        # Check if child is mounted on U pos
        if "Rackable" in data["tiMounting"]:
            if str.isdigit(data["cmbUPosition"]):
                result["attributes"]["slot"] = f"u{data['cmbUPosition']}"
            else:
                result["attributes"]["posU"] = data["cmbUPosition"]

        # Check if child is mounted in PDU slot
        elif "ZeroU" in data["tiMounting"]:
            isInSlot = True
            # Rack side
            if "Left" in data["radioCabinetSide"]:
                result["attributes"]["slot"] = "pduLeft"
            elif "Right" in data["radioCabinetSide"]:
                result["attributes"]["slot"] = "pduRight"
            else:
                isInSlot = False

            # Rack Depth
            if "Center" in data["radioDepthPosition"]:
                result["attributes"]["slot"] += "Center"
            elif "Front" in data["radioDepthPosition"]:
                result["attributes"]["slot"] += "Front"
            elif "Rear" in data["radioDepthPosition"]:
                result["attributes"]["slot"] += "Rear"
            else:
                isInSlot = False

            if not isInSlot:
                result["attributes"]["posU"] = data["cmbUPosition"]

        # Default
        else:
            result["attributes"]["posU"] = "0"

        return result

    def BuildTemplate(self, data: dict[str, Any]) -> dict[str, Any]:
        """Build a template from dcTrack data

        :param data: dcTrack data,
            - must contains "model", "dimHeight", "dimDepth", "dimWidth", "make", "category", "class", "powerPorts", "dataPorsts", "ruHeight" (if "category"'s value  is "rack")
            - all other keys will be ignored
        :type data: dict[str, Any]
        :return: a dict describing an OGrEE template
        :rtype: dict[str, Any]
        """
        uSize = 44.45
        files = [
            f.split(".")[0]
            for f in listdir(self.templatePath)
            if isfile(join(self.templatePath, f))
        ]
        if data["model"] in files:
            with open(f"{self.templatePath}/{data['model']}.json") as componentJSON:
                return json.loads(componentJSON.read())
        saveTemplate = True
        template = {
            "slug": data["model"].replace(" ", "-").replace(".", "-").lower(),
            "description": data["make"],
            "category": data["category"],
            "sizeWDHmm": [
                data["dimHeight"] if "Rack PDU" in data["class"] else data["dimWidth"],
                data["dimDepth"],
                data["dimWidth"] if "Rack PDU" in data["class"] else data["dimHeight"],
            ],
            "fbxModel": "",
            "attributes": {
                "vendor": data["make"],
                "model": data["model"],
                "type": "",
            },
            "colors": [],
            "components": [],
            "slots": [],
        }

        ports = data["powerPorts"] + data["dataPorts"]

        if len(ports) > 0:
            components = GetAllComponents()
            offsetX = 0
            offsetY = template["sizeWDHmm"][1] - 1
            offsetZ = 0
            for component in ports:
                if component["connector"] in components:
                    componentOgree = deepcopy(components[component["connector"]])
                    componentOgree["location"] = component["portName"]
                else:
                    saveTemplate = False
                    componentOgree = {
                        "location": component["portName"],
                        "type": "Power (AC)"
                        if component in data["powerPorts"]
                        else "Data",
                        "elemOrient": "",
                        "elemPos": [],
                        "elemSize": [15, 15, 15],
                        "labelPos": "front",
                        "color": "000000",
                        "attributes": {"factor": component["connector"]},
                    }

                size = componentOgree["elemSize"]
                offsetX += size[0]
                if offsetX > template["sizeWDHmm"][0]:
                    offsetX = 0
                    offsetY -= (
                        max([i["elemSize"][1] for i in template["components"]]) * 2
                    )
                else:
                    offsetX -= size[0]
                offsetY -= size[1]
                if offsetY < 0:
                    offsetY = template["sizeWDHmm"][1] - 1
                    offsetZ += max([i["elemSize"][2] for i in template["components"]])
                else:
                    offsetY += size[1]
                componentOgree["elemPos"] = [offsetX, offsetY - size[1], offsetZ]
                template["components"].append(componentOgree)
                offsetX += size[0]

        if data["category"] == "rack":
            # U slots
            for i in range(data["ruHeight"]):
                template["slots"].append(
                    {
                        "location": f"u{i+1}",
                        "type": "u",
                        "elemOrient": "horizontal",
                        "elemPos": [
                            data["dimWidth"] * 0.1,
                            data["dimDepth"] * 0.1,
                            uSize * i,
                        ],
                        "elemSize": [
                            data["dimWidth"] * 0.8,
                            data["dimDepth"] * 0.8,
                            uSize,
                        ],
                        "mandatory": "no",
                        "labelPos": "frontrear",
                        "color": "b0e0e6",
                    }
                )
            # PDU : 3 left, 3 right

            # Right front
            template["slots"].append(
                {
                    "location": "pduRightFront",
                    "type": "pdu",
                    "elemOrient": "vertical",
                    "elemPos": [data["dimWidth"] - 60, 160, 0],
                    "elemSize": [1331, 80, 60],
                    "mandatory": "no",
                    "labelPos": "bottom",
                    "color": "ffff00",
                }
            )

            # Right rear
            template["slots"].append(
                {
                    "location": "pduRightRear",
                    "type": "pdu",
                    "elemOrient": "vertical",
                    "elemPos": [data["dimWidth"] - 60, 0, 0],
                    "elemSize": [1331, 80, 60],
                    "mandatory": "no",
                    "labelPos": "bottom",
                    "color": "ffff00",
                }
            )

            # Right center
            template["slots"].append(
                {
                    "location": "pduRightCenter",
                    "type": "pdu",
                    "elemOrient": "vertical",
                    "elemPos": [data["dimWidth"] - 60, 80, 0],
                    "elemSize": [1331, 80, 60],
                    "mandatory": "no",
                    "labelPos": "bottom",
                    "color": "ffff00",
                }
            )

            # Left front
            template["slots"].append(
                {
                    "location": "pduLeftFront",
                    "type": "pdu",
                    "elemOrient": "vertical",
                    "elemPos": [0, 160, 0],
                    "elemSize": [1331, 80, 60],
                    "mandatory": "no",
                    "labelPos": "top",
                    "color": "ffff00",
                }
            )

            # Left rear
            template["slots"].append(
                {
                    "location": "pduLeftRear",
                    "type": "pdu",
                    "elemOrient": "vertical",
                    "elemPos": [0, 0, 0],
                    "elemSize": [1331, 80, 60],
                    "mandatory": "no",
                    "labelPos": "top",
                    "color": "ffff00",
                }
            )

            # Left center
            template["slots"].append(
                {
                    "location": "pduLeftCenter",
                    "type": "pdu",
                    "elemOrient": "vertical",
                    "elemPos": [0, 80, 0],
                    "elemSize": [1331, 80, 60],
                    "mandatory": "no",
                    "labelPos": "top",
                    "color": "ffff00",
                }
            )

        if saveTemplate:
            with open(f"{self.templatePath}/{data['model']}.json", "x") as newTemplate:
                newTemplate.write(json.dumps(template, indent=4))
        return template
