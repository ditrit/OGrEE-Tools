from abc import ABC, abstractmethod
from typing import Any


class IToOGrEE(ABC):
    def __init__(self, **kw) -> None:
        super().__init__(**kw)

    @abstractmethod
    def BuildSite(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Build a site from another base's data

        :param dict[str, Any] siteData: a JSON used to build the site
        :returns: a dict describing an OGrEE site
        :rtype: dict[str, Any]
        """
        pass

    @abstractmethod
    def BuildBuilding(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Build a building from another base's data

        :param dict[str, Any] buildingData: a JSON used to build the site
        :returns: a dict describing an OGrEE building
        :rtype: dict[str, Any]
        """
        pass

    @abstractmethod
    def BuildRoom(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Build a room from another base's data

        :param dict[str, Any] roomData: a JSON used to build the site
        :returns: a dict describing an OGrEE room
        :rtype: dict[str, Any]
        """
        pass

    @abstractmethod
    def BuildRack(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Build a rack from another base's data

        :param dict[str, Any] rackData: a JSON used to build the rack
        :returns: a dict describing an OGrEE rack
        :rtype: dict[str, Any]
        """
        pass

    @abstractmethod
    def BuildDevice(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Build a device from another base's data

        :param dict[str, Any] deviceData: a JSON used to build the device
        :returns: a dict describing an OGrEE device
        :rtype: dict[str, Any]
        """
        pass

    @abstractmethod
    def BuildTemplate(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Build a template from another base's data

        :param dict[str, Any] templateData: a JSON used to build the template
        :returns: a dict describing an OGrEE template
        :rtype: dict[str, Any]
        """
        pass
