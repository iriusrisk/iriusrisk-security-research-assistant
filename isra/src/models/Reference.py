import copy
from dataclasses import dataclass, field


@dataclass
class Reference:
    name: str = field(default="")
    url: str = field(default="")

    def get_name(self):
        return self.name

    def set_name(self, value):
        self.name = value

    def get_url(self):
        return self.url

    def set_url(self, value):
        self.url = value

    def to_dict(self):
        data = copy.deepcopy(self.__dict__)
        return data

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
