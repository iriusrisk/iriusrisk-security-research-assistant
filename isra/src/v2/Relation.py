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

    def get_risk_pattern(self):
        return self.risk_pattern

    def set_risk_pattern(self, value):
        self.risk_pattern = value

    def get_use_case(self):
        return self.use_case

    def set_use_case(self, value):
        self.use_case = value

    def get_threat(self):
        return self.threat

    def set_threat(self, value):
        self.threat = value

    def get_weakness(self):
        return self.weakness

    def set_weakness(self, value):
        self.weakness = value

    def get_control(self):
        return self.control

    def set_control(self, value):
        self.control = value

    def get_mitigation(self):
        return self.mitigation

    def set_mitigation(self, value):
        self.mitigation = value

    def to_dict(self):
        data = copy.deepcopy(self.__dict__)
        return data

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
