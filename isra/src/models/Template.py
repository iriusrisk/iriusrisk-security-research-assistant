import copy
from dataclasses import dataclass, field

from isra.src.models.Component import Component
from isra.src.models.Control import Control
from isra.src.models.Relation import Relation
from isra.src.models.RiskPattern import RiskPattern
from isra.src.models.Threat import Threat


@dataclass
class Template:
    component: Component = field(default_factory=Component)
    risk_pattern: RiskPattern = field(default_factory=RiskPattern)
    threats: list[Threat] = field(default_factory=list[Threat])
    controls: list[Control] = field(default_factory=list[Control])
    relations: list[Relation] = field(default_factory=list[Relation])

    def get_component(self):
        return self.component

    def set_component(self, value):
        self.component = value

    def get_risk_pattern(self):
        return self.risk_pattern

    def set_risk_pattern(self, risk_pattern: RiskPattern):
        self.risk_pattern = risk_pattern

    def get_relations(self):
        return self.relations

    def add_relation(self, relation: Relation):
        self.relations.append(relation)

    def remove_relation(self, relation: Relation):
        self.relations.remove(relation)

    def get_relation_by_refs(self, relation_filter: Relation, type: str):
        """
        Returns a list of relations that match the filter
        :param relation_filter: a relation
        :param type: allowed types: ['and', 'or']
        :return: list
        """
        for item in self.relations:
            pass


        return []

    def get_threats(self):
        return self.threats

    def get_threat(self, ref):
        for item in self.threats:
            if item.ref == ref:
                return item

    def get_controls(self):
        return self.controls

    def get_control(self, ref):
        for item in self.controls:
            if item.ref == ref:
                return item

    def to_dict(self):
        data = copy.deepcopy(self.__dict__)
        data['component'] = self.component.to_dict()
        data['risk_pattern'] = self.risk_pattern.to_dict()
        data['threats'] = [item.to_dict() for item in self.threats]
        data['controls'] = [item.to_dict() for item in self.controls]
        data['relations'] = [item.to_dict() for item in self.relations]
        return data

    @classmethod
    def from_dict(cls, data):
        data['component'] = Component.from_dict(data['component'])
        data['risk_pattern'] = RiskPattern.from_dict(data['risk_pattern'])
        data['threats'] = [Threat.from_dict(item) for item in data['threats']]
        data['controls'] = [Control.from_dict(item) for item in data['controls']]
        data['relations'] = [Relation.from_dict(item) for item in data['relations']]
        return cls(**data)


