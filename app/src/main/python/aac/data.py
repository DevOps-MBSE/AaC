from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, List




class Data(ABC):

    def __init__(self, name: str, type: Primitaves, content: Dict):
        self.name = name
        self.type = type
        if not type == Primitaves.OBJECT:
            pass
        else:
            self.value = content.pop

    @abstractmethod
    def getDataElements(self) -> List[Data(ABC)]:
        pass