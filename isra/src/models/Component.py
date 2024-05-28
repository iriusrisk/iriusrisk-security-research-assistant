import copy
from dataclasses import dataclass, field


@dataclass
class Component:
    ref: str = field(default="")
    name: str = field(default="")
    description: str = field(default="")
    category: str = field(default="")

    def set_ref(self, value):
        self.ref = value

    def set_description(self, value):
        self.description = value

    def set_category(self, value):
        self.category = value

    def to_dict(self):
        data = copy.deepcopy(self.__dict__)
        return data

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
