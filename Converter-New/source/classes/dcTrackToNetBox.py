from typing import Any
from source.classes.BaseConverter import BaseConverter
from source.classes.DataLoader import EDCIM
from source.interfaces.IToNetBox import IToNetBox
from os.path import realpath, dirname

defaultOutputPath = realpath(f"{dirname(realpath(__file__))}/../../output/NetBox")


class dcTrackToNetBox(IToNetBox, BaseConverter):
    dcim_code = EDCIM.NETBOX.value - EDCIM.DCTRACK.value
    """Convert data from dcTrack to NetBox

    :param IToNetBox: Interface of to-NetBox converters
    :type IToNetBox: ItoNetBox
    :param BaseConverter: Base class of all converters
    :type BaseConverter: BaseConverter
    """

    def __init__(
        self,
        outputPath: str | None = None,
        **kw,
    ) -> None:
        """
        :param outputPath: where the data will be saved, defaults to Converter/output/dcTrack
        :type outputPath: str | None, optional
        """
        self.outputPath = realpath(outputPath) if outputPath is not None else defaultOutputPath
        self.modelPath = realpath(f"{self.outputPath}/models")
        super().__init__(**kw)

    def Convert(data: dict[str, Any]):
        pass

    def BuildLocation(self, data: dict[str, Any]) -> dict[str, Any]:
        pass
    
    def BuildDevice(self, data: dict[str, Any]) -> dict[str, Any]:
        pass
    
    def BuildDeviceRole(self, data: dict[str, Any]) -> dict[str, Any]:
        pass
    
    def BuildDeviceType(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        pass
    
    def BuildRack(self, data: dict[str, Any]) -> dict[str, Any]:
        pass
    
    def BuildRackRole(self, data: dict[str, Any]) -> dict[str, Any]:
        pass
    
    def BuildRegion(self, data: dict[str, Any]) -> dict[str, Any]:
        pass
    
    def BuildReservation(self, data: dict[str, Any]) -> dict[str, Any]:
        pass
    
    def BuildSite(self, data: dict[str, Any]) -> dict[str, Any]:
        pass
    
    def BuildTenant(self, data: dict[str, Any]) -> dict[str, Any]:
        pass