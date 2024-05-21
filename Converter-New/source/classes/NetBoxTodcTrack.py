from typing import Any
from source.classes.BaseConverter import BaseConverter
from source.classes.DataLoader import EDCIM
from source.interfaces.ITodcTrack import ITodcTrack
from os.path import realpath, dirname

defaultOutputPath = realpath(f"{dirname(realpath(__file__))}/../../output/dcTrack")


class NetBoxTodcTrack(ITodcTrack, BaseConverter):
    """Convert data from NetBox to dcTrack

    :param ITodcTrack: Interface of to-dcTrack converters
    :type ITodcTrack: ItodcTrack
    :param BaseConverter: Base class of all converters
    :type BaseConverter: BaseConverter
    """
    dcim_code = EDCIM.DCTRACK.value - EDCIM.NETBOX.value

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
    
    def Convert(data: dict[str, Any]) -> None:
        pass

    def BuildItem(self, data: dict[str, Any]) -> dict[str, Any]:
        pass
    
    def BuildLocation(self, data: dict[str, Any]) -> dict[str, Any]:
        pass
    
    def BuildModel(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        pass
