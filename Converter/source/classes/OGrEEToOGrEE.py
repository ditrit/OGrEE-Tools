import json
from copy import deepcopy
from os import listdir
from os.path import isfile, join
from typing import Any

from common.Utils import GetAllComponents
from Converter.source.classes.BaseConverter import BaseConverter
from Converter.source.interfaces.IToOGrEE import IToOGrEE


class OGrEEToOGrEE(IToOGrEE, BaseConverter):
    def __init__(
        self,
        url: str,
        headersGET: dict[str, Any],
        headersPOST: dict[str, Any],
        outputPath: str = None,
    ) -> None:
        super().__init__(url, headersGET, headersPOST, outputPath)
        self.templatePath = f"{self.outputPath}/templates"

    def BuildTenant(self, data: dict[str, Any]) -> dict[str, Any]:
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
