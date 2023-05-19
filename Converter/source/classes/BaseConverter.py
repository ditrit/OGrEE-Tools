from __future__ import annotations

import logging
from typing import Any

from common import Api

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())


class BaseConverter:
    """Base class for all converters
    """
    def __init__(
        self, url: str, headersGET: dict[str, Any], headersPOST: dict[str, Any], **kw
    ) -> None:
        """

        :param url: API url of the source
        :type url: str
        :param headersGET: headers of the GET requests
        :type headersGET: dict[str, Any]
        :param headersPOST: headers of the POST requests
        :type headersPOST: dict[str, Any]
        """
        self.url = url
        self.headersGET = headersGET
        self.headersPOST = headersPOST
        super().__init__(**kw)

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
        return Api.PostFile(self.url, headers, endpoint, payload)

    def PutData(self):
        """Not implemented yet
        """
        pass

    def PostData(self):
        """Not implemented yet
        """
        pass

    def SaveToFile(self):
        """Not implemented yet
        """
        pass
