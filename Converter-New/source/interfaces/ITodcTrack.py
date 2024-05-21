from abc import ABC, abstractmethod
from typing import Any


class ITodcTrack(ABC):
    def __init__(self, **kw) -> None:
        super().__init__(**kw)

    @abstractmethod
    def BuildLocation(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Build a location from another base's data

        :param dict[str, Any] data: a JSON used to build the location
        :returns: a dict describing an dcTrack location
        :rtype: dict[str, Any]
        """
        pass

    @abstractmethod
    def BuildItem(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Build a item from another base's data

        :param dict[str, Any] data: a JSON used to build the item
        :returns: a dict describing an dcTrack item
        :rtype: dict[str, Any]
        """
        pass

    @abstractmethod
    def BuildModel(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Build a model from another base's data

        :param dict[str, Any] data: a JSON used to build the model
        :returns: a dict describing an dcTrack model
        :rtype: dict[str, Any]
        """
        pass
