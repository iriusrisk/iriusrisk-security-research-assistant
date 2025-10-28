from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
import uuid
from .base import IRBaseElement, IRBaseElementNoUUID, ItemType


@dataclass
class IRRiskRating:
    """Risk rating for threats"""
    confidentiality: str
    integrity: str
    availability: str
    ease_of_exploitation: str

    def __init__(self, c: str, i: str, a: str, ee: str):
        self.confidentiality = c
        self.integrity = i
        self.availability = a
        self.ease_of_exploitation = ee


@dataclass
class IRTest:
    """Test information for controls and weaknesses"""
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    steps: str = ""
    references: Dict[str, str] = field(default_factory=dict)

    def __init__(self, steps: str = "", uuid: Optional[str] = None):
        self.uuid = uuid if uuid else str(uuid.uuid4())
        self.steps = steps
        self.references = {}


@dataclass
class IRReference:
    """Reference information"""
    name: str
    url: str
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __init__(self, name: str, url: str, uuid: Optional[str] = None):
        self.uuid = uuid if uuid else str(uuid.uuid4())
        self.name = name
        self.url = url

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


@dataclass
class IRStandard:
    """Standard information"""
    supported_standard_ref: str
    standard_ref: str
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __init__(self, supported_standard_ref: str, standard_ref: str, uuid: Optional[str] = None):
        self.uuid = uuid if uuid else str(uuid.uuid4())
        self.supported_standard_ref = supported_standard_ref
        self.standard_ref = standard_ref

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


@dataclass
class IRSupportedStandard:
    """Supported standard information"""
    supported_standard_ref: str
    supported_standard_name: str
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __init__(self, supported_standard_ref: str, supported_standard_name: str, uuid: Optional[str] = None):
        self.uuid = uuid if uuid else str(uuid.uuid4())
        self.supported_standard_ref = supported_standard_ref
        self.supported_standard_name = supported_standard_name

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
        return (self.supported_standard_ref, self.supported_standard_name) < (other.supported_standard_ref, other.supported_standard_name)


@dataclass
class IRRuleCondition:
    """Rule condition"""
    name: str
    field: str
    value: str

    def __init__(self, name: str, field: str, value: str):
        self.name = name
        self.field = field
        self.value = value


@dataclass
class IRRuleAction:
    """Rule action"""
    name: str
    value: str
    project: str

    def __init__(self, name: str, value: str, project: str):
        self.name = name
        self.value = value
        self.project = project


@dataclass
class IRRule:
    """Rule definition"""
    name: str
    module: str
    gui: str
    conditions: List[IRRuleCondition] = field(default_factory=list)
    actions: List[IRRuleAction] = field(default_factory=list)

    def __init__(self, name: str, module: str, gui: str):
        self.name = name
        self.module = module
        self.gui = gui
        self.conditions = []
        self.actions = []


@dataclass
class IRRelation:
    """Relation between elements"""
    risk_pattern_uuid: str
    usecase_uuid: str
    threat_uuid: str
    weakness_uuid: str
    control_uuid: str
    mitigation: str
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __init__(self, risk_pattern_uuid: str, usecase_uuid: str, threat_uuid: str, 
                 weakness_uuid: str, control_uuid: str, mitigation: str, uuid: Optional[str] = None):
        self.uuid = uuid if uuid else str(uuid.uuid4())
        self.risk_pattern_uuid = risk_pattern_uuid
        self.usecase_uuid = usecase_uuid
        self.threat_uuid = threat_uuid
        self.weakness_uuid = weakness_uuid
        self.control_uuid = control_uuid
        self.mitigation = mitigation


@dataclass
class IRExtendedRelation:
    """Extended relation with library reference"""
    library_ref: str
    risk_pattern_ref: str
    usecase_ref: str
    threat_ref: str
    weakness_ref: str
    control_ref: str
    mitigation: str

    def __init__(self, library_ref: str, risk_pattern_ref: str, usecase_ref: str, 
                 threat_ref: str, weakness_ref: str, control_ref: str, mitigation: str):
        self.library_ref = library_ref
        self.risk_pattern_ref = risk_pattern_ref
        self.usecase_ref = usecase_ref
        self.threat_ref = threat_ref
        self.weakness_ref = weakness_ref
        self.control_ref = control_ref
        self.mitigation = mitigation

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
@dataclass
class IRCategoryComponent(IRBaseElement):
    """Category component"""
    def __init__(self, ref: str, name: str, uuid: Optional[str] = None):
        super().__init__(ref, name, "", uuid)


@dataclass
class IRComponentDefinition(IRBaseElement):
    """Component definition"""
    category_ref: str = ""
    visible: str = ""
    risk_pattern_refs: List[str] = field(default_factory=list)

    def __init__(self, ref: str, name: str, desc: str, category_ref: str, visible: str, uuid: Optional[str] = None):
        super().__init__(ref, name, desc, uuid)
        self.category_ref = category_ref
        self.visible = visible
        self.risk_pattern_refs = []


