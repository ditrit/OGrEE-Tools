import logging
import sys
from os.path import exists
import os
import json
import re

reg = '.+]-'
labelMatcherSpliter = re.compile(reg)

#####################################################################################################################
#####################################################################################################################

def validateJSON(jsonData):
    try:
        json.loads(jsonData)
    except ValueError as err:
        return False
    return True

#####################################################################################################################
#####################################################################################################################

def ReadEnv(pathToEnvFile):
    file_exists = exists(pathToEnvFile)
    if file_exists:
        f = open(pathToEnvFile, "r")
        data = json.load(f)
        url = data['api_url']
        token = data['api_token']
        endpoint = data['api_endpoint']
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        f.close()
        return url, token, headers, endpoint
    else:
        logging.warning("Cannot find configuration file (GetUrlAndToken in Utils.py)")
        sys.exit()
#####################################################################################################################
#####################################################################################################################

def ReadConf(pathToRegexFile, customer, site):
    file_exists = exists(pathToRegexFile)
    if file_exists:
        f = open(pathToRegexFile, "r")
        data = json.load(f)
        colorRange = data['range']
        if data['customer'] == customer:
            attributes = data['regexps']
            for i in range(len(attributes)):
                if attributes[i]['site'] == site:
                    regexp = attributes[i]['regexp']
                    room = attributes[i]['room']
                    type = attributes[i]['type']
                    background = attributes[i]['background']
                    return regexp, room, type, background, colorRange
            logging.error('Site name does not exist (ReadRegex in Utils.py)')
            sys.exit()
        else:
            logging.error("Customer name is wrong (ReadRegex in Utils.py)")
            sys.exit()
    else:
        logging.warning("File does not exist (ReadRegex in Utils.py)")
        sys.exit()


#####################################################################################################################
#####################################################################################################################

def CustomerAndSiteSpliter(customerAndSite):
    customerSiteList = customerAndSite.split('.')
    customer = customerSiteList[0]
    site = customerSiteList[1]
    return customer, site

#####################################################################################################################
#####################################################################################################################

def RegexSiteRoomRackSpliter(regexp):
    if labelMatcherSpliter.findall(regexp):
        label = labelMatcherSpliter.match(regexp)
        span = label.end()
        siteRoomRegex = regexp[:span-1]
        rackRegex = regexp[span:]
    else:
        logging.error("the regex provided is wrong. Error (Utils.py)")
        sys.exit()

    return siteRoomRegex, rackRegex

#####################################################################################################################
#####################################################################################################################
