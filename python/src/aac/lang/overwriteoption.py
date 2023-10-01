from enum import Enum, auto

class OverwriteOption(Enum):
    OVERWRITE = auto()
    SKIP = auto()

    @classmethod
    def from_dict(cls, d: str):
        if 'OVERWRITE' == d:
            return cls.OVERWRITE
        elif 'SKIP' == d:
            return cls.SKIP
        else:
            raise ValueError('Invalid dictionary for OverwriteOption')