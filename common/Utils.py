"""
**Utility functions**
"""
import logging
import sys
from os.path import exists
import json
import re
from os.path import isfile
import json
from os import listdir
import os
from typing import Any

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())

#####################################################################################################################
#####################################################################################################################


def ReadEnv(pathToEnvFile: str) -> tuple[str, dict[str, str], str]:
    """Read information in the env.json to setup API request. Returns url, token, headers and endpoint for the API."""
    file_exists = exists(pathToEnvFile)
    if file_exists:
        f = open(pathToEnvFile, "r")
        data = json.load(f)
        url = data["api_url"]
        token = data["api_token"]
        headers = {"Authorization": token}
        database = data["database"]
        f.close()
        return url, headers, database
    else:
        log.warning(
            "Cannot find .env.json file in the root (GetUrlAndToken in ogLblUtils.py)"
        )
        sys.exit()


#####################################################################################################################
#####################################################################################################################


def ReadConf(
    pathToRegexFile: str, customer: str, site: str, deviceType: str
) -> tuple[list[str], list[str], list[str], list[str], int]:
    """
    Read information in the conf.json to have different parameters. Returns a list of regexp (corresponding to the provided customer, site, deviceType),
    a list of the background color for each regexp and a unique color Range (sensitivity for the color).
    """
    file_exists = exists(pathToRegexFile)
    isFirstMatch = True
    regexp = []
    roomList = []
    type = []
    background = []
    if file_exists:
        f = open(pathToRegexFile, "r")
        data = json.load(f)
        test = data["tenants"]
        for j in range(len(test)):
            colorRange = test[j]["range"]
            if test[j]["customer"] == customer:
                attributes = test[j]["regexps"]
                for i in range(len(attributes)):
                    if attributes[i]["type"] == deviceType:
                        if attributes[i]["site"] == site:
                            regexp.append(attributes[i]["regexp"])
                            roomList.append(attributes[i]["room"])
                            type.append(attributes[i]["type"])
                            background.append(attributes[i]["background"])
                            if isFirstMatch:
                                log.debug(
                                    f"Found a match for device type {deviceType} and {site}:"
                                )
                                isFirstMatch = False
                            log.debug(f"{attributes[i]}")
                if regexp:
                    return regexp, roomList, type, background, colorRange
                else:
                    log.error(
                        f"Device type: {deviceType} and site name: {site} does not match any line in data: {test[j]} (ReadConf in Utils.py)"
                    )
                    sys.exit()

        log.error(
            f"Customer name: {customer} does not match customer in data {data} (ReadConf in Utils.py)"
        )
        sys.exit()
    else:
        log.warning("Cannot find .conf.json File in root (ReadConf in Utils.py)")
        sys.exit()


#####################################################################################################################
#####################################################################################################################


def CustomerAndSiteSpliter(customerAndSite: str) -> tuple[str, str]:
    """
    Split MYCUST.SITE into MYCUST, SITE

    :param str customerAndSite: customer and site name
    :returns: customer and site name, separated
    :rtype: tuple[str,str]
    """
    customerSiteList = customerAndSite.split(".")
    try:
        customer = customerSiteList[0]
        site = customerSiteList[1]
    except BaseException:
        log.error(
            "Site not correct. Please provide a site with the following syntax : MYCUST.MYSITE"
        )
        sys.exit()
    return customer, site


#####################################################################################################################
#####################################################################################################################


regRecursive = "(?!\[.\])([- _=~])(?!.\])"
recursiveMatcher = re.compile(regRecursive)
characterListToRemove = ["-", " ", "_", "=", "~"]


def RegexSpliterRecursive(regexp: str) -> list[str]:
    """
    Split the regexp according to a predefined list of problematic characters (['-', ' ', '_', '=', '~']). Returns the regexp as a list containing each part

    :returns: the regexp as a list containing each part
    :rtype: list[str]
    """
    list = recursiveMatcher.split(regexp)
    for ele in list:
        if ele in characterListToRemove:
            list.remove(ele)
    if list:
        return list
    else:
        log.error(
            f"the expression provided: {regexp} does not match the awaited regexp {recursiveMatcher}. Error (ogLblUtils.py)"
        )
        sys.exit()


#####################################################################################################################
#####################################################################################################################


def UpdateComponentList():
    """
    Update templates/components.json with all lone components JSON files in templates/components/
    """
    path = f"{os.path.dirname(os.path.realpath(__file__))}/../Converter/output/OGrEE/templates"
    files = [f for f in listdir(f"{path}/components") if isfile(f"{path}/components/{f}")]
    if not os.path.exists(f"{path}/components.json"):
        with open(f"{path}/components.json", "w") as file:
            json.dump({}, file)
    with open(f"{path}/components.json") as componentsJSON:
        all = json.loads(componentsJSON.read())
        for filename in files:
            with open(f"{path}/components/" + filename) as componentJSON:
                comp = json.loads(componentJSON.read())
                all[comp["attributes"]["factor"]] = comp
    with open(
        f"{path}/components.json",
        "w",
    ) as componentsJSON:
        componentsJSON.write(json.dumps(all, indent=4))


def GetAllComponents() -> dict[str, Any]:
    """
    Update templates/components.json and return it

    :returns: a JSON containing all components
    :rtype: dict[str,Any]
    """
    UpdateComponentList()
    with open(
       f"{os.path.dirname(os.path.realpath(__file__))}/../Converter/output/OGrEE/templates/components.json"
    ) as componentsJSON:
        return json.loads(componentsJSON.read())