@dataclass
class IRThreat(IRBaseElement):
    """Threat definition"""
    risk_rating: IRRiskRating = field(default_factory=lambda: IRRiskRating("100", "100", "100", "100"))
    mitre: List[str] = field(default_factory=list)
    stride: List[str] = field(default_factory=list)
    references: Dict[str, str] = field(default_factory=dict)

    def __init__(self, ref: str, name: str, desc: str, uuid: Optional[str] = None):
        super().__init__(ref, name, desc, uuid)
        self.references = {}
        self.mitre = []
        self.stride = []
        self.risk_rating = IRRiskRating("100", "100", "100", "100")


@dataclass
class IRWeakness(IRBaseElement):
    """Weakness definition"""
    impact: str = "100"
    test: IRTest = field(default_factory=IRTest)

    def __init__(self, ref: str, name: str, desc: str, impact: str = "100", 
                 test: Optional[IRTest] = None, uuid: Optional[str] = None):
        super().__init__(ref, name, desc, uuid)
        self.impact = impact
        self.test = test if test else IRTest()


@dataclass
class IRControl(IRBaseElement):
    """Control definition"""
    standards: Dict[str, str] = field(default_factory=dict)
    references: Dict[str, str] = field(default_factory=dict)
    implementations: Set[str] = field(default_factory=set)
    test: IRTest = field(default_factory=lambda: IRTest(""))
    state: str = "Recommended"
    cost: str = "0"
    base_standard: List[str] = field(default_factory=list)
    base_standard_section: List[str] = field(default_factory=list)
    scope: List[str] = field(default_factory=list)
    mitre: List[str] = field(default_factory=list)

    def __init__(self, ref: str, name: str, desc: str = "", state: str = "Recommended", 
                 cost: str = "0", test: Optional[IRTest] = None, uuid: Optional[str] = None):
        super().__init__(ref, name, desc, uuid)
        self.standards = {}
        self.references = {}
        self.implementations = set()
        self.state = state
        self.cost = cost
        self.test = test if test else IRTest("")
        self.base_standard = []
        self.base_standard_section = []
        self.scope = []
        self.mitre = []


@dataclass
class IRUseCase(IRBaseElement):
    """Use case definition"""
    def __init__(self, ref: str, name: str, desc: str, uuid: Optional[str] = None):
        super().__init__(ref, name, desc, uuid)


@dataclass
class IRRiskPattern(IRBaseElement):
    """Risk pattern definition"""
    def __init__(self, ref: str, name: str, desc: str, uuid: Optional[str] = None):
        super().__init__(ref, name, desc, uuid)


@dataclass
class IRLibrary(IRBaseElement):
    """Library definition"""
    revision: str = "1"
    filename: str = ""
    enabled: str = "true"
    risk_patterns: Dict[str, IRRiskPattern] = field(default_factory=dict)
    rules: List[IRRule] = field(default_factory=list)
    component_definitions: Dict[str, IRComponentDefinition] = field(default_factory=dict)
    relations: Dict[str, IRRelation] = field(default_factory=dict)

    def __init__(self, ref: str, name: str = "", desc: str = "", revision: str = "1", 
                 filename: str = "", enabled: str = "true", uuid: Optional[str] = None):
        super().__init__(ref, name, desc, uuid)
        self.revision = revision
        self.filename = filename
        self.enabled = enabled
        self.risk_patterns = {}
        self.rules = []
        self.component_definitions = {}
        self.relations = {}


@dataclass
class IRCustomField(IRBaseElement):
    """Custom field"""
    value: str = ""

    def __init__(self, ref: str, value: str, uuid: Optional[str] = None):
        super().__init__(ref, "", "", uuid)
        self.value = value


# Item classes extending IRBaseElementNoUUID
@dataclass
class IRControlItem(IRBaseElementNoUUID):
    """Control item for relations"""
    mitigation: str = ""

    def __init__(self, ref: str, mitigation: str):
        super().__init__(ref)
        self.mitigation = mitigation


@dataclass
class IRWeaknessItem(IRBaseElementNoUUID):
    """Weakness item for relations"""
    controls: Dict[str, IRControlItem] = field(default_factory=dict)

    def __init__(self, ref: str):
        super().__init__(ref)
        self.controls = {}


@dataclass
class IRThreatItem(IRBaseElementNoUUID):
    """Threat item for relations"""
    weaknesses: Dict[str, IRWeaknessItem] = field(default_factory=dict)
    orphaned_controls: Dict[str, IRControlItem] = field(default_factory=dict)

    def __init__(self, ref: str):
        super().__init__(ref)
        self.weaknesses = {}
        self.orphaned_controls = {}


@dataclass
class IRUseCaseItem(IRBaseElementNoUUID):
    """Use case item for relations"""
    threats: Dict[str, IRThreatItem] = field(default_factory=dict)

    def __init__(self, ref: str):
        super().__init__(ref)
        self.threats = {}


@dataclass
class IRRiskPatternItem(IRBaseElementNoUUID):
    """Risk pattern item for relations"""
    usecases: Dict[str, IRUseCaseItem] = field(default_factory=dict)

    def __init__(self, ref: str):
        super().__init__(ref)
        self.usecases = {}