from os.path import dirname,realpath
from typing import Any

from Converter.source.classes.BaseConverter import BaseConverter
from Converter.source.interfaces.IToOGrEE import IToOGrEE

defaultOutputPath = realpath(f"{dirname(realpath(__file__))}/../../output/OGrEE")


class OGrEEToOGrEE(IToOGrEE, BaseConverter):

    def __init__(
        self,
        url: str,
        headersGET: dict[str, Any],
        headersPOST: dict[str, Any],
        outputPath: str | None = None,
        **kw,
    ) -> None:
        """

        :param url: API url of the source
        :type url: str
        :param headersGET: headers of the GET requests
        :type headersGET: dict[str, Any]
        :param headersPOST: headers of the POST requests
        :type headersPOST: dict[str, Any]
        :param outputPath: where the data will be saved, defaults to Converter/output/OGrEE
        :type outputPath: str | None, optional
        """
        self.outputPath = (
            realpath(outputPath) if outputPath is not None else defaultOutputPath
        )
        self.templatePath = realpath(f"{self.outputPath}/templates")
        super().__init__(url=url, headersGET=headersGET, headersPOST=headersPOST, **kw)

    def BuildDomain(self, data: dict[str, Any]) -> dict[str, Any]:
        return data

    def BuildSite(self, data: dict[str, Any]) -> dict[str, Any]:
        return data

    def BuildBuilding(self, data: dict[str, Any]) -> dict[str, Any]:
        return data

    def BuildRoom(self, data: dict[str, Any]) -> dict[str, Any]:
        return data

    def BuildRack(self, data: dict[str, Any]) -> dict[str, Any]:
        return data

    def BuildDevice(self, data: dict[str, Any]) -> dict[str, Any]:
        return data

    def BuildTemplate(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        return data
