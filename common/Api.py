from distutils.log import debug
import logging
import sys
import json
import requests
from threading import Thread
import functools

#####################################################################################################################
#####################################################################################################################

def timeout(timeout):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            res = [Exception('function [%s] timeout [%s seconds] exceeded!' % (func.__name__, timeout))]
            def newFunc():
                try:
                    res[0] = func(*args, **kwargs)
                except Exception as e:
                    res[0] = e
            t = Thread(target=newFunc)
            t.daemon = True
            try:
                t.start()
                t.join(timeout)
            except Exception as je:
                logging.error('error starting thread (Api.py)')
                raise je
            ret = res[0]
            if isinstance(ret, BaseException):
                raise ret
            return ret
        return wrapper
    return deco

#####################################################################################################################

@timeout(20)
def GetRequest(url, headers, endpoint):

    apiURL = "{}/{}".format(url, endpoint)
    payload = ""
    try:
        response = requests.get(apiURL, headers=headers, data=payload)
        logging.debug("API is up and running")
        logging.debug(f"The reponse [status code = {response.status_code}] to the POST request on url: {apiURL} is: \n{response.json()}")
    except:
        logging.error(f"No reponse to the GET request on url: {apiURL}. API may be down")
        sys.exit()
    try:
        test = response.json()['data']['objects']
    except:
        logging.error(f"Could not retrieve [status code = {response.status_code}] data from response: {response.json()}")
        sys.exit()

    return response.json()['data']['objects']

#####################################################################################################################

@timeout(20)
def PostRequest(url, headers, endpoint, payload):

    apiURL = "{}/{}".format(url, endpoint)
    try:
        response = requests.post(apiURL, headers=headers, data=json.dumps(payload))
        logging.debug(f"The reponse [status code = {response.status_code}] to the POST request on url: {apiURL} is: \n{response.json()}")
    except:
        logging.error(f"No reponse to the POST request on url: {apiURL}. API may be down")
        sys.exit()
    try:
        response.status_code == 201
    except:
        logging.error(f"Error during POST [status code = {response.status_code}] data from response: {response.json()}")
        sys.exit()

    return response.status_code

