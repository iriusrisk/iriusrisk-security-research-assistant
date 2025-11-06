"""
Version controller for IriusRisk Content Manager API
"""

from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException

from isra.src.ile.backend.app import WeaknessUpdateRequest
from isra.src.ile.backend.app.facades.version_facade import VersionFacade
from isra.src.ile.backend.app.models import (
    ILEVersion, IRCategoryComponent, IRControl, IRLibrary, IRReference,
    IRStandard, IRSupportedStandard, IRThreat, IRUseCase, IRWeakness,
    IRSuggestions, IRVersionReport, CategoryRequest, CategoryUpdateRequest, ControlRequest,
    ControlUpdateRequest, LibraryRequest, ReferenceItemRequest,
    StandardItemRequest, ReferenceRequest, ReferenceUpdateRequest, StandardRequest, StandardUpdateRequest,
    SuggestionRequest, SupportedStandardRequest, SupportedStandardUpdateRequest, ThreatRequest,
    ThreatUpdateRequest, UsecaseRequest, UsecaseUpdateRequest, WeaknessRequest
)

router = APIRouter()


def get_version_facade() -> VersionFacade:
    """Dependency injection for VersionFacade"""
    return VersionFacade()


@router.get("/version/list")
async def list_stored_versions(version_facade: VersionFacade = Depends(get_version_facade)) -> List[str]:
    """List stored versions"""
    return version_facade.list_stored_versions()


@router.get("/version/{version_ref}")
async def get_version(version_ref: str, version_facade: VersionFacade = Depends(get_version_facade)) -> ILEVersion:
    """Get version"""
    return version_facade.get_version(version_ref)


@router.get("/version/{version_ref}/save")
async def save_version(version_ref: str, version_facade: VersionFacade = Depends(get_version_facade)) -> None:
    """Save version"""
    version_facade.save_version(version_ref)


@router.get("/version/{version_ref}/clean")
async def clean_version(version_ref: str, version_facade: VersionFacade = Depends(get_version_facade)) -> List[str]:
    """Clean version"""
    return version_facade.clean_version(version_ref)


@router.post("/version/{version_ref}/import", status_code=200)
async def import_library_to_version(version_ref: str, files: List[UploadFile] = File(...),
                                    version_facade: VersionFacade = Depends(get_version_facade)) -> dict:
    """Import library to version"""
    version_facade.import_library_to_version(version_ref, files)
    return {"status": "success", "message": "Library imported successfully"}


@router.get("/version/{version_ref}/import/folder")
async def import_libraries_from_folder(version_ref: str,
                                       version_facade: VersionFacade = Depends(get_version_facade)) -> None:
    """Import libraries from folder"""
    version_facade.import_libraries_from_folder(version_ref)


@router.get("/version/{version_ref}/export/{format}")
async def export_version_to_folder_xml(version_ref: str, format: str,
                                       version_facade: VersionFacade = Depends(get_version_facade)) -> None:
    """Export version to folder"""
    version_facade.export_version_to_folder(version_ref, format)


