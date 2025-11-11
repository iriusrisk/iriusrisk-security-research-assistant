from typing import Dict, List
import uuid
from pydantic import BaseModel, Field
from .base import IRBaseElement, IRBaseElementNoUUID


class IRRiskRating(BaseModel):
    """Risk rating for threats"""
    confidentiality: str
    integrity: str
    availability: str
    ease_of_exploitation: str


class IRTest(BaseModel):
    """Test information for controls and weaknesses"""
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    steps: str = ""
    references: Dict[str, str] = Field(default_factory=dict)


class IRReference(BaseModel):
    """Reference information"""
    name: str
    url: str
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))

    def __eq__(self, other):
        if not isinstance(other, IRReference):
            return False
        return (self.uuid == other.uuid and
                self.name == other.name and
                self.url == other.url)

    def __hash__(self):
        return hash((self.uuid, self.name, self.url))

    def __lt__(self, other):
        if not isinstance(other, IRReference):
            return NotImplemented
        return (self.name, self.url) < (other.name, other.url)


class IRStandard(BaseModel):
    """Standard information"""
    supported_standard_ref: str
    standard_ref: str
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))

    def __eq__(self, other):
        if not isinstance(other, IRStandard):
            return False
        return (self.supported_standard_ref == other.supported_standard_ref and
                self.standard_ref == other.standard_ref)

    def __hash__(self):
        return hash((self.supported_standard_ref, self.standard_ref))

    def __lt__(self, other):
        if not isinstance(other, IRStandard):
            return NotImplemented
        return (self.standard_ref, self.supported_standard_ref) < (other.standard_ref, other.supported_standard_ref)


class IRSupportedStandard(BaseModel):
    """Supported standard information"""
    supported_standard_ref: str
    supported_standard_name: str
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))

    def __eq__(self, other):
        if not isinstance(other, IRSupportedStandard):
            return False
        return (self.supported_standard_ref == other.supported_standard_ref and
                self.supported_standard_name == other.supported_standard_name)

    def __hash__(self):
        return hash((self.supported_standard_ref, self.supported_standard_name))

    def __lt__(self, other):
        if not isinstance(other, IRSupportedStandard):
            return NotImplemented
        return (self.supported_standard_ref, self.supported_standard_name) < (
        other.supported_standard_ref, other.supported_standard_name)


class IRRuleCondition(BaseModel):
    """Rule condition"""
    name: str
    field: str
    value: str


class IRRuleAction(BaseModel):
    """Rule action"""
    name: str
    value: str
    project: str


class IRRule(BaseModel):
    """Rule definition"""
    name: str
    module: str
    gui: str
    conditions: List[IRRuleCondition] = Field(default_factory=list)
    actions: List[IRRuleAction] = Field(default_factory=list)


class IRRelation(BaseModel):
    """Relation between elements"""
    risk_pattern_uuid: str
    usecase_uuid: str
    threat_uuid: str
    weakness_uuid: str
    control_uuid: str
    mitigation: str
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))


class IRExtendedRelation(BaseModel):
    """Extended relation with library reference"""
    library_ref: str
    risk_pattern_ref: str
    usecase_ref: str
    threat_ref: str
    weakness_ref: str
    control_ref: str
    mitigation: str

    @classmethod
    def from_relation(cls, library_ref: str, risk_pattern_ref: str, relation: IRRelation):
        return cls(
            library_ref=library_ref,
            risk_pattern_ref=risk_pattern_ref,
            usecase_ref=relation.usecase_uuid,
            threat_ref=relation.threat_uuid,
            weakness_ref=relation.weakness_uuid,
            control_ref=relation.control_uuid,
            mitigation=relation.mitigation
        )


# Elements extending IRBaseElement
class IRCategoryComponent(IRBaseElement):
    """Category component"""


class IRComponentDefinition(IRBaseElement):
    """Component definition"""
    category_ref: str = ""
    visible: str = ""
    risk_pattern_refs: List[str] = Field(default_factory=list)


class IRThreat(IRBaseElement):
    """Threat definition"""
    risk_rating: IRRiskRating = Field(
        default_factory=lambda: IRRiskRating(confidentiality="100", integrity="100", availability="100",
                                             ease_of_exploitation="100"))
    mitre: List[str] = Field(default_factory=list)
    stride: List[str] = Field(default_factory=list)
    references: Dict[str, str] = Field(default_factory=dict)


class IRWeakness(IRBaseElement):
    """Weakness definition"""
    impact: str = "100"
    test: IRTest = Field(default_factory=IRTest)


class IRControl(IRBaseElement):
    """Control definition"""
    standards: Dict[str, str] = Field(default_factory=dict)
    references: Dict[str, str] = Field(default_factory=dict)
    implementations: List[str] = Field(default_factory=list)
    test: IRTest = Field(default_factory=lambda: IRTest())
    state: str = "Recommended"
    cost: str = "0"
    base_standard: List[str] = Field(default_factory=list)
    base_standard_section: List[str] = Field(default_factory=list)
    scope: List[str] = Field(default_factory=list)
    mitre: List[str] = Field(default_factory=list)


class IRUseCase(IRBaseElement):
    """Use case definition"""


class IRRiskPattern(IRBaseElement):
    """Risk pattern definition"""


class IRLibrary(IRBaseElement):
    """Library definition"""
    revision: str = "1"
    filename: str = ""
    enabled: str = "true"
    risk_patterns: Dict[str, IRRiskPattern] = Field(default_factory=dict)
    rules: List[IRRule] = Field(default_factory=list)
    component_definitions: Dict[str, IRComponentDefinition] = Field(default_factory=dict)
    relations: Dict[str, IRRelation] = Field(default_factory=dict)


# Item classes extending IRBaseElementNoUUID
class IRControlItem(IRBaseElementNoUUID):
    """Control item for relations"""
    mitigation: str = ""


class IRWeaknessItem(IRBaseElementNoUUID):
    """Weakness item for relations"""
    controls: Dict[str, IRControlItem] = Field(default_factory=dict)


class IRThreatItem(IRBaseElementNoUUID):
    """Threat item for relations"""
    weaknesses: Dict[str, IRWeaknessItem] = Field(default_factory=dict)
    orphaned_controls: Dict[str, IRControlItem] = Field(default_factory=dict)


class IRUseCaseItem(IRBaseElementNoUUID):
    """Use case item for relations"""
    threats: Dict[str, IRThreatItem] = Field(default_factory=dict)


class IRRiskPatternItem(IRBaseElementNoUUID):
    """Risk pattern item for relations"""
    usecases: Dict[str, IRUseCaseItem] = Field(default_factory=dict)
