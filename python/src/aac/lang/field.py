from dataclasses import dataclass

@dataclass
class Field():
    name: str
    type: str
    description: str
    is_required: bool