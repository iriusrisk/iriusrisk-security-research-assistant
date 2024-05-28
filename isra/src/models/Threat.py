import copy
from dataclasses import dataclass, field

from isra.src.models.Reference import Reference
from isra.src.models.RiskScore import RiskScore
from isra.src.models.Taxonomy import Taxonomy


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

    def get_taxonomy(self, ref):
        for th in self.taxonomies:
            if th.ref == ref:
                return th

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
