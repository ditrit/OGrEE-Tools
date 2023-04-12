"""
**Handles communications with remote server**
"""
import logging
import json
from typing import Any
import requests
from threading import Thread
import functools

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())

#####################################################################################################################
#####################################################################################################################


def timeout(timeout):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            res = [
                Exception(
                    "function [%s] timeout [%s seconds] exceeded!"
                    % (func.__name__, timeout)
                )
            ]

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
                log.error("error starting thread (Api.py)")
                raise je
            ret = res[0]
            #    if isinstance(ret, BaseException):
            #        raise ret
            return ret

        return wrapper

    return deco


#####################################################################################################################


@timeout(10)
def GetJSON(url: str, headers: dict[str, Any], endpoint: str) -> dict[str, Any]:
    """
    Perform a GET request to a given URI and return a JSON

    :param str url: url of the remote server
    :param dict[str,Any] headers: headers of the request, JSON-formatted
    :param str endpoint: endpoint to be added after the url
    :return: return a JSON containing the server's answer
    :rtype: dict[str,Any]
    """
    apiURL = f"{url}/{endpoint}"
    payload = ""
    try:
        response = requests.get(apiURL, headers=headers, data=payload)
        log.debug("API is up and running")
        log.debug(
            f" [status code = {response.status_code}] to the GET request on url: {apiURL}"
        )
    except:
        raise Exception(
            f"No response to the GET request on url: {apiURL}. API may be down"
        )
    try:
        test = response.json()
    except:
        raise Exception(
            f"Could not retrieve [status code = {response.status_code}] data from response: {response.content}"
        )

    return test


#####################################################################################################################


@timeout(10)
def PostJSON(
    url: str, headers: dict[str, Any], endpoint: str, payload: dict[str, Any]
) -> dict[str, Any]:
    """
    Perform a POST request to a given URI and return a JSON

    :param str url: url of the remote server
    :param dict[str,Any] headers: headers of the request, JSON-formatted
    :param str endpoint: endpoint to be added after the url
    :param dict[str,Any] payload: payload of the request, JSON-formatted
    :return: return a JSON containing the server's answer
    :rtype: dict[str,Any]
    """
    apiURL = f"{url}/{endpoint}"
    try:
        response = requests.post(apiURL, headers=headers, data=json.dumps(payload))
        log.debug(
            f"The response [status code = {response.status_code}] to the POST request on url: {apiURL} is: \n{response.json()}"
        )
        log.debug(f"post payload : {payload}")
    except:
        raise Exception(
            f"No response to the POST request on url: {apiURL}. API may be down"
        )
    try:
        test = response.json()
    except:
        print("test")
        raise Exception(
            f"Could not retrieve [status code = {response.status_code}] data from response: {response.content}"
        )
    return test


@timeout(10)
def GetFile(url: str, headers: dict[str, Any], endpoint: str) -> bytes:
    """
    Perform a GET request to a given URI and return a file

    :param str url: url of the remote server
    :param dict[str,Any] headers: headers of the request, JSON-formatted
    :param str endpoint: endpoint to be added after the url
    :return: return a byte array containing the server's answer, or an empty byte array if the server returned an error
    :rtype: bytes
    """
    apiURL = f"{url}/{endpoint}"
    payload = ""
    try:
        response = requests.get(apiURL, headers=headers, data=payload)
        log.debug("API is up and running")
        log.debug(
            f" [status code = {response.status_code}] to the GET request on url: {apiURL}"
        )
    except:
        raise Exception(
            f"No response to the GET request on url: {apiURL}. API may be down"
        )
    return response.content if response.status_code == 200 else b""


@timeout(10)
def PostFile(
    url: str, headers: dict[str, Any], endpoint: str, payload: dict[str, Any]
) -> bytes:
    """
    Perform a POST request to a given URI and return a file

    :param str url: url of the remote server
    :param dict[str,Any] headers: headers of the request, JSON-formatted
    :param str endpoint: endpoint to be added after the url
    :param dict[str,Any] payload: payload of the request, JSON-formatted
    :return: return a byte array containing the server's answer, or an empty byte array if the server returned an error
    :rtype: bytes
    """
    apiURL = f"{url}/{endpoint}"
    payload = ""
    try:
        response = requests.post(apiURL, headers=headers, data=payload)
        log.debug("API is up and running")
        log.debug(
            f" [status code = {response.status_code}] to the POST request on url: {apiURL}"
        )
    except:
        raise Exception(
            f"No response to the POST request on url: {apiURL}. API may be down"
        )
    return response.content if response.status_code == 200 else b""
