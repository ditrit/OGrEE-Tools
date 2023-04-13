from abc import ABC, abstractmethod
from os.path import dirname, realpath
from typing import Any

defaultOutputPath = realpath(f"{dirname(realpath(__file__))}/../../output/OGrEE")


class IToOGrEE(ABC):
    def __init__(
        self,
        url: str,
        headersGET: dict[str, Any],
        headersPOST: dict[str, Any],
        outputPath: str|None = None,
    ) -> None:
        self.url = url
        self.headersGET = headersGET
        self.headersPOST = headersPOST
        self.outputPath = realpath(outputPath) if outputPath is not None else defaultOutputPath

    @abstractmethod
    def BuildTenant(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        returns the tenant identifed by tenantData if it exists

        :param dict[str, Any] tenantData: a JSON used to get the tenant from the API
        :returns: a JSON containing the tenant's data
        :rtype: dict[str, Any]
        """
        pass

    @abstractmethod
    def BuildSite(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        returns the site identified by siteData if it exists

        :param dict[str, Any] siteData: a JSON used to get the site from the API
        :returns: a JSON containing the site's data
        :rtype: dict[str, Any]
        """
        pass

    @abstractmethod
    def BuildBuilding(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        returns the building identified by buildingData if it exists

        :param dict[str, Any] buildingData: a JSON used to get the site from the API
        :returns: a JSON containing the building's data
        :rtype: dict[str, Any]
        """
        pass

    @abstractmethod
    def BuildRoom(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        returns the room identified by roomData if it exists

        :param dict[str, Any] roomData: a JSON used to get the site from the API
        :returns: a JSON containing the room's data
        :rtype: dict[str, Any]
        """
        pass

    @abstractmethod
    def BuildRack(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        returns the rack identified by rackData if it exists

        :param dict[str, Any] rackData: a JSON used to get the rack from the API
        :returns: a JSON containing the rack's data
        :rtype: dict[str, Any]
        """
        pass

    @abstractmethod
    def BuildDevice(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        returns the device identified by deviceData if it exists

        :param dict[str, Any] deviceData: a JSON used to get the device from the API
        :returns: a JSON containing the device's data
        :rtype: dict[str, Any]
        """
        pass

    @abstractmethod
    def BuildTemplate(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        """
        returns the OGrEE template identified by templateData if it exists

        :param dict[str, Any] templateData: a JSON used to get the template from the API
        :returns: a JSON containing the template's data
        :rtype: dict[str, Any]
        """
        pass