@router.get("/version/{version_ref}/marketplace/release")
async def create_marketplace_release(version_ref: str,
                                      version_facade: VersionFacade = Depends(get_version_facade)) -> dict:
    """Create marketplace release structure"""
    try:
        version_facade.create_marketplace_release(version_ref)
        return {"status": "success", "message": f"Marketplace release created successfully for version {version_ref}"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating marketplace release: {str(e)}")


@router.get("/version/{version_ref}/quickreload")
async def quick_reload(version_ref: str, version_facade: VersionFacade = Depends(get_version_facade)) -> None:
    """Quick reload version"""
    version_facade.quick_reload_version(version_ref)


@router.post("/version/{version_ref}/suggestions")
async def get_suggestions_for_element(version_ref: str, body: SuggestionRequest,
                                      version_facade: VersionFacade = Depends(get_version_facade)) -> IRSuggestions:
    """Get suggestions for element"""
    return version_facade.get_suggestions(version_ref, body.type, body.ref)


@router.get("/version/{version_ref}/fix/ascii")
async def fix_non_ascii_values(version_ref: str, version_facade: VersionFacade = Depends(get_version_facade)) -> None:
    """Fix non-ASCII values"""
    version_facade.fix_non_ascii_values(version_ref)


@router.get("/version/{version_ref}/report")
async def get_version_report(version_ref: str,
                             version_facade: VersionFacade = Depends(get_version_facade)) -> IRVersionReport:
    """Get version report"""
    try:
        return version_facade.create_version_report(version_ref)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/version/{version_ref}/library")
async def list_libraries(version_ref: str, version_facade: VersionFacade = Depends(get_version_facade)) -> List[str]:
    """List libraries"""
    return version_facade.list_libraries(version_ref)


@router.post("/version/{version_ref}/library")
async def create_library(version_ref: str, library_request: LibraryRequest,
                         version_facade: VersionFacade = Depends(get_version_facade)) -> IRLibrary:
    """Create library"""
    return version_facade.create_library(version_ref, library_request.library_ref)


@router.put("/version/{version_ref}/library")
async def increment_library_revision(version_ref: str, library_request: LibraryRequest,
                                     version_facade: VersionFacade = Depends(get_version_facade)) -> None:
    """Increment library revision"""
    version_facade.increment_library_revision(version_ref, library_request.library_ref)


@router.delete("/version/{version_ref}/library")
async def delete_library(version_ref: str, library_request: LibraryRequest,
                         version_facade: VersionFacade = Depends(get_version_facade)) -> None:
    """Delete library"""
    version_facade.delete_library(version_ref, library_request.library_ref)


@router.get("/version/{version_ref}/reference")
async def list_references(version_ref: str, version_facade: VersionFacade = Depends(get_version_facade)) -> List[
    IRReference]:
    """List references"""
    return version_facade.list_references(version_ref)


@router.get("/version/{version_ref}/reference/{uuid}")
async def get_reference(version_ref: str, uuid: str,
                        version_facade: VersionFacade = Depends(get_version_facade)) -> IRReference:
    """Get reference by UUID"""
    return version_facade.get_reference(version_ref, uuid)


@router.post("/version/{version_ref}/reference")
async def add_reference(version_ref: str, body: ReferenceRequest,
                        version_facade: VersionFacade = Depends(get_version_facade)) -> IRReference:
    """Add reference"""
    return version_facade.add_reference(version_ref, body)


@router.put("/version/{version_ref}/reference")
async def update_reference(version_ref: str, body: ReferenceUpdateRequest,
                           version_facade: VersionFacade = Depends(get_version_facade)) -> IRReference:
    """Update reference"""
    return version_facade.update_reference(version_ref, body)


@router.delete("/version/{version_ref}/reference")
async def delete_references(version_ref: str, body: List[IRReference],
                            version_facade: VersionFacade = Depends(get_version_facade)) -> None:
    """Delete references"""
    for ref in body:
        version_facade.delete_reference(version_ref, ref)


@router.get("/version/{version_ref}/category")
async def list_categories(version_ref: str, version_facade: VersionFacade = Depends(get_version_facade)) -> List[
    IRCategoryComponent]:
    """List categories"""
    return version_facade.list_categories(version_ref)


@router.post("/version/{version_ref}/category")
async def add_category(version_ref: str, body: CategoryRequest,
                       version_facade: VersionFacade = Depends(get_version_facade)) -> IRCategoryComponent:
    """Add category"""
    return version_facade.add_category(version_ref, body)


@router.put("/version/{version_ref}/category")
async def update_category(version_ref: str, body: CategoryUpdateRequest,
                          version_facade: VersionFacade = Depends(get_version_facade)) -> IRCategoryComponent:
    """Update category"""
    return version_facade.update_category(version_ref, body)


@router.delete("/version/{version_ref}/category")
async def delete_category(version_ref: str, body: List[IRCategoryComponent],
                          version_facade: VersionFacade = Depends(get_version_facade)) -> None:
    """Delete categories"""
    for category in body:
        version_facade.delete_category(version_ref, category.uuid)


@router.get("/version/{version_ref}/supportedStandard")
async def list_supported_standards(version_ref: str, version_facade: VersionFacade = Depends(get_version_facade)) -> \
List[IRSupportedStandard]:
    """List supported standards"""
    return version_facade.list_supported_standards(version_ref)


@router.post("/version/{version_ref}/supportedStandard")
async def add_supported_standard(version_ref: str, body: SupportedStandardRequest,
                                 version_facade: VersionFacade = Depends(get_version_facade)) -> IRSupportedStandard:
    """Add supported standard"""
    return version_facade.add_supported_standard(version_ref, body)


@router.put("/version/{version_ref}/supportedStandard")
async def update_supported_standard(version_ref: str, body: SupportedStandardUpdateRequest,
                                    version_facade: VersionFacade = Depends(get_version_facade)) -> IRSupportedStandard:
    """Update supported standard"""
    return version_facade.update_supported_standard(version_ref, body)


@router.delete("/version/{version_ref}/supportedStandard")
async def delete_supported_standard(version_ref: str, body: List[IRSupportedStandard],
                                    version_facade: VersionFacade = Depends(get_version_facade)) -> None:
    """Delete supported standards"""
    for req in body:
        version_facade.delete_supported_standard(version_ref, req)


@router.get("/version/{version_ref}/standard")
async def list_standards(version_ref: str, version_facade: VersionFacade = Depends(get_version_facade)) -> List[
    IRStandard]:
    """List standards"""
    return version_facade.list_standards(version_ref)


@router.post("/version/{version_ref}/standard")
async def add_standard(version_ref: str, body: StandardRequest,
                       version_facade: VersionFacade = Depends(get_version_facade)) -> IRStandard:
    """Add standard"""
    return version_facade.add_standard(version_ref, body)


@router.put("/version/{version_ref}/standard")
async def update_standard(version_ref: str, body: StandardUpdateRequest,
                          version_facade: VersionFacade = Depends(get_version_facade)) -> IRStandard:
    """Update standard"""
    return version_facade.update_standard(version_ref, body)


@router.delete("/version/{version_ref}/standard")
async def delete_standard(version_ref: str, body: List[IRStandard],
                          version_facade: VersionFacade = Depends(get_version_facade)) -> None:
    """Delete standards"""
    for req in body:
        version_facade.delete_standard(version_ref, req)


@router.get("/version/{version_ref}/control")
async def list_controls(version_ref: str, version_facade: VersionFacade = Depends(get_version_facade)) -> List[
    IRControl]:
    """List controls"""
    return version_facade.list_controls(version_ref)


@router.post("/version/{version_ref}/control")
async def add_control(version_ref: str, body: ControlRequest,
                      version_facade: VersionFacade = Depends(get_version_facade)) -> IRControl:
    """Add control"""
    return version_facade.add_control(version_ref, body)


@router.put("/version/{version_ref}/control")
async def update_control(version_ref: str, body: ControlUpdateRequest,
                         version_facade: VersionFacade = Depends(get_version_facade)) -> IRControl:
    """Update control"""
    return version_facade.update_control(version_ref, body)


@router.delete("/version/{version_ref}/control")
async def delete_controls(version_ref: str, body: List[IRControl],
                          version_facade: VersionFacade = Depends(get_version_facade)) -> None:
    """Delete controls"""
    for req in body:
        version_facade.delete_control(version_ref, req)


@router.put("/version/{version_ref}/control/reference")
async def add_reference_to_control(version_ref: str, body: ReferenceItemRequest,
                                   version_facade: VersionFacade = Depends(get_version_facade)) -> IRControl:
    """Add reference to control"""
    return version_facade.add_reference_to_control(version_ref, body)


@router.delete("/version/{version_ref}/control/reference")
async def delete_reference_from_control(version_ref: str, body: ReferenceItemRequest,
                                        version_facade: VersionFacade = Depends(get_version_facade)) -> IRControl:
    """Delete reference from control"""
    return version_facade.delete_reference_from_control(version_ref, body)


@router.put("/version/{version_ref}/control/standard")
async def add_standard_to_control(version_ref: str, body: StandardItemRequest,
                                  version_facade: VersionFacade = Depends(get_version_facade)) -> IRControl:
    """Add standard to control"""
    return version_facade.add_standard_to_control(version_ref, body)


@router.delete("/version/{version_ref}/control/standard")
async def delete_standard_from_control(version_ref: str, body: StandardItemRequest,
                                       version_facade: VersionFacade = Depends(get_version_facade)) -> IRControl:
    """Delete standard from control"""
    return version_facade.delete_standard_from_control(version_ref, body)


@router.get("/version/{version_ref}/weakness")
async def list_weaknesses(version_ref: str, version_facade: VersionFacade = Depends(get_version_facade)) -> List[
    IRWeakness]:
    """List weaknesses"""
    return version_facade.list_weaknesses(version_ref)


@router.post("/version/{version_ref}/weakness")
async def add_weakness(version_ref: str, body: WeaknessRequest,
                       version_facade: VersionFacade = Depends(get_version_facade)) -> IRWeakness:
    """Add weakness"""
    return version_facade.add_weakness(version_ref, body)


@router.put("/version/{version_ref}/weakness")
async def update_weakness(version_ref: str, body: WeaknessUpdateRequest,
                          version_facade: VersionFacade = Depends(get_version_facade)) -> IRWeakness:
    """Update weakness"""
    return version_facade.update_weakness(version_ref, body)


@router.delete("/version/{version_ref}/weakness")
async def delete_weakness(version_ref: str, body: List[IRWeakness],
                          version_facade: VersionFacade = Depends(get_version_facade)) -> None:
    """Delete weaknesses"""
    for req in body:
        version_facade.delete_weakness(version_ref, req)


@router.put("/version/{version_ref}/weakness/reference")
async def add_reference_to_weakness(version_ref: str, body: ReferenceItemRequest,
                                    version_facade: VersionFacade = Depends(get_version_facade)) -> IRWeakness:
    """Add reference to weakness"""
    return version_facade.add_reference_to_weakness(version_ref, body)


@router.delete("/version/{version_ref}/weakness/reference")
async def delete_reference_from_weakness(version_ref: str, body: ReferenceItemRequest,
                                         version_facade: VersionFacade = Depends(get_version_facade)) -> IRWeakness:
    """Delete reference from weakness"""
    return version_facade.delete_reference_from_weakness(version_ref, body)


@router.get("/version/{version_ref}/usecase")
async def list_usecases(version_ref: str, version_facade: VersionFacade = Depends(get_version_facade)) -> List[
    IRUseCase]:
    """List use cases"""
    return version_facade.list_usecases(version_ref)


@router.post("/version/{version_ref}/usecase")
async def add_usecase(version_ref: str, body: UsecaseRequest,
                      version_facade: VersionFacade = Depends(get_version_facade)) -> IRUseCase:
    """Add use case"""
    return version_facade.add_usecase(version_ref, body)


@router.put("/version/{version_ref}/usecase")
async def update_usecase(version_ref: str, body: UsecaseUpdateRequest,
                         version_facade: VersionFacade = Depends(get_version_facade)) -> IRUseCase:
    """Update use case"""
    try:
        return version_facade.update_usecase(version_ref, body)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/version/{version_ref}/usecase")
async def delete_usecase(version_ref: str, body: List[IRUseCase],
                         version_facade: VersionFacade = Depends(get_version_facade)) -> None:
    """Delete use cases"""
    for usecase in body:
        version_facade.delete_usecase(version_ref, usecase)


@router.get("/version/{version_ref}/threat")
async def list_threats(version_ref: str, version_facade: VersionFacade = Depends(get_version_facade)) -> List[IRThreat]:
    """List threats"""
    return version_facade.list_threats(version_ref)


@router.post("/version/{version_ref}/threat")
async def add_threat(version_ref: str, body: ThreatRequest,
                     version_facade: VersionFacade = Depends(get_version_facade)) -> IRThreat:
    """Add threat"""
    return version_facade.add_threat(version_ref, body)


@router.put("/version/{version_ref}/threat")
async def update_threat(version_ref: str, body: ThreatUpdateRequest,
                        version_facade: VersionFacade = Depends(get_version_facade)) -> IRThreat:
    """Update threat"""
    return version_facade.update_threat(version_ref, body)


@router.delete("/version/{version_ref}/threat")
async def delete_threat(version_ref: str, body: List[IRThreat],
                        version_facade: VersionFacade = Depends(get_version_facade)) -> None:
    """Delete threats"""
    for req in body:
        version_facade.delete_threat(version_ref, req)


@router.put("/version/{version_ref}/threat/reference")
async def add_reference_to_threat(version_ref: str, body: ReferenceItemRequest,
                                  version_facade: VersionFacade = Depends(get_version_facade)) -> IRThreat:
    """Add reference to threat"""
    return version_facade.add_reference_to_threat(version_ref, body)


@router.delete("/version/{version_ref}/threat/reference")
async def delete_reference_from_threat(version_ref: str, body: ReferenceItemRequest,
                                       version_facade: VersionFacade = Depends(get_version_facade)) -> IRThreat:
    """Delete reference from threat"""
    return version_facade.delete_reference_from_threat(version_ref, body)
