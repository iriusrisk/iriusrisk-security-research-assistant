import copy
from dataclasses import dataclass, field


@dataclass
class Relation:
    risk_pattern: str = field(default="")
    use_case: str = field(default="")
    threat: str = field(default="")
    weakness: str = field(default="")
    control: str = field(default="")
    mitigation: str = field(default="")

    def to_dict(self):
        data = copy.deepcopy(self.__dict__)
        return data

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
