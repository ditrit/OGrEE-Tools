from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Any

from numpy import ndarray


@dataclass
class OgreeMessage:
    """
    Represents a message be sent and received by OGrEE software
    """

    data: dict[str, Any]
    message: str = "successfully got object"
    status: bool = True

    @classmethod
    def FormatDict(cls, data: dict[str, Any]) -> str:
        """Take a dict representing an OGrEE object and returns a message to be sent to OGrEE-3D

        :param data: OGrEE data
        :type data: dict[str, Any]
        :return: a string containing the OGrEE data and formatted as a message sent to OGrEE-3D
        :rtype: str
        """
        return json.dumps(asdict(OgreeMessage(data)))


class IncorrectResponseError(Exception):
    """
    Custom error class used when the API do not send back expected data
    """

    def __init__(
        self,
        url: str,
        endpoint: str,
        payload: dict[str, Any] | None = None,
        message: str = "",
    ) -> None:
        """_summary_

        :param url: the API's url
        :type url: str
        :param endpoint: the API's endpoint
        :type endpoint: str
        :param payload: the request's payload. If None, the request will categorised as GET and as POST otherwise
        :type payload: dict[str, Any] | None, optional
        :param message: a custom error message. If precised, it will be printed instead of the default "GET/POST request to API {url} with endpoint {endpoint} returned incorrect data [payload :{payload}]"
        :type message: str, optional
        """
        super().__init__(message)
        self.url = url
        self.endpoint = endpoint
        self.message = message
        self.payload = payload

    def __str__(self) -> str:
        """Overwrite Exception.__str__

        :return: the default message if no message has been passed to this instance, or super().__str__()
        :rtype: str
        """
        if self.message != "":
            return super(IncorrectResponseError, self).__str__()
        if self.payload is None:
            return f"GET request to API {self.url} with endpoint {self.endpoint} returned incorrect data"
        else:
            return f"POST request to API {self.url} with endpoint {self.endpoint} returned incorrect data\npayload :{self.payload}"


class IARConverter(ABC):
    @abstractmethod
    def MakeFBX(self, data: dict[str, Any]) -> str:
        """Create an Fbx file from data describing an object

        :param data: data used to get the dimensions and textures of an object
        :type data: dict[str, Any]
        :return: the path to the created Fbx
        :rtype: str
        """
        pass

    @abstractmethod
    def RackSearch(
        self, img: ndarray, domain : str, site : str, deviceType: str, debug: bool = False
    ) -> str:
        """Perform OCR on a picture to get a rack name, then build the data describing him

        :param img: the image with a rack name in it
        :type img: ndarray
        :param customerAndSite: customer and site names : [CUSTOMER].[SITE]
        :type customerAndSite: str
        :param deviceType: "rack" or "mdi"
        :type deviceType: str
        :return: the data describing a rack
        :rtype: str
        """
        pass

    @abstractmethod
    def GetList(self):
        """Not implemented"""
        pass
