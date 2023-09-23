from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass(frozen=True)
class AacType(ABC):
    name: str
    description: str
    root: str

    @abstractmethod
    def get_gen_plugin_template() -> str:
        pass