"""
Version service for IriusRisk Content Manager API
"""

import json
import logging
import uuid
from pathlib import Path
from typing import Collection, List, Set

from fastapi import UploadFile

from isra.src.ile.backend.app.configuration.constants import ILEConstants
from isra.src.ile.backend.app.configuration.properties_manager import PropertiesManager
from isra.src.ile.backend.app.facades.io_facade import IOFacade
from isra.src.ile.backend.app.models import (
    ILEVersion, IRCategoryComponent, IRControl,
    IRLibrary, IRReference, IRRiskRating,
    IRStandard, IRSupportedStandard, IRThreat, IRUseCase, IRWeakness,
    IRSuggestions, IRVersionReport, CategoryRequest, CategoryUpdateRequest, ControlRequest,
    ControlUpdateRequest, ReferenceItemRequest, ReferenceRequest, ReferenceUpdateRequest,
    StandardItemRequest, StandardRequest, StandardUpdateRequest, SupportedStandardRequest,
    SupportedStandardUpdateRequest,
    ThreatRequest, ThreatUpdateRequest, UsecaseRequest, UsecaseUpdateRequest, WeaknessRequest
)
from isra.src.ile.backend.app.models.requests import WeaknessUpdateRequest
from isra.src.ile.backend.app.services.data_service import DataService

logger = logging.getLogger(__name__)


