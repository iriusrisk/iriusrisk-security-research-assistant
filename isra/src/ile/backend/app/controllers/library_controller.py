"""
Library controller for IriusRisk Content Manager API
"""

from fastapi import APIRouter, Depends
from typing import List, Collection
from isra.src.ile.backend.app.models import (
    IRComponentDefinition, IRRelation, IRRiskPattern, Graph, 
    IRLibraryReport, IRMitigationReport, ComponentRequest, 
    LibraryUpdateRequest, RelationRequest, RiskPatternRequest
)
from isra.src.ile.backend.app.facades.library_facade import LibraryFacade

router = APIRouter()


def get_library_facade() -> LibraryFacade:
    """Dependency injection for LibraryFacade"""
    return LibraryFacade()


@router.get("/version/{version_ref}/{library_ref}/report")
async def get_library_report(version_ref: str, library_ref: str, library_facade: LibraryFacade = Depends(get_library_facade)) -> IRLibraryReport:
    """Get library report"""
    return library_facade.create_library_report(version_ref, library_ref)


@router.get("/version/{version_ref}/{library_ref}/getRulesGraph")
async def get_rules_graph(version_ref: str, library_ref: str, library_facade: LibraryFacade = Depends(get_library_facade)) -> Graph:
    """Get rules graph"""
    return library_facade.create_rules_graph(version_ref, library_ref)


@router.get("/version/{version_ref}/{library_ref}/checkMitigation")
async def check_mitigation(version_ref: str, library_ref: str, library_facade: LibraryFacade = Depends(get_library_facade)) -> IRMitigationReport:
    """Check mitigation"""
    return library_facade.check_mitigation(version_ref, library_ref)


@router.get("/version/{version_ref}/{library_ref}/balanceMitigation")
async def balance_mitigation(version_ref: str, library_ref: str, library_facade: LibraryFacade = Depends(get_library_facade)) -> IRMitigationReport:
    """Balance mitigation"""
    library_facade.balance_mitigation(version_ref, library_ref)
    return library_facade.check_mitigation(version_ref, library_ref)


@router.get("/version/{version_ref}/{library_ref}/export/{format}")
async def export_library(version_ref: str, library_ref: str, format: str, library_facade: LibraryFacade = Depends(get_library_facade)) -> None:
    """Export library"""
    library_facade.export_library(version_ref, library_ref, format)


@router.put("/version/{version_ref}/{library_ref}")
async def update_library(version_ref: str, library_ref: str, body: LibraryUpdateRequest, library_facade: LibraryFacade = Depends(get_library_facade)) -> IRLibraryReport:
    """Update library"""
    library_facade.update_library(version_ref, library_ref, body)
    return library_facade.create_library_report(version_ref, library_ref)


@router.get("/version/{version_ref}/{library_ref}/relation")
async def list_relations(version_ref: str, library_ref: str, library_facade: LibraryFacade = Depends(get_library_facade)) -> List[IRRelation]:
    """List relations"""
    return library_facade.list_relations(version_ref, library_ref)


@router.post("/version/{version_ref}/{library_ref}/relation")
async def add_relation(version_ref: str, library_ref: str, body: RelationRequest, library_facade: LibraryFacade = Depends(get_library_facade)) -> IRRelation:
    """Add relation"""
    return library_facade.add_relation(version_ref, library_ref, body)


@router.put("/version/{version_ref}/{library_ref}/relation")
async def update_relation(version_ref: str, library_ref: str, body: IRRelation, library_facade: LibraryFacade = Depends(get_library_facade)) -> IRRelation:
    """Update relation"""
    return library_facade.update_relation(version_ref, library_ref, body)


@router.delete("/version/{version_ref}/{library_ref}/relation")
async def delete_relation(version_ref: str, library_ref: str, body: List[IRRelation], library_facade: LibraryFacade = Depends(get_library_facade)) -> None:
    """Delete relations"""
    for req in body:
        library_facade.delete_relation(version_ref, library_ref, req)


@router.get("/version/{version_ref}/{library_ref}/riskPattern")
async def list_risk_patterns(version_ref: str, library_ref: str, library_facade: LibraryFacade = Depends(get_library_facade)) -> List[IRRiskPattern]:
    """List risk patterns"""
    return library_facade.list_risk_patterns(version_ref, library_ref)


@router.post("/version/{version_ref}/{library_ref}/riskPattern")
async def add_risk_pattern(version_ref: str, library_ref: str, body: RiskPatternRequest, library_facade: LibraryFacade = Depends(get_library_facade)) -> IRRiskPattern:
    """Add risk pattern"""
    return library_facade.add_risk_pattern(version_ref, library_ref, body)


@router.put("/version/{version_ref}/{library_ref}/riskPattern")
async def update_risk_pattern(version_ref: str, library_ref: str, body: RiskPatternRequest, library_facade: LibraryFacade = Depends(get_library_facade)) -> IRRiskPattern:
    """Update risk pattern"""
    return library_facade.update_risk_pattern(version_ref, library_ref, body)


@router.delete("/version/{version_ref}/{library_ref}/riskPattern")
async def delete_risk_pattern(version_ref: str, library_ref: str, body: List[IRRiskPattern], library_facade: LibraryFacade = Depends(get_library_facade)) -> None:
    """Delete risk patterns"""
    for req in body:
        library_facade.delete_risk_pattern(version_ref, library_ref, req)


@router.get("/version/{version_ref}/{library_ref}/component")
async def list_components(version_ref: str, library_ref: str, library_facade: LibraryFacade = Depends(get_library_facade)) -> List[IRComponentDefinition]:
    """List components"""
    return library_facade.list_components(version_ref, library_ref)


@router.post("/version/{version_ref}/{library_ref}/component")
async def add_component(version_ref: str, library_ref: str, body: ComponentRequest, library_facade: LibraryFacade = Depends(get_library_facade)) -> IRComponentDefinition:
    """Add component"""
    return library_facade.add_component(version_ref, library_ref, body)


@router.put("/version/{version_ref}/{library_ref}/component")
async def update_component(version_ref: str, library_ref: str, body: IRComponentDefinition, library_facade: LibraryFacade = Depends(get_library_facade)) -> IRComponentDefinition:
    """Update component"""
    return library_facade.update_component(version_ref, library_ref, body)


@router.delete("/version/{version_ref}/{library_ref}/component")
async def delete_component(version_ref: str, library_ref: str, body: List[IRComponentDefinition], library_facade: LibraryFacade = Depends(get_library_facade)) -> None:
    """Delete components"""
    for req in body:
        library_facade.delete_component(version_ref, library_ref, req)
