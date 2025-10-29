from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class VersionNamesResponse(BaseModel):
    """Version names response"""
    project: str
    versions: List[str] = Field(default_factory=list)


class ILEError(BaseModel):
    """Error response"""
    message: str
    code: Optional[str] = None


# Request models
class CategoryRequest(BaseModel):
    ref: str
    name: str


class ComponentRequest(BaseModel):
    ref: str
    name: str
    desc: str
    category_ref: str
    visible: str


class ControlRequest(BaseModel):
    uuid: str
    ref: str
    name: str
    desc: str
    state: str
    cost: str
    steps: str
    base_standard: List[str]
    base_standard_section: List[str]
    scope: List[str]
    mitre: List[str]


class ControlUpdateRequest(BaseModel):
    uuid: str
    ref: str
    name: str
    desc: str
    state: str
    cost: str
    steps: str
    base_standard: List[str]
    base_standard_section: List[str]
    scope: List[str]
    mitre: List[str]


class LibraryRequest(BaseModel):
    library_ref: str


class LibraryUpdateRequest(BaseModel):
    ref: str
    name: str
    desc: str
    revision: str
    filename: str
    enabled: str


class MergeLibraryRequest(BaseModel):
    src_version: str
    src_library: str
    dst_version: str
    dst_library: str


class ReferenceRequest(BaseModel):
    name: str
    url: str


class ReferenceItemRequest(BaseModel):
    ref: str
    name: str
    url: str


class RelationRequest(BaseModel):
    risk_pattern_uuid: str
    usecase_uuid: str
    threat_uuid: str
    weakness_uuid: str
    control_uuid: str
    mitigation: str


class RiskPatternRequest(BaseModel):
    ref: str
    name: str
    desc: str


class RiskRatingRequest(BaseModel):
    confidentiality: str
    integrity: str
    availability: str
    ease_of_exploitation: str


class StandardRequest(BaseModel):
    supported_standard_ref: str
    standard_ref: str


class StandardItemRequest(BaseModel):
    ref: str
    supported_standard_ref: str
    standard_ref: str


class SupportedStandardRequest(BaseModel):
    supported_standard_ref: str
    supported_standard_name: str


class TestRequest(BaseModel):
    steps: str


class ThreatRequest(BaseModel):
    ref: str
    name: str
    desc: str


class ThreatUpdateRequest(BaseModel):
    ref: str
    name: str
    desc: str


class UsecaseRequest(BaseModel):
    ref: str
    name: str
    desc: str


class WeaknessRequest(BaseModel):
    ref: str
    name: str
    desc: str
    impact: str


class CopyVersionRequest(BaseModel):
    src_version: str
    ref: str


class ChangelogRequest(BaseModel):
    from_version: str
    to_version: str
    first_version: Optional[str] = None
    first_library: Optional[str] = None
    second_version: Optional[str] = None
    second_library: Optional[str] = None
    library_ref: Optional[str] = None


class ChangelogVersionRequest(BaseModel):
    version: str


class ContentReportRequest(BaseModel):
    version: str
    library: str


class SuggestionRequest(BaseModel):
    text: str