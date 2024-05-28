import copy
from dataclasses import dataclass, field


@dataclass
class RiskPattern:
    ref: str = field(default="")
    name: str = field(default="")
    description: str = field(default="")
    type: str = field(default="static")

    def get_ref(self):
        return self.ref

    def set_ref(self, value):
        self.ref = value

    def get_name(self):
        return self.name

    def set_name(self, value):
        self.name = value

    def get_description(self):
        return self.description

    def set_description(self, value):
        self.description = value

    def to_dict(self):
        data = copy.deepcopy(self.__dict__)
        return data

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
