from __future__ import annotations

import logging
from typing import Any

from common import Api

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())


class BaseConverter:
    def __init__(
        self, url: str, headersGET: dict[str, Any], headersPOST: dict[str, Any]
    ) -> None:
        self.url = url
        self.headersGET = headersGET
        self.headersPOST = headersPOST

    def GetJSON(
        self, endpoint: str, headers: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        send a GET request to the API

        :param str endpoint: the API's endpoint
        :param dict[str,Any]|None headers: optionnal headers if you want to override the GET headers set when creating the Converter instance
        :returns: a json containing the API's response
        :rtype: dict[str,Any]
        """
        if headers is None:
            return Api.GetJSON(self.url, self.headersGET, endpoint)
        return Api.GetJSON(self.url, headers, endpoint)

    def PostJSON(
        self,
        endpoint: str,
        payload: dict[str, Any],
        headers: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        send a POST request to the API

        :param str endpoint: the API's endpoint
        :param dict[str,Any] payload: a JSON containing the payload of the POST request
        :param dict[str,Any]|None headers: optionnal headers if you want to override the POST headers set when creating the Converter instance
        :returns: a json containing the API's response
        :rtype: dict[str,Any]
        """
        if headers is None:
            return Api.PostJSON(self.url, self.headersPOST, endpoint, payload)
        return Api.PostJSON(self.url, headers, endpoint, payload)

    def GetFile(self, endpoint: str, headers: dict[str, Any] | None = None) -> bytes:
        """
        send a GET request to the API for a file

        :param str endpoint: the API's endpoint
        :param dict[str,Any]|None headers: optionnal headers if you want to override the GET headers set when creating the Converter instance
        :returns: a bytes containing the API's response
        :rtype: bytes
        """
        if headers is None:
            return Api.GetFile(self.url, self.headersGET, endpoint)
        return Api.GetFile(self.url, headers, endpoint)

    def PostFile(
        self,
        endpoint: str,
        payload: dict[str, Any],
        headers: dict[str, Any] | None = None,
    ) -> bytes:
        """
        send a POST request to the API for a file

        :param str endpoint: the API's endpoint
        :param dict[str,Any] payload: a JSON containing the payload of the POST request
        :param dict[str,Any]|None headers: optionnal headers if you want to override the POST headers set when creating the Converter instance
        :returns: a bytes containing the API's response
        :rtype: bytes
        """
        if headers is None:
            return Api.PostFile(self.url, self.headersPOST, endpoint, payload)
        return Api.Postfile(self.url, headers, endpoint, payload)

    def PutData():
        pass

    def PostData():
        pass

    def SaveToFile():
        pass