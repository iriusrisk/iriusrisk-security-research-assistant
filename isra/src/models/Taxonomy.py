import copy
from dataclasses import dataclass, field


@dataclass
class Taxonomy:
    ref: str = field(default="")
    values: set[str] = field(default_factory=set[str])

    def get_ref(self):
        return self.ref

    def set_ref(self, value):
        self.ref = value

    def get_values(self):
        return self.values

    def add_value(self, value):
        self.values.add(value)

    def remove_value(self, value):
        self.values.remove(value)

    def get_string_values(self):
        return "||".join(self.values)

    def to_dict(self):
        data = copy.deepcopy(self.__dict__)
        return data

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
