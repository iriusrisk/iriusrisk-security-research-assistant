import copy
from dataclasses import dataclass, field

from isra.src.v2.Component import Component
from isra.src.v2.Control import Control
from isra.src.v2.Relation import Relation
from isra.src.v2.RiskPattern import RiskPattern
from isra.src.v2.Threat import Threat


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

    def set_relations(self, value):
        self.relations = value

    def clean(self):
        self.threats = []
        self.controls = []
        self.relations = []

    def get_relation_by_refs(self, relation_filter: Relation, type: str):
        """
        Returns a list of relations that match the filter
        :param relation_filter: a relation
        :param type: allowed types: ['and', 'or']
        :return: list
        """
        filtered_elements = []

        for element in self.relations:
            if type == "and":
                if all(getattr(element, key) == value for key, value in relation_filter.__dict__.items() if
                       value is not None):
                    filtered_elements.append(element.__dict__)
            elif type == "or":
                if any(getattr(element, key) == value for key, value in relation_filter.__dict__.items() if
                       value is not None):
                    filtered_elements.append(element.__dict__)

        return filtered_elements

    def build_tree(self):
        tree = {}

        for obj in self.relations:
            current_level = tree
            for key, value in obj.__dict__.items():
                if value not in current_level:
                    current_level[value] = {}
                current_level = current_level[value]

        return tree



    def get_threats(self):
        return self.threats

    def set_threats(self, value):
        self.threats = value

    def get_threat(self, ref):
        for item in self.threats:
            if item.ref == ref:
                return item

    def get_controls(self):
        return self.controls

    def set_controls(self, value):
        self.controls = value

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
