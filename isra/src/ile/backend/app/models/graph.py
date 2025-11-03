import uuid
from typing import Any, Dict, List, Optional, Union, Set, TYPE_CHECKING
from collections import OrderedDict
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from isra.src.ile.backend.app.models.elements import IRExtendedRelation


class Node(BaseModel):
    """Graph node - base class with only id"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class Link(BaseModel):
    """Graph link"""
    source: str
    target: str

class Graph(BaseModel):
    """Graph structure"""
    # Using Union type to enable polymorphic serialization
    # When RuleNode or IRNode instances are added, Pydantic will serialize
    # all their fields (message, color, etc.) not just the base Node fields
    nodes: List[Union['RuleNode', 'IRNode', 'Node']] = Field(default_factory=list)
    links: List[Link] = Field(default_factory=list)
    directed: bool = True
    multigraph: bool = False
    showMitigations: bool = False
    revFirst: str = ""
    revSecond: str = ""
    equalRevisionNumber: bool = False
    changelogList: List['ChangelogItem'] = Field(default_factory=list)
    
    def has_node_value(self, node_id: str) -> bool:
        """Check if a node with the given ID exists"""
        return any(node.id == node_id for node in self.nodes)


class GraphList(BaseModel):
    """List of graphs"""
    graphs: Dict[str, Graph] = Field(default_factory=dict)
    deleted_libraries: List[str] = Field(default_factory=list)
    added_libraries: List[str] = Field(default_factory=list)


class IRNode(Node):
    """IriusRisk specific node"""
    name: str
    changes: List['Change'] = Field(default_factory=list)
    type: str = ""
    color: str = ""
    
    def __init__(self, name: str, arg2: Optional[Union[str, List['Change']]] = None, 
                 arg3: Optional[str] = None, **kwargs):
        """Initialize IRNode
        
        Supports both Java constructor signatures:
        - IRNode(name, type) -> arg2 is type (str)
        - IRNode(name, changes, type) -> arg2 is changes (List), arg3 is type (str)
        
        Args:
            name: Node name
            arg2: Either type (str) or changes (List[Change])
            arg3: Type (str) if arg2 is changes
        """
        changes: List['Change'] = []
        node_type: str = ""
        
        if isinstance(arg2, list):
            # IRNode(name, changes, type) signature
            changes = arg2
            node_type = arg3 if arg3 is not None else ""
        elif isinstance(arg2, str):
            # IRNode(name, type) signature
            node_type = arg2
            changes = kwargs.get('changes', [])
        else:
            # Default case or arg2 not provided
            node_type = arg3 if arg3 is not None else ""
            changes = kwargs.get('changes', [])
        
        super().__init__(**kwargs)
        self.name = name
        self.type = node_type
        self.changes = changes
        self._set_color_from_type()
    
    def _set_color_from_type(self) -> None:
        """Set color based on type"""
        type_colors = {
            "E": "#f6ec48",
            "N": "#39e260",
            "D": "#fa4040",
            "ROOT": "#30cbe8"
        }
        self.color = type_colors.get(self.type, "#C0C0C0")
    
    @property
    def node_type(self) -> str:
        """Backward compatibility alias for type"""
        return self.type
    
    @node_type.setter
    def node_type(self, value: str) -> None:
        """Backward compatibility alias for type"""
        self.type = value
        self._set_color_from_type()


class RuleNode(Node):
    """Rule node - extends Node with message and color"""
    message: str = ""
    color: str = ""
    
    def __init__(self, name: str = "", value: str = "", field: str = "", 
                 components_or_risk_patterns: Optional[Union[Dict, Dict[str, Any]]] = None,
                 project: Optional[str] = None, **kwargs):
        """Initialize RuleNode from condition or action
        
        Args:
            name: Condition or action name
            value: Condition or action value
            field: "CONDITION" for conditions, or project string for actions
            components_or_risk_patterns: For conditions: dict of IRComponentDefinition keyed by ref
                                        For actions: dict of IRRiskPattern keyed by uuid
            project: Optional project string (overrides field for actions)
        """
        # Initialize Node with auto-generated UUID (can be overridden later)
        super().__init__(**kwargs)
        self.message = ""
        self.color = ""
        
        if components_or_risk_patterns is None:
            components_or_risk_patterns = {}
        
        # Determine if this is a condition or action node
        if field == "CONDITION":
            self._set_value_for_condition_node(name, value, field, components_or_risk_patterns)
        else:
            # It's an action node - use project parameter or field as project
            action_project = project if project is not None else field
            self._set_value_for_action_node(name, value, action_project, components_or_risk_patterns)
    
    def _set_value_for_condition_node(self, name: str, value: str, field: str, 
                                     components: Dict[str, Any]) -> None:
        """Set value for condition node - components is dict of IRComponentDefinition"""
        if not value or value == "":
            # Hardcoded special case
            if name == "CONDITION_DATAFLOW_CROSS_TRUST_BOUNDARY":
                self.id = str(uuid.uuid4())
                self.message = "Trustzone crosses boundary"
                self.color = "#800080"
            else:
                self.id = str(uuid.uuid4())
                self.message = "Unknown: " + name
                self.color = "#C0C0C0"
            return
        
        value_list = []
        
        if name == "CONDITION_COMPONENT_DEFINITION":
            self.id = value
            comp = components.get(self.id)
            if comp:
                self.message = f"Is specific component definition: {comp.name}"
            else:
                self.message = f"Is specific component definition: {self.id}"
            self.color = "#000080"
            
        elif name in ["CONDITION_QUESTION_GROUP_EXISTS", "CONDITION_COMPONENT_QUESTION_GROUP_EXISTS"]:
            value_list = value.split("_::_")
            self.id = value_list[0] if value_list else value
            self.message = f"If question group '{self.id}' exists"
            self.color = "#00FFFF"
            
        elif name in ["CONDITION_QUESTION", "CONDITION_COMPONENT_QUESTION"]:
            self.id = value
            self.message = f"If answer is {self.id}"
            self.color = "#00FF00"
            
        elif name in ["CONDITION_QUESTION_NOT_ANSWERED", "CONDITION_COMPONENT_QUESTION_NOT_ANSWERED"]:
            self.id = value
            self.message = f"If answer is not {self.id}"
            self.color = "#008080"
            
        elif name == "CONDITION_RISK_PATTERN_EXISTS":
            self.id = value
            value_parts = self.id.split("_::_")
            if len(value_parts) >= 2:
                self.message = f"Risk pattern {value_parts[0]} -> {value_parts[1]} exists"
            else:
                self.message = f"Risk pattern {self.id} exists"
            self.color = "#800000"
            
        elif name in ["CONDITION_CONCLUSION_EXISTS", "CONDITION_CONCLUSION_COMPONENT_EXISTS"]:
            self.id = value
            self.message = f"Conclusion {self.id} exists"
            self.color = "#0000FF"
            
        elif name in ["CONDITION_CONCLUSION_NOT_EXISTS", "CONDITION_CONCLUSION_COMPONENT_NOT_EXISTS"]:
            self.id = value
            self.message = f"Conclusion {self.id} not exists"
            self.color = "#FF00FF"
            
        elif name == "CONDITION_APPLIED_CONTROL":
            self.id = value
            self.message = f"Countermeasure {self.id} is required"
            self.color = "#800080"
            
        elif name == "CONDITION_DATAFLOW_CONTAINS_TAG":
            self.id = value
            self.message = f"Dataflow contains tag '{self.id}'"
            self.color = "#800080"
            
        elif name == "CONDITION_CLASSIFICATION":
            self.id = value
            self.message = f"Dataflow contains asset of type '{self.id}'"
            self.color = "#800080"
            
        elif name == "CONDITION_ORIGIN_TRUSTZONE":
            self.id = value
            self.message = f"Trustzone at origin is {self.id}"
            self.color = "#800080"
            
        elif name == "CONDITION_DESTINATION_TRUSTZONE":
            self.id = value
            self.message = f"Trustzone at destination is {self.id}"
            self.color = "#800080"
            
        elif name == "CONDITION_DATAFLOW_CROSS_TRUST_BOUNDARY":
            self.id = str(uuid.uuid4())
            self.message = "Trustzone crosses boundary"
            self.color = "#800080"
            
        elif name == "CONDITION_DATAFLOW_RISK_PATTERN_IN_ORIGIN":
            self.id = value
            self.message = f"Risk pattern {self.id} is in origin"
            self.color = "#800080"
            
        elif name == "CONDITION_DATAFLOW_RISK_PATTERN_IN_DESTINATION":
            self.id = value
            self.message = f"Risk pattern {self.id} is in destination"
            self.color = "#800080"
            
        elif name == "CONDITION_DATAFLOW_CONTAINS_ASSET":
            self.id = value
            self.message = f"Asset {self.id} is in dataflow"
            self.color = "#800080"
            
        else:
            self.id = str(uuid.uuid4())
            self.message = f"Unknown: {name}"
            self.color = "#C0C0C0"
    
    def _set_value_for_action_node(self, name: str, value: str, project: str, 
                                  risk_patterns: Dict[str, Any]) -> None:
        """Set value for action node - risk_patterns is dict of IRRiskPattern keyed by uuid"""
        if not value or value == "":
            self.id = str(uuid.uuid4())
            self.message = f"Unknown: {name}"
            self.color = "#00FF7F"
            return
        
        value_list = value.split("_::_")
        
        if name in ["INSERT_QUESTION_GROUP", "INSERT_COMPONENT_QUESTION_GROUP"]:
            self.id = value_list[0] if value_list else value
            self.message = f"Question: {value_list[2] if len(value_list) > 2 else value}"
            self.color = "#f6ec48"
            
        elif name in ["INSERT_QUESTION", "INSERT_COMPONENT_QUESTION"]:
            self.id = value_list[0] if value_list else value
            self.message = f"Answer: {value_list[1] if len(value_list) > 1 else value}"
            self.color = "#008000"
            
        elif name == "IMPORT_RISK_PATTERN":
            self.id = value_list[1] if len(value_list) > 1 else value
            rp = risk_patterns.get(self.id)
            if rp:
                self.message = f"Import Risk Pattern: {rp.name}"
                self.color = "#FF4500"
            else:
                self.message = f"Import Risk Pattern (Not found!): {self.id}"
                self.color = "#000000"
                
        elif name == "EXTEND_RISK_PATTERN":
            self.id = value
            self.message = f"Extend Risk Pattern {value_list[0] if value_list else ''} >> {value_list[1] if len(value_list) > 1 else ''}"
            self.color = "#FFA07A"
            
        elif name in ["INSERT_CONCLUSION", "INSERT_COMPONENT_CONCLUSION"]:
            self.id = value_list[1] if len(value_list) > 1 else value
            self.message = f"Conclusion: {value_list[2] if len(value_list) > 2 else value}"
            self.color = "#F0E68C"
            
        elif name == "APPLY_CONTROL":
            self.id = f"{project}_::_{value}"
            self.message = f"Apply Control: {project} -> {self.id}"
            self.color = "#663399"
            
        elif name == "MARK_CONTROL_AS":
            self.id = value_list[0] if value_list else value
            self.message = f"Apply Control: {project} -> {self.id}"
            self.color = "#663399"
            
        elif name == "APPLY_SECURITY_STANDARD":
            self.id = value_list[1] if len(value_list) > 1 else value
            self.message = f"Apply security standard: {self.id}"
            self.color = "#FFA500"
            
        elif name in ["ANSWER_QUESTION", "ANSWER_COMPONENT_QUESTION"]:
            self.id = value_list[0] if value_list else value
            self.message = f"Answered question: {self.id}"
            self.color = "#6A5ACD"
            
        elif name == "IMPORT_SPECIFIC_UC":
            self.id = f"{value_list[1] if len(value_list) > 1 else ''}_::_{value_list[2] if len(value_list) > 2 else ''}"
            self.message = f"Imported use case: {value_list[2] if len(value_list) > 2 else ''} from risk pattern {value_list[1] if len(value_list) > 1 else ''}"
            self.color = "#5A5ACD"
            
        elif name == "IMPORT_RISK_PATTERN_ORIGIN":
            self.id = value_list[1] if len(value_list) > 1 else value
            rp = risk_patterns.get(self.id)
            if rp:
                self.message = f"Import Risk Pattern in origin: {rp.name}"
                self.color = "#FF4500"
            else:
                self.message = f"Import Risk Pattern in origin (Not found!): {self.id}"
                self.color = "#000000"
                
        elif name == "IMPORT_RISK_PATTERN_DESTINATION":
            self.id = value_list[1] if len(value_list) > 1 else value
            rp = risk_patterns.get(self.id)
            if rp:
                self.message = f"Import Risk Pattern in destination: {rp.name}"
                self.color = "#FF4500"
            else:
                self.message = f"Import Risk Pattern in destination (Not found!): {self.id}"
                self.color = "#000000"
                
        elif name == "IMPLEMENT_CONTROL_ORIGIN":
            self.id = f"{project}_::_{value}"
            self.message = f"Apply Control in origin: {project} -> {self.id}"
            self.color = "#663399"
            
        elif name == "IMPLEMENT_CONTROL_DESTINATION":
            self.id = f"{project}_::_{value}"
            self.message = f"Apply Control in destination: {project} -> {self.id}"
            self.color = "#663399"
            
        elif name == "INSERT_DATAFLOW_NOTIFICATION":
            self.id = value_list[1] if len(value_list) > 1 else value
            self.message = f"Notify (from dataflow): {value_list[2] if len(value_list) > 2 else value}"
            self.color = "#663399"
            
        elif name == "INSERT_COMPONENT_NOTIFICATION":
            self.id = value_list[1] if len(value_list) > 1 else value
            self.message = f"Notify (from component): {value_list[2] if len(value_list) > 2 else value}"
            self.color = "#663399"
            
        elif name == "INSERT_CONCLUSION_ORIGIN_COMPONENT":
            self.id = value_list[1] if len(value_list) > 1 else value
            self.message = f"Insert conclusion in origin: {value_list[2] if len(value_list) > 2 else value}"
            self.color = "#663399"
            
        elif name == "INSERT_CONCLUSION_DESTINATION_COMPONENT":
            self.id = value_list[1] if len(value_list) > 1 else value
            self.message = f"Insert conclusion in destination: {value_list[2] if len(value_list) > 2 else value}"
            self.color = "#663399"
            
        elif name == "INSERT_COMPONENT_ALERT":
            self.id = value_list[1] if len(value_list) > 1 else value
            self.message = f"Notify (from component): {value_list[2] if len(value_list) > 2 else value}"
            self.color = "#663399"
            
        else:
            self.id = str(uuid.uuid4())
            self.message = f"Unknown: {name}"
            self.color = "#00FF7F"


class Change(BaseModel):
    """Change item"""
    field: str
    old: Optional[str] = None
    new: Optional[str] = None
    
    def __init__(self, **kwargs):
        """Initialize Change with field, old, and new values"""
        # Handle both 'old'/'old_value' and 'new'/'new_value' for backward compatibility
        if 'old_value' in kwargs and 'old' not in kwargs:
            kwargs['old'] = kwargs.pop('old_value')
        if 'new_value' in kwargs and 'new' not in kwargs:
            kwargs['new'] = kwargs.pop('new_value')
        # Handle 'type' and 'description' for backward compatibility
        if 'type' in kwargs and 'field' not in kwargs:
            kwargs['field'] = kwargs.pop('type')
        if 'description' in kwargs:
            # Combine description into a change message if needed
            desc = kwargs.pop('description')
            if 'old' not in kwargs and 'new' not in kwargs:
                # Try to parse description if it contains old/new info
                pass
        super().__init__(**kwargs)
    
    @property
    def old_value(self) -> Optional[str]:
        """Get old value (alias for old)"""
        return self.old
    
    @old_value.setter
    def old_value(self, value: Optional[str]) -> None:
        """Set old value (alias for old)"""
        self.old = value
    
    @property
    def new_value(self) -> Optional[str]:
        """Get new value (alias for new)"""
        return self.new
    
    @new_value.setter
    def new_value(self, value: Optional[str]) -> None:
        """Set new value (alias for new)"""
        self.new = value


class ChangelogItem(BaseModel):
    """Changelog item"""
    element: Optional[str] = None
    elementRef: Optional[str] = None
    action: Optional[str] = None
    info: Optional[str] = None
    changes: List[Change] = Field(default_factory=list)
    
    # Backward compatibility: support 'item' as alias for 'elementRef'
    @property
    def item(self) -> Optional[str]:
        """Get item (alias for elementRef)"""
        return self.elementRef
    
    @item.setter
    def item(self, value: Optional[str]) -> None:
        """Set item (alias for elementRef)"""
        self.elementRef = value


class ChangelogReport(BaseModel):
    """Changelog report"""
    deleted: Set[Any] = Field(default_factory=set)  # IRExtendedRelation
    added: Set[Any] = Field(default_factory=set)  # IRExtendedRelation
    new_countermeasures: Dict[str, List[Any]] = Field(default_factory=dict)  # List[IRExtendedRelation]


class LibrarySummary(BaseModel):
    """Library summary"""
    ref: str
    name: str
    status: str  # "ADDED", "DELETED", "MODIFIED"
    old_revision: Optional[str] = None
    new_revision: Optional[str] = None
    has_changes: bool = True


class LibrarySummariesResponse(BaseModel):
    """Library summaries response"""
    added_libraries: List[LibrarySummary] = Field(default_factory=list)
    deleted_libraries: List[LibrarySummary] = Field(default_factory=list)
    modified_libraries: List[LibrarySummary] = Field(default_factory=list)