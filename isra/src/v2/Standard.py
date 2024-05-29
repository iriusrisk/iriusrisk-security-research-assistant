import copy
from dataclasses import dataclass, field


@dataclass
class Standard:
    ref: str = field(default="")
    sections: set[str] = field(default_factory=set[str])

    def get_ref(self):
        return self.ref

    def set_ref(self, value):
        self.ref = value

    def get_sections(self):
        return self.sections

    def add_section(self, value):
        self.sections.add(value)

    def remove_section(self, value):
        self.sections.remove(value)

    def get_string_sections(self):
        return "||".join(self.sections)

    def to_dict(self):
        data = copy.deepcopy(self.__dict__)
        data['sections'] = list(self.sections)
        return data

    @classmethod
    def from_dict(cls, data):
        data['sections'] = set(data['sections'])
        return cls(**data)
