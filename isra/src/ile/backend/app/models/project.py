from dataclasses import dataclass, field
from typing import Dict
from .base import IRBaseElement
from .elements import (IRLibrary, IRUseCase, IRThreat, IRWeakness, IRControl, 
                      IRCategoryComponent, IRReference, IRSupportedStandard, IRStandard)


@dataclass
class ILEProject(IRBaseElement):
    """Main project class"""
    versions: Dict[str, 'ILEVersion'] = field(default_factory=dict)

    def __init__(self, ref: str, name: str, desc: str, uuid: str = None):
        super().__init__(ref, name, desc, uuid)
        self.versions = {}


@dataclass
class ILEVersion:
    """Version containing all libraries and elements"""
    version: str
    libraries: Dict[str, IRLibrary] = field(default_factory=dict)
    usecases: Dict[str, IRUseCase] = field(default_factory=dict)
    threats: Dict[str, IRThreat] = field(default_factory=dict)
    weaknesses: Dict[str, IRWeakness] = field(default_factory=dict)
    controls: Dict[str, IRControl] = field(default_factory=dict)
    categories: Dict[str, IRCategoryComponent] = field(default_factory=dict)
    references: Dict[str, IRReference] = field(default_factory=dict)
    supported_standards: Dict[str, IRSupportedStandard] = field(default_factory=dict)
    standards: Dict[str, IRStandard] = field(default_factory=dict)

    def __init__(self, version: str):
        self.version = version
        self.libraries = {}
        self.usecases = {}
        self.threats = {}
        self.weaknesses = {}
        self.controls = {}
        self.categories = {}
        self.references = {}
        self.supported_standards = {}
        self.standards = {}

    def get_library(self, library: str) -> IRLibrary:
        """Get library by name"""
        return self.libraries.get(library)

    def clone(self) -> 'ILEVersion':
        """Create a clone of this version"""
        import copy
        return copy.deepcopy(self)