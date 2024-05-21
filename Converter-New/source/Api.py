"""
**Handles communications with remote server**
"""

import logging
import json
from typing import Any
import requests
from threading import Thread
import functools
import traceback

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())


class APIHandler:
    def __init__(self, api_url: str, headers: dict[str, Any] | None) -> None:
        """
        The __init__ function is called when the class is instantiated.
        It initializes two attributes: API_URL and headers.

        :param api_url: str: Set the api_url attribute of the class
        :param headers: dict[str:, Any]: Pass a dictionary of headers to the api
        :return: None
        """
        self.API_URL = api_url
        self.headers = headers if headers else {}

    def timeout(timeout: int):
        """
        The timeout function is a decorator that can be used to wrap any function.
        It will run the wrapped function in a separate thread and kill it if it takes longer than the specified timeout.
        This is useful for functions that may take too long to complete, such as those which make API calls.

        :param timeout: int: Set the time limit for the function to run
        :return: A function that takes a function and returns another function
        """

        def deco(func):
            """
            The deco function is a decorator that takes a function and returns another function.
            The returned function will execute the original function in a separate thread,
            and if it does not complete within timeout seconds, it will raise an exception.

            :param func: Pass the function to be timed out
            :return: The wrapper function
            """

            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Exception:
                """
                The wrapper function is a decorator that will run the function it wraps in a separate thread.
                    If the function does not return within timeout seconds, then it will be terminated and an exception
                    raised. The wrapper function returns whatever value was returned by the wrapped function.

                :param *args: Pass a non-keyworded, variable-length argument list to the function
                :param **kwargs: Pass keyworded, variable-length argument list to the function
                :return: Whatever value was returned by the wrapped function
                """
                res = [Exception("function [%s] timeout [%s seconds] exceeded!" % (func.__name__, timeout))]

                def newFunc() -> None:
                    """
                    The newFunc function is a wrapper function that will be used to wrap the
                        original function. It will catch any exceptions thrown by the original
                        function and store them in res[0]. If no exception is thrown, it stores
                        the return value of func in res[0].

                    :return: The result of the func function or an exception if it occurs
                    """
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
                return ret

            return wrapper

        return deco

    @timeout(20)
    def GetJSON(self, headers: dict[str, Any], endpoint: str) -> dict[str, Any]:
        """
        Perform a GET request to a given URI and return a JSON

        :param str url: url of the remote server
        :param dict[str,Any] headers: headers of the request, JSON-formatted
        :param str endpoint: endpoint to be added after the url
        :return: return a JSON containing the server's answer
        :rtype: dict[str,Any]
        """
        apiURL = f"{self.API_URL}/{endpoint}"
        payload = ""
        try:
            response = requests.get(apiURL, headers=(headers if headers else {}) | self.headers, data=payload)
            log.debug("API is up and running")
            log.debug(f" [status code = {response.status_code}] to the GET request on url: {apiURL}")
        except:
            traceback.print_exc()
            raise Exception(f"No response to the GET request on url: {apiURL}. API may be down")
        try:
            test = response.json()
        except:
            traceback.print_exc()
            raise Exception(f"Could not retrieve [status code = {response.status_code}] data from response: {response.content}")

        return test

    @timeout(60)
    def PostJSON(self, headers: dict[str, Any], endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Perform a POST request to a given URI and return a JSON

        :param str url: url of the remote server
        :param dict[str,Any] headers: headers of the request, JSON-formatted
        :param str endpoint: endpoint to be added after the url
        :param dict[str,Any] payload: payload of the request, JSON-formatted
        :return: return a JSON containing the server's answer
        :rtype: dict[str,Any]
        """
        apiURL = f"{self.API_URL}/{endpoint}"
        try:
            response = requests.post(apiURL, headers=(headers if headers else {}) | self.headers, data=json.dumps(payload))
            log.debug(f"The response [status code = {response.status_code}] to the POST request on url: {apiURL} is: \n{response.json()}")
            log.debug(f"post payload : {payload}")
        except:
            traceback.print_exc()
            raise Exception(f"No response to the POST request on url: {apiURL}. API may be down")
        try:
            test = response.json()
        except:
            traceback.print_exc()
            raise Exception(f"Could not retrieve [status code = {response.status_code}] data from response: {response.content}")
        return test

    @timeout(10)
    def PutJSON(self, headers: dict[str, Any], endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Perform a PUT request to a given URI and return a JSON

        :param str url: url of the remote server
        :param dict[str,Any] headers: headers of the request, JSON-formatted
        :param str endpoint: endpoint to be added after the url
        :param dict[str,Any] payload: payload of the request, JSON-formatted
        :return: return a JSON containing the server's answer
        :rtype: dict[str,Any]
        """
        apiURL = f"{self.API_URL}/{endpoint}"
        try:
            response = requests.put(apiURL, headers=(headers if headers else {}) | self.headers, data=json.dumps(payload))
            log.debug(f"The response [status code = {response.status_code}] to the PUT request on url: {apiURL} is: \n{response.json()}")
            log.debug(f"put payload : {payload}")
        except:
            traceback.print_exc()
            raise Exception(f"No response to the PUT request on url: {apiURL}. API may be down")
        try:
            test = response.json()
        except:
            traceback.print_exc()
            raise Exception(f"Could not retrieve [status code = {response.status_code}] data from response: {response.content}")
        return test

    @timeout(10)
    def GetFile(self, headers: dict[str, Any], endpoint: str) -> bytes:
        """
        Perform a GET request to a given URI and return a file

        :param str url: url of the remote server
        :param dict[str,Any] headers: headers of the request, JSON-formatted
        :param str endpoint: endpoint to be added after the url
        :return: return a byte array containing the server's answer, or an empty byte array if the server returned an error
        :rtype: bytes
        """
        apiURL = f"{self.API_URL}/{endpoint}"
        payload = ""
        try:
            response = requests.get(apiURL, headers=(headers if headers else {}) | self.headers, data=payload)
            log.debug("API is up and running")
            log.debug(f" [status code = {response.status_code}] to the GET request on url: {apiURL}")
        except:
            traceback.print_exc()
            raise Exception(f"No response to the GET request on url: {apiURL}. API may be down")
        return response.content if response.status_code == 200 else b""

    @timeout(10)
    def PostFile(self, headers: dict[str, Any], endpoint: str, payload: dict[str, Any]) -> bytes:
        """
        Perform a POST request to a given URI and return a file

        :param str url: url of the remote server
        :param dict[str,Any] headers: headers of the request, JSON-formatted
        :param str endpoint: endpoint to be added after the url
        :param dict[str,Any] payload: payload of the request, JSON-formatted
        :return: return a byte array containing the server's answer, or an empty byte array if the server returned an error
        :rtype: bytes
        """
        apiURL = f"{self.API_URL}/{endpoint}"
        try:
            response = requests.post(apiURL, headers=(headers if headers else {}) | self.headers, data=payload)
            log.debug("API is up and running")
            log.debug(f" [status code = {response.status_code}] to the POST request on url: {apiURL}")
        except:
            traceback.print_exc()
            raise Exception(f"No response to the POST request on url: {apiURL}. API may be down")
        return response.content if response.status_code == 200 else b""
