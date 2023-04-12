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
        return json.dumps(asdict(OgreeMessage(data)))


class IncorrectResponseError(Exception):
    """
    Custom error class used when the API do not send back expected data

    :param str url: the API's url
    :param str endpoint: the API's endpoint
    :param dict[str,Any]|None payload: the request's payload. If None, the request will categorised as GET and as POST otherwise
    :param str message: a custom error message. If precised, it will be printed instead of the default "GET/POST request to API {url} with endpoint {endpoint} returned incorrect data [payload :{payload}]"
    """

    def __init__(
        self,
        url: str,
        endpoint: str,
        payload: dict[str, Any] | None = None,
        message: str = "",
    ) -> None:
        super().__init__(message)
        self.url = url
        self.endpoint = endpoint
        self.message = message
        self.payload = payload

    def __str__(self) -> str:
        if self.message != "":
            return super.__str__(self)
        if self.payload is None:
            return f"GET request to API {self.url} with endpoint {self.endpoint} returned incorrect data"
        else:
            return f"POST request to API {self.url} with endpoint {self.endpoint} returned incorrect data\npayload :{self.payload}"


class IARConverter(ABC):
    @abstractmethod
    def MakeFBX(self, data: dict[str, Any]) -> str:
        pass

    @abstractmethod
    def RackSearch(self, img: ndarray, customerAndSite: str, deviceType: str) -> str:
        pass

    @abstractmethod
    def GetList(self):
        pass
