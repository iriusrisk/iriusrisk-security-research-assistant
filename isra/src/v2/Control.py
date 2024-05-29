import copy
from dataclasses import dataclass, field

from isra.src.v2.Reference import Reference
from isra.src.v2.Standard import Standard
from isra.src.v2.Taxonomy import Taxonomy


@dataclass
class Control:
    ref: str = field(default="")
    name: str = field(default="")
    description: str = field(default="")
    cost: str = field(default="2")
    question: str = field(default="")
    question_desc: str = field(default="")
    base_standard: Standard = field(default_factory=Standard)
    cwe: str = field(default="")
    cwe_impact: str = field(default="")
    references: list[Reference] = field(default_factory=list[Reference])
    taxonomies: list[Taxonomy] = field(default_factory=list[Taxonomy])
    standards: list[Standard] = field(default_factory=list[Standard])
    dataflow_tags: list[str] = field(default_factory=list)

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

    def get_cost(self):
        return self.cost

    def set_cost(self, value):
        self.cost = value

    def get_question(self):
        return self.question

    def set_question(self, value):
        self.question = value

    def get_question_desc(self):
        return self.question_desc

    def set_question_desc(self, value):
        self.question_desc = value

    def get_dataflow_tags(self):
        return self.dataflow_tags

    def set_dataflow_tags(self, value):
        self.dataflow_tags = value

    def get_base_standard(self):
        return self.base_standard

    def set_base_standard(self, value):
        self.base_standard = value

    def get_references(self):
        return self.references

    def set_references(self, value):
        self.references = value

    def get_taxonomies(self):
        return self.taxonomies

    def get_taxonomy(self, value):
        for item in self.taxonomies:
            if item.get_ref() == value:
                return item

    def set_taxonomies(self, value):
        self.taxonomies = value

    def get_standards(self):
        return self.standards

    def set_standards(self, value):
        self.standards = value

    def add_standard(self, ref, value):
        index = None
        for idx, x in enumerate(self.standards):
            if x.get_ref() == ref:
                self.standards[idx].add_section(value)
                return
        if index is None:
            new_standard = Standard(ref=ref, sections=set(value))
            self.standards.append(new_standard)

    def to_dict(self):
        data = copy.deepcopy(self.__dict__)
        data['base_standard'] = self.base_standard.to_dict()
        data['references'] = [item.to_dict() for item in self.references]
        data['taxonomies'] = [item.to_dict() for item in self.taxonomies]
        data['standards'] = [item.to_dict() for item in self.standards]
        return data

    @classmethod
    def from_dict(cls, data):
        data['base_standard'] = Standard.from_dict(data['base_standard'])
        data['references'] = [Reference.from_dict(item) for item in data['references']]
        data['taxonomies'] = [Taxonomy.from_dict(item) for item in data['taxonomies']]
        data['standards'] = [Standard.from_dict(item) for item in data['standards']]
        return cls(**data)
