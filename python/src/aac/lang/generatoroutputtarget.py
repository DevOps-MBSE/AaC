from enum import Enum

class GeneratorOutputTarget(Enum):
    CODE = 1
    TEST = 2
    DOC = 3

    @classmethod
    def from_dict(cls, d: str):
        if 'CODE' == d:
            return cls.CODE
        elif 'TEST' == d:
            return cls.TEST
        elif 'DOC' == d:
            return cls.DOC
        else:
            raise ValueError('Invalid dictionary for GeneratorOutputTarget')