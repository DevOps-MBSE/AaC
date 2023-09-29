from enum import Enum

class OverwriteOption(Enum):
    OVERWRITE = 1
    SKIP = 2
    # MERGE = 3

    @classmethod
    def from_dict(cls, d: str):
        if 'OVERWRITE' == d:
            return cls.OVERWRITE
        elif 'SKIP' == d:
            return cls.SKIP
        # elif 'MERGE' == d:
        #     return cls.MERGE
        else:
            raise ValueError('Invalid dictionary for OverwriteOption')