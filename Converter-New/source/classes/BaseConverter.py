from abc import ABC, abstractmethod
from typing import Any


class BaseConverter(ABC):
    """
    Base class for all converters
    """
    dcim_code:int

    @abstractmethod
    def Convert(data : dict[str,Any]) -> None:
        pass
