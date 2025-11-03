from typing import List, Dict, Any
from pydantic import BaseModel, Field
from .base import IRBaseElement


class IRProjectReport(IRBaseElement):
    """Project report"""
    version_reports: List['IRVersionReport'] = Field(default_factory=list)


class IRVersionReport(BaseModel):
    """Version report"""
    version: str
    num_libraries: int = 0
    num_risk_patterns: int = 0
    num_usecases: int = 0
    num_threats: int = 0
    num_weaknesses: int = 0
    num_controls: int = 0
    num_references: int = 0
    num_standards: int = 0
    num_categories: int = 0
    num_components: int = 0
    num_rules: int = 0
    library_reports: List['IRLibraryReport'] = Field(default_factory=list)


class IRLibraryReport(BaseModel):
    """Library report"""
    library_ref: str
    library_name: str
    library_desc: str
    revision: str
    enabled: str
    library_filename: str
    num_component_definitions: int = 0
    num_risk_patterns: int = 0
    num_rules: int = 0
    num_usecases: int = 0
    num_threats: int = 0


class IRMitigationItem(BaseModel):
    """Mitigation item"""
    usecase_ref: str = ""
    threat_ref: str = ""
    message: str = ""
    total: str = ""
    relations: List[Any] = Field(default_factory=list)
    error: bool = False


class IRMitigationRiskPattern(BaseModel):
    """Mitigation risk pattern"""
    risk_pattern_ref: str
    threats: List[IRMitigationItem] = Field(default_factory=list)


class IRMitigationReport(BaseModel):
    """Mitigation report"""
    risk_patterns: List[IRMitigationRiskPattern] = Field(default_factory=list)


class IRSuggestions(BaseModel):
    """Suggestions"""
    library_suggestions: List[str] = Field(default_factory=list)
    threat_suggestions: List[str] = Field(default_factory=list)
    weakness_suggestions: List[str] = Field(default_factory=list)
    control_suggestions: List[str] = Field(default_factory=list)
    relation_suggestions: List['IRRelation'] = Field(default_factory=list)


class IRTestReport(BaseModel):
    """Test report"""
    tests: List[str] = Field(default_factory=list)
    num_failed_tests: int = 0
    num_success_tests: int = 0
    test_results: Dict[str, List[str]] = Field(default_factory=dict)


# Forward reference resolution
from .elements import IRRelation