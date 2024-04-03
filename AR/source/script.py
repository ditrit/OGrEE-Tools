
import argparse
from io import TextIOWrapper
import os
import logging
from pydoc import apropos
from typing import Any
import common.Utils as Utils
from AR.source.classes.ARdcTrackToOGrEE import ARdcTrackToOGrEE
import json

def main(roomName : str, devices: bool, fbx:bool):
    env = Utils.ReadEnv(os.path.realpath(f"{os.path.dirname(__file__)}/../.env.json"))
    converter = ARdcTrackToOGrEE(env["api_url"], env["headers"], {"Content-Type": "application/json"},fbx)
    domainData = converter.GetDomain(env["domain"])
    siteData = converter.GetSite(domainData,env["site"])
    buildingData, roomData = converter.GetBuildingAndRoom(siteData, roomName)
    loadedTemplates=[]
    items = converter.PostJSON(
                "/api/v2/quicksearch/items?pageSize=0",
                {
                    "columns": [
                        {"name": "tiRoomNodeCode", "filter": {"eq": f'"{roomName}"'}},
                    ]
                },
            )["searchResults"]["items"]
    with open("output.ocli","w") as file:
        for item in items:
            if "cmbCabinet" not in item:
                print(f"ALERT : {item['tiName']} is not a rack and is not racked in room {item['tiRoomNodeCode']}")
                continue
            if item["tiClass"] != "Cabinet":
                continue
            print(item["tiName"])
            rackData, templates, fbx = converter.GetRack(roomData, item['tiName'],devices)
            if rackData['attributes']['template'] not in loadedTemplates:
                file.write(f".template:{converter.templatePath}/{rackData['attributes']['template']}.json\n")
                loadedTemplates.append(rackData['attributes']['template'])
            file.write(f'+rk:/P/NOE/BI2/{roomName}/{rackData["name"]}@{rackData["attributes"]["posXYZ"]}@m@[0,0,0]@{rackData["attributes"]["template"]}\n')
            loadedTemplates = WriteChildren(loadedTemplates, file,converter,roomName,rackData)


def WriteChildren(loadedTemplates :list[str], file : TextIOWrapper,converter : ARdcTrackToOGrEE, roomName : str, parent : dict[str, Any]):
    for child in parent["children"]:
        if child['attributes']['template'] not in loadedTemplates:
            file.write(f".template:{converter.templatePath}/{child['attributes']['template']}.json\n")
            loadedTemplates.append(child['attributes']['template'])
        file.write(f'+dv:/P/NOE/BI2/{roomName}/{parent["name"]}/{child["name"]}@{child["attributes"]["slot"]}@{child["attributes"]["template"]}\n')
        loadedTemplates = WriteChildren(loadedTemplates,file,converter,roomName,child)
    return loadedTemplates

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract data from dcTrack"
    )
    parser.add_argument(
        "--verbose",
        help="""Specify the verbosity level""",
        default="INFO",
    )
    parser.add_argument(
        "--devices",
        action="store_true",
        help="""convert devices too""",
    )
    parser.add_argument(
        "--fbx",
        action="store_true",
        help="""convert fbx too, only useful with --devices""",
    )
    parser.add_argument(
        "--room",
        help="""room name (i.e. C8)""",
        required=True
    )
    args = vars(parser.parse_args())
    numeric_level = getattr(logging, args["verbose"].upper())
    logging.basicConfig(
        filename=os.path.dirname(os.path.abspath(__file__)) + "/server.log",
        format=f"%(asctime)s %(levelname)s %(name)s : %(message)s",
        level=numeric_level,
    )
    main(args["room"],args["devices"],args["fbx"])