class VersionService:
    """Service for handling version operations"""

    def __init__(self):
        self.data_service = DataService()
        self.io_facade = IOFacade()

    def get_version(self, version_ref: str) -> ILEVersion:
        """Get version by reference"""
        return self.data_service.get_version(version_ref)

    def list_stored_versions(self) -> List[str]:
        """List stored versions"""
        versions_folder = Path(ILEConstants.VERSIONS_FOLDER)
        if not versions_folder.exists():
            return []

        return [
            f.name.replace(".irius", "")
            for f in versions_folder.iterdir()
            if f.is_file() and f.suffix == ".irius"
        ]

    def save_version(self, version_ref: str) -> None:
        """Save version to file"""
        logger.info(f"Saving version {version_ref}")
        version_path = Path(ILEConstants.VERSIONS_FOLDER) / f"{version_ref}.irius"

        try:
            v = self.data_service.get_version(version_ref)
            with open(version_path, 'w') as f:
                json.dump(v.model_dump(), f, indent=2)
            logger.info(f"Saving version success: {version_ref}")
        except Exception as e:
            raise RuntimeError("Failed to save version") from e

    def clean_version(self, version_ref: str) -> List[str]:
        """Clean unused elements from version"""
        logger.info(f"Cleaning version {version_ref}")
        removed_items = []
        v = self.data_service.get_version(version_ref)

        # Collect used elements
        used_risk_patterns: Set[str] = set()
        used_usecases: Set[str] = set()
        used_threats: Set[str] = set()
        used_weaknesses: Set[str] = set()
        used_controls: Set[str] = set()
        used_categories: Set[str] = set()
        used_references: Set[IRReference] = set()
        used_standards: Set[IRStandard] = set()
        used_supported_standards: Set[IRSupportedStandard] = set()

        for l in v.libraries.values():
            for comp in l.component_definitions.values():
                used_categories.add(comp.category_ref)
                used_risk_patterns.update(comp.risk_pattern_refs)

        # Remove unused elements (simplified implementation)
        # In a full implementation, you would remove unused elements here

        return removed_items

    def quick_reload_version(self, version_ref: str) -> None:
        """Quick reload version"""
        self.data_service.remove_version(version_ref)
        self.data_service.put_version(ILEVersion(version=version_ref))
        self.import_libraries_from_folder(version_ref)

    def create_version_report(self, version_ref: str) -> IRVersionReport:
        """Create version report"""
        return self.data_service.create_version_report(version_ref)

    def import_libraries_from_folder(self, version_ref: str) -> None:
        """Import libraries from configured folder"""
        folder = PropertiesManager.get_property(ILEConstants.MAIN_LIBRARY_FOLDER)
        if folder:
            folder_path = Path(folder)
            if folder_path.is_dir():
                self._import_files_recursively(folder_path, version_ref)

    def _import_files_recursively(self, directory: Path, version_ref: str) -> None:
        """Import files recursively from directory"""
        # Check if version exists, create it if it doesn't
        version = self.data_service.get_version(version_ref)
        if version is None:
            logger.info(f"Version {version_ref} does not exist, creating it")
            version = ILEVersion(version=version_ref)
            self.data_service.put_version(version)

        for file_path in directory.iterdir():
            if file_path.is_dir():
                self._import_files_recursively(file_path, version_ref)
            elif file_path.is_file():
                try:
                    if file_path.suffix == ".xml":
                        with open(file_path, 'rb') as f:
                            self.io_facade.import_library_xml(file_path.name, f, version)
                    elif file_path.suffix == ".xlsx":
                        with open(file_path, 'rb') as f:
                            self.io_facade.import_library_xlsx(file_path.name, f, version)
                    elif file_path.suffix == ".yaml":
                        with open(file_path, 'rb') as f:
                            self.io_facade.import_ysc_component(file_path.name, f, version)
                except Exception as e:
                    logger.error(f"Error when importing {file_path.name}: {e}")

    def import_library_to_version(self, version_ref: str, submissions: List[UploadFile]) -> None:
        """Import library files to version"""
        # Check if version exists, create it if it doesn't
        version = self.data_service.get_version(version_ref)
        if version is None:
            logger.info(f"Version {version_ref} does not exist, creating it")
            version = ILEVersion(version=version_ref)
            self.data_service.put_version(version)

        for file in submissions:
            try:
                filename = file.filename
                if filename.endswith(".xml"):
                    self.io_facade.import_library_xml(filename, file.file, version)
                elif filename.endswith(".xlsx"):
                    self.io_facade.import_library_xlsx(filename, file.file, version)
                elif filename.endswith(".yaml"):
                    self.io_facade.import_ysc_component(filename, file.file, version)
            except Exception as e:
                logger.error(f"Error when importing {file.filename}: {e}")
                raise RuntimeError("Error when importing") from e

    def export_version_to_folder(self, version_ref: str, format: str) -> None:
        """Export version to folder"""
        logger.info(f"Exporting {version_ref} to {format}")
        version = self.data_service.get_version(version_ref)
        if version is None:
            raise ValueError(f"Version '{version_ref}' not found")

        version_path = Path(ILEConstants.OUTPUT_FOLDER) / version.version
        version_path.mkdir(parents=True, exist_ok=True)

        try:
            for lib in version.libraries.values():
                if format == "xml":
                    self.io_facade.export_library_xml(lib, version, str(version_path))
                elif format == "xlsx":
                    self.io_facade.export_library_xlsx(lib, version, str(version_path))
        except Exception as e:
            logger.error(f"Error exporting version {version_ref}: {e}")
            raise RuntimeError("Error exporting version") from e

    def create_marketplace_release(self, version_ref: str) -> None:
        """Create marketplace release structure from version libraries"""
        logger.info(f"Creating marketplace release for version {version_ref}")
        version = self.data_service.get_version(version_ref)
        if version is None:
            raise ValueError(f"Version '{version_ref}' not found")

        # Load library structure from config folder
        library_structure_path = Path(ILEConstants.CONFIG_FOLDER) / "library_structure.json"
        if not library_structure_path.exists():
            raise FileNotFoundError(f"Library structure file not found at {library_structure_path}")

        with open(library_structure_path, 'r', encoding='utf-8') as f:
            library_structure = json.load(f)

        # Create mapping from library ref to package info
        library_to_package = {}
        for package_ref, package_info in library_structure.get("packages", {}).items():
            for library_ref in package_info.get("libraries", []):
                library_to_package[library_ref] = {
                    "package_ref": package_ref,
                    "type": package_info.get("type", "v2")
                }

        # Group libraries by package and type
        packages_by_type = {}  # {type: {package_ref: [library_refs]}}

        for library_ref, library in version.libraries.items():
            if library_ref in library_to_package:
                package_info = library_to_package[library_ref]
                package_type = package_info["type"]
                package_ref = package_info["package_ref"]

                if package_type not in packages_by_type:
                    packages_by_type[package_type] = {}
                if package_ref not in packages_by_type[package_type]:
                    packages_by_type[package_type][package_ref] = []

                packages_by_type[package_type][package_ref].append(library_ref)
            else:
                logger.warning(f"Library '{library_ref}' not found in library structure, skipping")

        # Create marketplace folder structure and export libraries
        marketplace_path = Path(ILEConstants.OUTPUT_FOLDER) / "marketplace"
        marketplace_path.mkdir(parents=True, exist_ok=True)

        try:
            for package_type, packages in packages_by_type.items():
                type_path = marketplace_path / package_type
                type_path.mkdir(parents=True, exist_ok=True)

                for package_ref, library_refs in packages.items():
                    package_path = type_path / package_ref
                    package_path.mkdir(parents=True, exist_ok=True)

                    # Export each library in the package
                    for library_ref in library_refs:
                        if library_ref in version.libraries:
                            library = version.libraries[library_ref]

                            # Save original filename
                            original_filename = library.filename

                            # Append revision number to filename
                            # Format: {base_name}_v{revision}.xml
                            filename_path = Path(original_filename)
                            base_name = filename_path.stem  # filename without extension
                            extension = filename_path.suffix or ".xml"
                            revision = library.revision or "0"

                            # Create new filename with revision
                            new_filename = f"{base_name}_v{revision}{extension}"
                            library.filename = new_filename

                            try:
                                self.io_facade.export_library_xml(library, version, str(package_path))
                                logger.info(
                                    f"Exported library '{library_ref}' (revision {revision}) to package '{package_ref}'"
                                    f" in {package_type} as '{new_filename}'")
                            finally:
                                # Restore original filename
                                library.filename = original_filename
                        else:
                            logger.warning(f"Library '{library_ref}' not found in version, skipping")

            logger.info(f"Marketplace release created successfully at {marketplace_path}")
        except Exception as e:
            logger.error(f"Error creating marketplace release for version {version_ref}: {e}")
            raise RuntimeError("Error creating marketplace release") from e

    def get_suggestions(self, version_ref: str, element_type: str, ref: str) -> IRSuggestions:
        """Get suggestions for element"""
        suggestions = IRSuggestions()
        v = self.data_service.get_version(version_ref)

        for library in v.libraries.values():
            for relation in library.relations.values():
                if element_type == "threat":
                    if relation.threat_uuid == ref:
                        suggestions.library_suggestions.append(library.ref)
                        if relation.weakness_uuid and relation.weakness_uuid != "":
                            suggestions.weakness_suggestions.append(relation.weakness_uuid)
                        if relation.control_uuid and relation.control_uuid != "":
                            suggestions.control_suggestions.append(relation.control_uuid)
                        suggestions.relation_suggestions.append(relation)
                elif element_type == "weakness":
                    if relation.weakness_uuid == ref:
                        suggestions.library_suggestions.append(library.ref)
                        if relation.threat_uuid and relation.threat_uuid != "":
                            suggestions.threat_suggestions.append(relation.threat_uuid)
                        if relation.control_uuid and relation.control_uuid != "":
                            suggestions.control_suggestions.append(relation.control_uuid)
                        suggestions.relation_suggestions.append(relation)
                elif element_type == "control":
                    if relation.control_uuid == ref:
                        suggestions.library_suggestions.append(library.ref)
                        if relation.threat_uuid and relation.threat_uuid != "":
                            suggestions.threat_suggestions.append(relation.threat_uuid)
                        if relation.weakness_uuid and relation.weakness_uuid != "":
                            suggestions.weakness_suggestions.append(relation.weakness_uuid)
                        suggestions.relation_suggestions.append(relation)

        return suggestions

    def fix_non_ascii_values(self, version_ref: str) -> None:
        """Fix non-ASCII values in version"""
        logger.info(f"Fixing non-ASCII values in version {version_ref}")
        version = self.data_service.get_version(version_ref)

        # Fix risk patterns in libraries
        for library in version.libraries.values():
            for risk_pattern in library.risk_patterns.values():
                risk_pattern.name = self._fix_ascii(risk_pattern.ref, risk_pattern.name)
                risk_pattern.desc = self._fix_ascii(risk_pattern.ref, risk_pattern.desc)

            # Fix component definitions in libraries
            for component_def in library.component_definitions.values():
                component_def.name = self._fix_ascii(component_def.ref, component_def.name)
                component_def.desc = self._fix_ascii(component_def.ref, component_def.desc)

        # Fix use cases
        for usecase in version.usecases.values():
            usecase.name = self._fix_ascii(usecase.ref, usecase.name)
            usecase.desc = self._fix_ascii(usecase.ref, usecase.desc)

        # Fix threats
        for threat in version.threats.values():
            threat.name = self._fix_ascii(threat.ref, threat.name)
            threat.desc = self._fix_ascii(threat.ref, threat.desc)

        # Fix weaknesses
        for weakness in version.weaknesses.values():
            weakness.name = self._fix_ascii(weakness.ref, weakness.name)
            weakness.desc = self._fix_ascii(weakness.ref, weakness.desc)
            weakness.test.steps = self._fix_ascii(weakness.ref, weakness.test.steps)

        # Fix controls
        for control in version.controls.values():
            control.name = self._fix_ascii(control.ref, control.name)
            control.desc = self._fix_ascii(control.ref, control.desc)
            control.test.steps = self._fix_ascii(control.ref, control.test.steps)

    def _fix_ascii(self, ref: str, text: str) -> str:
        """Fix non-ASCII characters in text"""
        if not text:
            return text

        result = text
        for char in text:
            code = ord(char)
            if code in ILEConstants.NON_ASCII_CODES:
                replacement = ILEConstants.NON_ASCII_CODES[code]
                logger.debug(f"{ref}: Replaced {char} with {replacement}")
                result = result.replace(char, replacement)

        return result

    # CRUD operations for various elements

    def list_supported_standards(self, version_ref: str) -> Collection[IRSupportedStandard]:
        """List supported standards"""
        return self.data_service.get_version(version_ref).supported_standards.values()

    def add_supported_standard(self, version_ref: str, st: SupportedStandardRequest) -> IRSupportedStandard:
        """Add supported standard"""
        v = self.data_service.get_version(version_ref)
        standard = IRSupportedStandard(
            supported_standard_ref=st.supported_standard_ref,
            supported_standard_name=st.supported_standard_name
        )
        v.supported_standards[standard.uuid] = standard
        return standard

    def update_supported_standard(self, version_ref: str,
                                  updated: SupportedStandardUpdateRequest) -> IRSupportedStandard:
        """Update supported standard"""
        v = self.data_service.get_version(version_ref)
        standard = v.supported_standards[updated.uuid]
        standard.supported_standard_ref = updated.supported_standard_ref
        standard.supported_standard_name = updated.supported_standard_name
        v.supported_standards[updated.uuid] = standard
        return standard

    def delete_supported_standard(self, version_ref: str, st: IRSupportedStandard) -> None:
        """Delete supported standard"""
        v = self.data_service.get_version(version_ref)
        v.supported_standards.pop(st.uuid, None)

    def list_standards(self, version_ref: str) -> Collection[IRStandard]:
        """List standards"""
        return self.data_service.get_version(version_ref).standards.values()

    def add_standard(self, version_ref: str, st: StandardRequest) -> IRStandard:
        """Add standard"""
        v = self.data_service.get_version(version_ref)
        standard = IRStandard(
            supported_standard_ref=st.supported_standard_ref,
            standard_ref=st.standard_ref
        )
        v.standards[standard.uuid] = standard
        return standard

    def update_standard(self, version_ref: str, updated: StandardUpdateRequest) -> IRStandard:
        """Update standard"""
        v = self.data_service.get_version(version_ref)
        standard = v.standards[updated.uuid]
        standard.supported_standard_ref = updated.supported_standard_ref
        standard.standard_ref = updated.standard_ref
        v.standards[updated.uuid] = standard
        return standard

    def delete_standard(self, version_ref: str, st: IRStandard) -> None:
        """Delete standard"""
        v = self.data_service.get_version(version_ref)
        v.standards.pop(st.uuid, None)

    def get_reference(self, version_ref: str, uuid: str) -> IRReference:
        """Get reference by UUID"""
        return self.data_service.get_version(version_ref).references.get(uuid)

    def list_references(self, version_ref: str) -> Collection[IRReference]:
        """List references"""
        return self.data_service.get_version(version_ref).references.values()

    def add_reference(self, version_ref: str, body: ReferenceRequest) -> IRReference:
        """Add reference"""
        v = self.data_service.get_version(version_ref)
        ref = IRReference(
            name=body.name,
            url=body.url
        )
        v.references[ref.uuid] = ref
        return ref

    def update_reference(self, version_ref: str, body: ReferenceUpdateRequest) -> IRReference:
        """Update reference"""
        v = self.data_service.get_version(version_ref)
        reference = v.references[body.uuid]
        reference.name = body.name
        reference.url = body.url
        v.references[body.uuid] = reference
        return reference

    def delete_reference(self, version_ref: str, body: IRReference) -> None:
        """Delete reference"""
        v = self.data_service.get_version(version_ref)
        v.references.pop(body.uuid, None)

    def list_categories(self, version_ref: str) -> Collection[IRCategoryComponent]:
        """List categories"""
        return self.data_service.get_version(version_ref).categories.values()

    def add_category(self, version_ref: str, body: CategoryRequest) -> IRCategoryComponent:
        """Add category"""
        v = self.data_service.get_version(version_ref)
        category = IRCategoryComponent(
            ref=body.ref,
            name=body.name,
            desc=""
        )
        v.categories[category.uuid] = category
        return category

    def update_category(self, version_ref: str, new_cat: CategoryUpdateRequest) -> IRCategoryComponent:
        """Update category"""
        v = self.data_service.get_version(version_ref)
        category = v.categories[new_cat.uuid]
        category.ref = new_cat.ref
        category.name = new_cat.name
        v.categories[new_cat.uuid] = category
        return category

    def delete_category(self, version_ref: str, ref: str) -> None:
        """Delete category"""
        v = self.data_service.get_version(version_ref)
        # Find category by ref and remove
        for uuid, cat in v.categories.items():
            if cat.ref == ref:
                v.categories.pop(uuid)
                break

    def list_controls(self, version_ref: str) -> Collection[IRControl]:
        """List controls"""
        return self.data_service.get_version(version_ref).controls.values()

    def add_control(self, version_ref: str, control: ControlRequest) -> IRControl:
        """Add control"""
        v = self.data_service.get_version(version_ref)
        ctrl = IRControl(
            ref=control.ref,
            name=control.name,
            desc=control.desc or "",
            state=control.state or "Recommended",
            cost=control.cost or "0",
            base_standard=control.base_standard or [],
            base_standard_section=control.base_standard_section or [],
            scope=control.scope or [],
            mitre=control.mitre or []
        )
        # Set test steps if provided
        if control.steps:
            ctrl.test.steps = control.steps
        v.controls[ctrl.uuid] = ctrl
        return ctrl

    def update_control(self, version_ref: str, new_control: ControlUpdateRequest) -> IRControl:
        """Update control"""
        v = self.data_service.get_version(version_ref)
        control = v.controls[new_control.uuid]

        if new_control.ref is not None:
            control.ref = new_control.ref
        if new_control.name is not None:
            control.name = new_control.name
        if new_control.desc is not None:
            control.desc = new_control.desc
        if new_control.state is not None:
            control.state = new_control.state
        if new_control.cost is not None:
            control.cost = new_control.cost
        if new_control.steps is not None:
            control.test.steps = new_control.steps
        if new_control.base_standard is not None:
            control.base_standard = new_control.base_standard
        if new_control.base_standard_section is not None:
            control.base_standard_section = new_control.base_standard_section
        if new_control.scope is not None:
            control.scope = new_control.scope
        if new_control.mitre is not None:
            control.mitre = new_control.mitre

        v.controls[control.uuid] = control
        return control

    def delete_control(self, version_ref: str, control: IRControl) -> None:
        """Delete control"""
        v = self.data_service.get_version(version_ref)
        v.controls.pop(control.uuid, None)

    def get_control(self, version_ref: str, uuid: str) -> IRControl:
        """Get control by UUID"""
        return self.data_service.get_version(version_ref).controls.get(uuid)

    def add_reference_to_element(self, version_ref: str, reference_item_request: ReferenceItemRequest) -> None:
        """Add reference to element"""
        v = self.data_service.get_version(version_ref)
        ref_uuid = reference_item_request.reference_uuid
        item_uuid = reference_item_request.item_uuid
        item_type = reference_item_request.item_type

        # Generate a unique key for the references map
        reference_key = str(uuid.uuid4())

        if item_type == "THREAT":
            if item_uuid in v.threats:
                v.threats[item_uuid].references[reference_key] = ref_uuid
        elif item_type == "CONTROL":
            if item_uuid in v.controls:
                v.controls[item_uuid].references[reference_key] = ref_uuid
        elif item_type == "CONTROL_TEST":
            if item_uuid in v.controls:
                v.controls[item_uuid].test.references[reference_key] = ref_uuid
        elif item_type == "WEAKNESS_TEST":
            if item_uuid in v.weaknesses:
                v.weaknesses[item_uuid].test.references[reference_key] = ref_uuid

    def delete_reference_from_element(self, version_ref: str, reference_item_request: ReferenceItemRequest) -> None:
        """Delete reference from element"""
        v = self.data_service.get_version(version_ref)
        ref_uuid = reference_item_request.reference_uuid
        item_uuid = reference_item_request.item_uuid
        item_type = reference_item_request.item_type

        if item_type == "THREAT":
            if item_uuid in v.threats:
                # Find and remove references that match the value (not the key)
                keys_to_remove = [key for key, value in v.threats[item_uuid].references.items()
                                  if value == ref_uuid]
                for key in keys_to_remove:
                    del v.threats[item_uuid].references[key]
        elif item_type == "CONTROL":
            if item_uuid in v.controls:
                keys_to_remove = [key for key, value in v.controls[item_uuid].references.items()
                                  if value == ref_uuid]
                for key in keys_to_remove:
                    del v.controls[item_uuid].references[key]
        elif item_type == "CONTROL_TEST":
            if item_uuid in v.controls:
                keys_to_remove = [key for key, value in v.controls[item_uuid].test.references.items()
                                  if value == ref_uuid]
                for key in keys_to_remove:
                    del v.controls[item_uuid].test.references[key]
        elif item_type == "WEAKNESS_TEST":
            if item_uuid in v.weaknesses:
                keys_to_remove = [key for key, value in v.weaknesses[item_uuid].test.references.items()
                                  if value == ref_uuid]
                for key in keys_to_remove:
                    del v.weaknesses[item_uuid].test.references[key]

    def add_standard_to_element(self, version_ref: str, standard_item_request: StandardItemRequest) -> None:
        """Add standard to element"""
        v = self.data_service.get_version(version_ref)
        item_uuid = standard_item_request.item_uuid
        standard_uuid = standard_item_request.standard_uuid
        item_type = standard_item_request.item_type

        # Generate a unique key for the standards map
        standard_key = str(uuid.uuid4())

        if item_type == "CONTROL":
            if item_uuid in v.controls:
                v.controls[item_uuid].standards[standard_key] = standard_uuid

    def delete_standard_from_element(self, version_ref: str, standard_item_request: StandardItemRequest) -> None:
        """Delete standard from element"""
        v = self.data_service.get_version(version_ref)
        item_uuid = standard_item_request.item_uuid
        standard_uuid = standard_item_request.standard_uuid
        item_type = standard_item_request.item_type

        if item_type == "CONTROL":
            if item_uuid in v.controls:
                # Find and remove standards that match the value (not the key)
                keys_to_remove = [key for key, value in v.controls[item_uuid].standards.items()
                                  if value == standard_uuid]
                for key in keys_to_remove:
                    del v.controls[item_uuid].standards[key]

    def list_weaknesses(self, version_ref: str) -> Collection[IRWeakness]:
        """List weaknesses"""
        return self.data_service.get_version(version_ref).weaknesses.values()

    def add_weakness(self, version_ref: str, weakness: WeaknessRequest) -> IRWeakness:
        """Add weakness"""
        v = self.data_service.get_version(version_ref)
        w = IRWeakness(
            ref=weakness.ref,
            name=weakness.name,
            desc=weakness.desc,
            impact=weakness.impact
        )
        v.weaknesses[w.uuid] = w
        return w

    def update_weakness(self, version_ref: str, new_weakness: WeaknessUpdateRequest) -> IRWeakness:
        """Update weakness"""
        v = self.data_service.get_version(version_ref)
        weakness = v.weaknesses[new_weakness.uuid]

        if new_weakness.ref is not None:
            weakness.ref = new_weakness.ref
        if new_weakness.name is not None:
            weakness.name = new_weakness.name
        if new_weakness.desc is not None:
            weakness.desc = new_weakness.desc
        if new_weakness.impact is not None:
            weakness.impact = new_weakness.impact

        v.weaknesses[weakness.uuid] = weakness
        return weakness

    def delete_weakness(self, version_ref: str, weakness: IRWeakness) -> None:
        """Delete weakness"""
        v = self.data_service.get_version(version_ref)
        v.weaknesses.pop(weakness.uuid, None)

    def get_weakness(self, version_ref: str, uuid: str) -> IRWeakness:
        """Get weakness by UUID"""
        return self.data_service.get_version(version_ref).weaknesses.get(uuid)

    def get_threat(self, version_ref: str, uuid: str) -> IRThreat:
        """Get threat by UUID"""
        return self.data_service.get_version(version_ref).threats.get(uuid)

    def list_threats(self, version_ref: str) -> Collection[IRThreat]:
        """List threats"""
        return self.data_service.get_version(version_ref).threats.values()

    def add_threat(self, version_ref: str, threat: ThreatRequest) -> IRThreat:
        """Add threat"""
        v = self.data_service.get_version(version_ref)
        t = IRThreat(
            ref=threat.ref,
            name=threat.name,
            desc=threat.desc,
            risk_rating=IRRiskRating(
                confidentiality=threat.risk_rating.confidentiality,
                integrity=threat.risk_rating.integrity,
                availability=threat.risk_rating.availability,
                ease_of_exploitation=threat.risk_rating.ease_of_exploitation
            ),
            mitre=threat.mitre,
            stride=threat.stride
        )
        v.threats[t.uuid] = t
        return t

    def update_threat(self, version_ref: str, new_threat: ThreatUpdateRequest) -> IRThreat:
        """Update threat"""
        v = self.data_service.get_version(version_ref)
        threat = v.threats[new_threat.uuid]

        if new_threat.ref is not None:
            threat.ref = new_threat.ref
        if new_threat.name is not None:
            threat.name = new_threat.name
        if new_threat.desc is not None:
            threat.desc = new_threat.desc
        if new_threat.risk_rating is not None:
            threat.risk_rating = IRRiskRating(
                confidentiality=new_threat.risk_rating.confidentiality,
                integrity=new_threat.risk_rating.integrity,
                availability=new_threat.risk_rating.availability,
                ease_of_exploitation=new_threat.risk_rating.ease_of_exploitation
            )
        if new_threat.mitre is not None:
            threat.mitre = new_threat.mitre
        if new_threat.stride is not None:
            threat.stride = new_threat.stride

        # Handle references to add
        if new_threat.references_to_add is not None:
            for ref_uuid in new_threat.references_to_add:
                # Add reference using UUID as both key and value
                threat.references[ref_uuid] = ref_uuid

        # Handle references to delete
        if new_threat.references_to_delete is not None:
            for ref_uuid in new_threat.references_to_delete:
                # Remove reference by finding and deleting entries with this UUID as value
                keys_to_delete = [key for key, value in threat.references.items() if value == ref_uuid]
                for key in keys_to_delete:
                    del threat.references[key]

        v.threats[threat.uuid] = threat
        return threat

    def delete_threat(self, version_ref: str, threat: IRThreat) -> None:
        """Delete threat"""
        v = self.data_service.get_version(version_ref)
        v.threats.pop(threat.uuid, None)

    def list_usecases(self, version_ref: str) -> Collection[IRUseCase]:
        """List use cases"""
        return self.data_service.get_version(version_ref).usecases.values()

    def add_usecase(self, version_ref: str, usecase: UsecaseRequest) -> IRUseCase:
        """Add use case"""
        v = self.data_service.get_version(version_ref)
        uc = IRUseCase(
            ref=usecase.ref,
            name=usecase.name,
            desc=usecase.desc
        )
        v.usecases[uc.uuid] = uc
        return uc

    def update_usecase(self, version_ref: str, new_usecase: UsecaseUpdateRequest) -> IRUseCase:
        """Update use case"""
        v = self.data_service.get_version(version_ref)
        if new_usecase.uuid not in v.usecases:
            raise ValueError(f"Use case with UUID {new_usecase.uuid} not found")
        usecase = v.usecases[new_usecase.uuid]
        usecase.ref = new_usecase.ref
        usecase.name = new_usecase.name
        usecase.desc = new_usecase.desc
        v.usecases[new_usecase.uuid] = usecase
        return usecase

    def delete_usecase(self, version_ref: str, usecase: IRUseCase) -> None:
        """Delete use case"""
        v = self.data_service.get_version(version_ref)
        v.usecases.pop(usecase.uuid, None)

    def list_libraries(self, version_ref: str) -> Collection[str]:
        """List libraries"""
        return self.data_service.get_version(version_ref).libraries.keys()

    def create_library(self, version_ref: str, library_ref: str) -> IRLibrary:
        """Create library"""
        v = self.data_service.get_version(version_ref)
        library = IRLibrary(
            ref=library_ref,
            name=library_ref,
            desc="",
            version="1",
            filename=f"{library_ref}.xml",
            visible="true"
        )
        v.libraries[library_ref] = library
        return library

    def increment_library_revision(self, version_ref: str, library_ref: str) -> None:
        """Increment library revision"""
        v = self.data_service.get_version(version_ref)
        library = v.libraries[library_ref]
        current_rev = int(library.revision)
        library.revision = str(current_rev + 1)

    def delete_library(self, version_ref: str, library_ref: str) -> None:
        """Delete library"""
        v = self.data_service.get_version(version_ref)
        v.libraries.pop(library_ref, None)
