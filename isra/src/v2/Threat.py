import copy
from dataclasses import dataclass, field

from isra.src.v2.Reference import Reference
from isra.src.v2.RiskScore import RiskScore
from isra.src.v2.Taxonomy import Taxonomy


@dataclass
class Threat:
    ref: str = field(default="")
    name: str = field(default="")
    description: str = field(default="")
    group: str = field(default="")
    references: list[Reference] = field(default_factory=list[Reference])
    taxonomies: list[Taxonomy] = field(default_factory=list[Taxonomy])
    question: str = field(default="")
    question_desc: str = field(default="")
    risk_score: RiskScore = field(default_factory=RiskScore)

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

    def get_group(self):
        return self.group

    def set_group(self, value):
        self.group = value

    def get_question(self):
        return self.question

    def set_question(self, value):
        self.question = value

    def get_question_desc(self):
        return self.question_desc

    def set_question_desc(self, value):
        self.question_desc = value

    def get_risk_score(self):
        return self.risk_score

    def set_risk_score(self, value):
        self.risk_score = value

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

    def to_dict(self):
        data = copy.deepcopy(self.__dict__)
        data['risk_score'] = self.risk_score.to_dict()
        data['references'] = [item.to_dict() for item in self.references]
        data['taxonomies'] = [item.to_dict() for item in self.taxonomies]
        return data

    @classmethod
    def from_dict(cls, data):
        data['risk_score'] = RiskScore.from_dict(data['risk_score'])
        data['references'] = [Reference.from_dict(item) for item in data['references']]
        data['taxonomies'] = [Taxonomy.from_dict(item) for item in data['taxonomies']]
        return cls(**data)
