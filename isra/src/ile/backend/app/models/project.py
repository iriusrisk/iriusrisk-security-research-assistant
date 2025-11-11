from typing import Dict

from pydantic import BaseModel, Field

from .base import IRBaseElement
from .elements import (IRLibrary, IRUseCase, IRThreat, IRWeakness, IRControl,
                       IRCategoryComponent, IRReference, IRSupportedStandard, IRStandard)


class ILEProject(IRBaseElement):
    """Main project class"""
    versions: Dict[str, 'ILEVersion'] = Field(default_factory=dict)


class ILEVersion(BaseModel):
    """Version containing all libraries and elements"""
    version: str
    libraries: Dict[str, IRLibrary] = Field(default_factory=dict)
    usecases: Dict[str, IRUseCase] = Field(default_factory=dict)
    threats: Dict[str, IRThreat] = Field(default_factory=dict)
    weaknesses: Dict[str, IRWeakness] = Field(default_factory=dict)
    controls: Dict[str, IRControl] = Field(default_factory=dict)
    categories: Dict[str, IRCategoryComponent] = Field(default_factory=dict)
    references: Dict[str, IRReference] = Field(default_factory=dict)
    supported_standards: Dict[str, IRSupportedStandard] = Field(default_factory=dict)
    standards: Dict[str, IRStandard] = Field(default_factory=dict)

    def get_library(self, library: str) -> IRLibrary:
        """Get library by name"""
        return self.libraries.get(library)

    def clone(self) -> 'ILEVersion':
        """Create a clone of this version"""
        import copy
        return copy.deepcopy(self)
