import copy
from dataclasses import dataclass, field


@dataclass
class RiskScore:
    confidentiality: str = field(default="100")
    integrity: str = field(default="100")
    availability: str = field(default="100")
    ease_of_exploitation: str = field(default="100")

    def to_dict(self):
        data = copy.deepcopy(self.__dict__)
        return data

    def get_confidentiality(self):
        return self.confidentiality

    def get_integrity(self):
        return self.integrity

    def get_availability(self):
        return self.availability

    def get_ease_of_exploitation(self):
        return self.ease_of_exploitation

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
