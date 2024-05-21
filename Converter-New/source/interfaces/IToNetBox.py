from abc import ABC, abstractmethod
from typing import Any


class IToNetBox(ABC):
    def __init__(self, **kw) -> None:
        super().__init__(**kw)

    @abstractmethod
    def BuildSite(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Build a site from another base's data

        :param dict[str, Any] data: a JSON used to build the site
        :returns: a dict describing an NetBox site
        :rtype: dict[str, Any]
        """
        pass

    @abstractmethod
    def BuildRegion(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Build a region from another base's data

        :param dict[str, Any] data: a JSON used to build the region
        :returns: a dict describing an NetBox region
        :rtype: dict[str, Any]
        """
        pass

    @abstractmethod
    def BuildLocation(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Build a location from another base's data

        :param dict[str, Any] data: a JSON used to build the location
        :returns: a dict describing an NetBox location
        :rtype: dict[str, Any]
        """
        pass

    @abstractmethod
    def BuildRack(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Build a rack from another base's data

        :param dict[str, Any] data: a JSON used to build the rack
        :returns: a dict describing an NetBox rack
        :rtype: dict[str, Any]
        """
        pass

    @abstractmethod
    def BuildRackRole(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Build a rack role from another base's data

        :param dict[str, Any] data: a JSON used to build the rack role
        :returns: a dict describing an NetBox rack role
        :rtype: dict[str, Any]
        """
        pass

    @abstractmethod
    def BuildReservation(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Build a reservation from another base's data

        :param dict[str, Any] data: a JSON used to build the reservation
        :returns: a dict describing an NetBox reservation
        :rtype: dict[str, Any]
        """
        pass

    @abstractmethod
    def BuildTenant(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Build a tenant from another base's data

        :param dict[str, Any] data: a JSON used to build the tenant
        :returns: a dict describing an NetBox tenant
        :rtype: dict[str, Any]
        """
        pass

    @abstractmethod
    def BuildDevice(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Build a device from another base's data

        :param dict[str, Any] data: a JSON used to build the device
        :returns: a dict describing an NetBox device
        :rtype: dict[str, Any]
        """
        pass

    @abstractmethod
    def BuildDeviceRole(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Build a device role from another base's data

        :param dict[str, Any] data: a JSON used to build the device role
        :returns: a dict describing an NetBox device role
        :rtype: dict[str, Any]
        """
        pass

    @abstractmethod
    def BuildDeviceType(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Build a device type from another base's data

        :param dict[str, Any] data: a JSON used to build the device type
        :returns: a dict describing an NetBox device type
        :rtype: dict[str, Any]
        """
        pass
