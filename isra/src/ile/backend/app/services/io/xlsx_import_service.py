"""
XLSX import service for IriusRisk Library Editor API
"""

import logging
import uuid
from typing import BinaryIO, List, Optional

import pandas as pd

from isra.src.ile.backend.app.configuration import ExcelConstants
from isra.src.ile.backend.app.models import (
    ILEVersion, IRCategoryComponent, IRComponentDefinition, IRControl,
    IRLibrary, IRReference, IRRelation, IRRiskPattern, IRRiskRating,
    IRRule, IRRuleAction, IRRuleCondition, IRStandard, IRSupportedStandard,
    IRTest, IRThreat, IRUseCase, IRWeakness
)

logger = logging.getLogger(__name__)


class XLSXImportService:
    """Service for importing XLSX library files"""
    
    def import_library_xlsx(self, filename: str, library: BinaryIO, version_element: ILEVersion) -> None:
        """Import library from XLSX stream"""
        try:
            filename = filename.replace("xlsx", "xml").replace("xls", "xml")
            
            # Load workbook using pandas
            # Note: pandas requires openpyxl or xlrd engine for .xlsx files
            # We use 'openpyxl' explicitly but this could be made configurable
            excel_file = pd.ExcelFile(library, engine='openpyxl')
            
            # Library properties
            properties_df = pd.read_excel(excel_file, sheet_name="Library properties", header=None)
            library_name = properties_df.iloc[1, 1] if len(properties_df) > 1 and properties_df.iloc[1, 1] is not pd.NA else ""
            library_ref = properties_df.iloc[2, 1] if len(properties_df) > 2 and properties_df.iloc[2, 1] is not pd.NA else ""
            library_desc = properties_df.iloc[3, 1] if len(properties_df) > 3 and properties_df.iloc[3, 1] is not pd.NA else ""
            library_revision = properties_df.iloc[4, 1] if len(properties_df) > 4 and properties_df.iloc[4, 1] is not pd.NA else "1"
            library_enabled = properties_df.iloc[5, 1] if len(properties_df) > 5 and properties_df.iloc[5, 1] is not pd.NA else "true"
            
            if not library_enabled or pd.isna(library_enabled):
                library_enabled = "true"
            
            new_library = IRLibrary(
                ref=str(library_ref) if not pd.isna(library_ref) else "",
                name=str(library_name) if not pd.isna(library_name) else "",
                desc=str(library_desc) if not pd.isna(library_desc) else "",
                revision=str(library_revision) if not pd.isna(library_revision) else "1",
                filename=filename,
                enabled=str(library_enabled) if not pd.isna(library_enabled) else "true"
            )
            
            # Import various elements
            self._add_references_from_excel(version_element, excel_file)
            self._add_supported_standards_from_excel(version_element, excel_file)
            self._add_standards_from_excel(version_element, excel_file)
            self._add_category_components_from_excel(version_element, excel_file)
            self._add_component_definitions_from_excel(new_library, excel_file)
            self._add_risk_patterns_from_excel(new_library, excel_file)
            self._add_usecases_from_excel(version_element, excel_file)
            self._add_threats_from_excel(version_element, excel_file)
            self._add_weaknesses_from_excel(version_element, excel_file)
            self._add_controls_from_excel(version_element, excel_file)
            self._add_relations_from_excel(new_library, excel_file)
            self._add_rules_from_excel(new_library, excel_file)
            
            logger.info(f"Adding new library {library_ref} to version {version_element.version}")
            version_element.libraries[library_ref] = new_library
            
        except Exception as e:
            logger.error(f"Error importing XLSX library {filename}: {e}")
            raise RuntimeError(f"Failed to import XLSX library: {e}") from e
    
    def _add_category_components_from_excel(self, version: ILEVersion, excel_file: pd.ExcelFile) -> None:
        """Add category components from Excel sheet"""
        try:
            df = pd.read_excel(excel_file, sheet_name="Components", header=0)
            for _, row in df.iterrows():
                category_ref = row.iloc[ExcelConstants.COMPONENTS_CATEGORY_REF] if len(row) > ExcelConstants.COMPONENTS_CATEGORY_REF else None
                if category_ref and pd.notna(category_ref):
                    category_ref = str(category_ref)
                    if category_ref not in version.categories:
                        category_name = row.iloc[ExcelConstants.COMPONENTS_CATEGORY_NAME] if len(row) > ExcelConstants.COMPONENTS_CATEGORY_NAME else ""
                        category_uuid = row.iloc[ExcelConstants.COMPONENTS_CATEGORY_UUID] if len(row) > ExcelConstants.COMPONENTS_CATEGORY_UUID else ""
                        category_component = IRCategoryComponent(
                            uuid=str(category_uuid) if pd.notna(category_uuid) else "",
                            ref=category_ref,
                            name=str(category_name) if pd.notna(category_name) else ""
                        )
                        if category_uuid and pd.notna(category_uuid):
                            version.categories[str(category_uuid)] = category_component
        except Exception as e:
            logger.warning(f"Error reading Components sheet for categories: {e}")
    
    def _add_component_definitions_from_excel(self, lib: IRLibrary, excel_file: pd.ExcelFile) -> None:
        """Add component definitions from Excel sheet"""
        try:
            df = pd.read_excel(excel_file, sheet_name="Components", header=0)
            for _, row in df.iterrows():
                component_ref = row.iloc[ExcelConstants.COMPONENTS_COMPONENT_REF] if len(row) > ExcelConstants.COMPONENTS_COMPONENT_REF else None
                if component_ref and pd.notna(component_ref):
                    component_name = row.iloc[ExcelConstants.COMPONENTS_COMPONENT_NAME] if len(row) > ExcelConstants.COMPONENTS_COMPONENT_NAME else ""
                    component_desc = row.iloc[ExcelConstants.COMPONENTS_COMPONENT_DESC] if len(row) > ExcelConstants.COMPONENTS_COMPONENT_DESC else ""
                    category_ref = row.iloc[ExcelConstants.COMPONENTS_CATEGORY_REF] if len(row) > ExcelConstants.COMPONENTS_CATEGORY_REF else ""
                    risk_patterns_str = row.iloc[ExcelConstants.COMPONENTS_RISK_PATTERNS] if len(row) > ExcelConstants.COMPONENTS_RISK_PATTERNS else ""
                    visible = row.iloc[ExcelConstants.COMPONENTS_VISIBLE] if len(row) > ExcelConstants.COMPONENTS_VISIBLE else ""
                    component_uuid = row.iloc[ExcelConstants.COMPONENTS_COMPONENT_UUID] if len(row) > ExcelConstants.COMPONENTS_COMPONENT_UUID else ""
                    
                    component_definition = IRComponentDefinition(
                        uuid=str(component_uuid) if pd.notna(component_uuid) else "",
                        ref=str(component_ref),
                        name=str(component_name) if pd.notna(component_name) else "",
                        desc=str(component_desc) if pd.notna(component_desc) else "",
                        category_ref=str(category_ref) if pd.notna(category_ref) else "",
                        visible=str(visible) if pd.notna(visible) else ""
                    )
                    
                    if risk_patterns_str and pd.notna(risk_patterns_str):
                        risk_patterns = [rp.strip() for rp in str(risk_patterns_str).split(",") if rp.strip()]
                        component_definition.risk_pattern_refs = risk_patterns
                    
                    if component_uuid and pd.notna(component_uuid):
                        lib.component_definitions[str(component_uuid)] = component_definition
        except Exception as e:
            logger.warning(f"Error reading Components sheet: {e}")
    
    def _add_supported_standards_from_excel(self, version: ILEVersion, excel_file: pd.ExcelFile) -> None:
        """Add supported standards from Excel sheet"""
        try:
            df = pd.read_excel(excel_file, sheet_name="Supported standards", header=0)
            for _, row in df.iterrows():
                supported_standard_ref = row.iloc[ExcelConstants.SUPPORTED_STANDARD_REF] if len(row) > ExcelConstants.SUPPORTED_STANDARD_REF else None
                if supported_standard_ref and pd.notna(supported_standard_ref):
                    supported_standard_name = row.iloc[ExcelConstants.SUPPORTED_STANDARD_NAME] if len(row) > ExcelConstants.SUPPORTED_STANDARD_NAME else ""
                    supported_standard_uuid = row.iloc[ExcelConstants.SUPPORTED_STANDARD_UUID] if len(row) > ExcelConstants.SUPPORTED_STANDARD_UUID else ""
                    supported_standard = IRSupportedStandard(
                        uuid=str(supported_standard_uuid) if pd.notna(supported_standard_uuid) else "",
                        supported_standard_ref=str(supported_standard_ref),
                        supported_standard_name=str(supported_standard_name) if pd.notna(supported_standard_name) else ""
                    )
                    if supported_standard_uuid and pd.notna(supported_standard_uuid):
                        version.supported_standards[str(supported_standard_uuid)] = supported_standard
        except Exception as e:
            logger.warning(f"Error reading Supported standards sheet: {e}")
    
    def _add_standards_from_excel(self, version: ILEVersion, excel_file: pd.ExcelFile) -> None:
        """Add standards from Excel sheet"""
        try:
            df = pd.read_excel(excel_file, sheet_name="Standards", header=0)
            for _, row in df.iterrows():
                supported_standard_ref = row.iloc[0] if len(row) > 0 else None
                if supported_standard_ref and pd.notna(supported_standard_ref):
                    standard_ref = row.iloc[1] if len(row) > 1 else ""
                    standard_uuid = row.iloc[2] if len(row) > 2 else ""
                    standard = IRStandard(
                        uuid=str(standard_uuid) if pd.notna(standard_uuid) else "",
                        supported_standard_ref=str(supported_standard_ref),
                        standard_ref=str(standard_ref) if pd.notna(standard_ref) else ""
                    )
                    if standard_uuid and pd.notna(standard_uuid):
                        version.standards[str(standard_uuid)] = standard
        except Exception as e:
            logger.warning(f"Error reading Standards sheet: {e}")
    
    def _add_rules_from_excel(self, lib: IRLibrary, excel_file: pd.ExcelFile) -> None:
        """Add rules from Excel sheet"""
        logger.debug("Importing rules...")
        
        try:
            df = pd.read_excel(excel_file, sheet_name="Rules", header=0)
            
            # Rules
            included_rules = set()
            rules_by_name = {}
            current_rule_name = ""
            
            for _, row in df.iterrows():
                # Handle rule name (may be empty due to merged cells)
                rule_name_val = row.iloc[ExcelConstants.RULES_NAME] if len(row) > ExcelConstants.RULES_NAME else None
                if rule_name_val and pd.notna(rule_name_val) and str(rule_name_val).strip():
                    current_rule_name = str(rule_name_val).strip()
                
                # Create rule if not already created
                if current_rule_name and current_rule_name not in included_rules:
                    rule_module = row.iloc[ExcelConstants.RULES_MODULE] if len(row) > ExcelConstants.RULES_MODULE and pd.notna(row.iloc[ExcelConstants.RULES_MODULE]) else ""
                    rule_gui = row.iloc[ExcelConstants.RULES_GUI] if len(row) > ExcelConstants.RULES_GUI and pd.notna(row.iloc[ExcelConstants.RULES_GUI]) else ""
                    rule = IRRule(
                        name=current_rule_name,
                        module=str(rule_module) if rule_module else "",
                        gui=str(rule_gui) if rule_gui else ""
                    )
                    lib.rules.append(rule)
                    rules_by_name[current_rule_name] = rule
                    included_rules.add(current_rule_name)
                
                # Add conditions
                c_name = row.iloc[ExcelConstants.RULES_CONDITION_NAME] if len(row) > ExcelConstants.RULES_CONDITION_NAME else None
                if c_name and pd.notna(c_name) and str(c_name).strip() and current_rule_name in rules_by_name:
                    c_value = row.iloc[ExcelConstants.RULES_CONDITION_VALUE] if len(row) > ExcelConstants.RULES_CONDITION_VALUE and pd.notna(row.iloc[ExcelConstants.RULES_CONDITION_VALUE]) else ""
                    c_field = row.iloc[ExcelConstants.RULES_CONDITION_FIELD] if len(row) > ExcelConstants.RULES_CONDITION_FIELD and pd.notna(row.iloc[ExcelConstants.RULES_CONDITION_FIELD]) else ""
                    condition = IRRuleCondition(
                        name=str(c_name),
                        field=str(c_field) if c_field else "",
                        value=str(c_value) if c_value else ""
                    )
                    rules_by_name[current_rule_name].conditions.append(condition)
                
                # Add actions
                a_name = row.iloc[ExcelConstants.RULES_ACTION_NAME] if len(row) > ExcelConstants.RULES_ACTION_NAME else None
                if a_name and pd.notna(a_name) and str(a_name).strip() and current_rule_name in rules_by_name:
                    a_value = row.iloc[ExcelConstants.RULES_ACTION_VALUE] if len(row) > ExcelConstants.RULES_ACTION_VALUE and pd.notna(row.iloc[ExcelConstants.RULES_ACTION_VALUE]) else ""
                    a_project = row.iloc[ExcelConstants.RULES_ACTION_PROJECT] if len(row) > ExcelConstants.RULES_ACTION_PROJECT and pd.notna(row.iloc[ExcelConstants.RULES_ACTION_PROJECT]) else ""
                    action = IRRuleAction(
                        name=str(a_name),
                        value=str(a_value) if a_value else "",
                        project=str(a_project) if a_project else ""
                    )
                    rules_by_name[current_rule_name].actions.append(action)
        except Exception as e:
            logger.warning(f"Error reading Rules sheet: {e}")
        
        logger.debug("Importing rules finished")
    
    def _add_risk_patterns_from_excel(self, lib: IRLibrary, excel_file: pd.ExcelFile) -> None:
        """Add risk patterns from Excel sheet"""
        try:
            df = pd.read_excel(excel_file, sheet_name="Risk Patterns", header=0)
            for _, row in df.iterrows():
                working_rp_ref = row.iloc[0] if len(row) > 0 and pd.notna(row.iloc[0]) else ""
                if working_rp_ref:
                    working_rp_name = row.iloc[1] if len(row) > 1 and pd.notna(row.iloc[1]) else ""
                    working_rp_desc = row.iloc[2] if len(row) > 2 and pd.notna(row.iloc[2]) else ""
                    working_rp_uuid = row.iloc[3] if len(row) > 3 and pd.notna(row.iloc[3]) else ""
                    
                    working_rp = IRRiskPattern(
                        ref=str(working_rp_ref),
                        name=str(working_rp_name) if working_rp_name else "",
                        desc=str(working_rp_desc) if working_rp_desc else "",
                        uuid=str(working_rp_uuid) if working_rp_uuid else ""
                    )
                    if working_rp_uuid:
                        lib.risk_patterns[str(working_rp_uuid)] = working_rp
        except Exception as e:
            logger.warning(f"Error reading Risk Patterns sheet: {e}")
        
        logger.info("Import risk patterns finished")
    
    def _add_usecases_from_excel(self, version: ILEVersion, excel_file: pd.ExcelFile) -> None:
        """Add use cases from Excel sheet"""
        try:
            df = pd.read_excel(excel_file, sheet_name="Use Cases", header=0)
            for _, row in df.iterrows():
                working_uc_ref = row.iloc[0] if len(row) > 0 and pd.notna(row.iloc[0]) else ""
                if working_uc_ref:
                    working_uc_name = row.iloc[1] if len(row) > 1 and pd.notna(row.iloc[1]) else ""
                    working_uc_desc = row.iloc[2] if len(row) > 2 and pd.notna(row.iloc[2]) else ""
                    working_uc_uuid = row.iloc[3] if len(row) > 3 and pd.notna(row.iloc[3]) else ""
                    
                    working_uc = IRUseCase(
                        ref=str(working_uc_ref),
                        name=str(working_uc_name) if working_uc_name else "",
                        desc=str(working_uc_desc) if working_uc_desc else ""
                    )
                    if working_uc_uuid:
                        working_uc.uuid = str(working_uc_uuid)
                        version.usecases[str(working_uc_uuid)] = working_uc
        except Exception as e:
            logger.warning(f"Error reading Use Cases sheet: {e}")
        
        logger.info("Import use cases finished")
    
    def _add_threats_from_excel(self, version: ILEVersion, excel_file: pd.ExcelFile) -> None:
        """Add threats from Excel sheet"""
        try:
            df = pd.read_excel(excel_file, sheet_name="Threats", header=0)
            for _, row in df.iterrows():
                working_t_ref = row.iloc[0] if len(row) > 0 and pd.notna(row.iloc[0]) else ""
                if working_t_ref:
                    working_t_name = row.iloc[1] if len(row) > 1 and pd.notna(row.iloc[1]) else ""
                    working_t_desc = row.iloc[2] if len(row) > 2 and pd.notna(row.iloc[2]) else ""
                    working_t_conf = row.iloc[3] if len(row) > 3 and pd.notna(row.iloc[3]) else ""
                    working_t_int = row.iloc[4] if len(row) > 4 and pd.notna(row.iloc[4]) else ""
                    working_t_av = row.iloc[5] if len(row) > 5 and pd.notna(row.iloc[5]) else ""
                    working_t_ee = row.iloc[6] if len(row) > 6 and pd.notna(row.iloc[6]) else ""
                    refs_str = row.iloc[7] if len(row) > 7 and pd.notna(row.iloc[7]) else ""
                    mitre_str = row.iloc[8] if len(row) > 8 and pd.notna(row.iloc[8]) else ""
                    stride_str = row.iloc[9] if len(row) > 9 and pd.notna(row.iloc[9]) else ""
                    working_t_uuid = row.iloc[10] if len(row) > 10 and pd.notna(row.iloc[10]) else ""
                    
                    working_th = IRThreat(
                        ref=str(working_t_ref),
                        name=str(working_t_name) if working_t_name else "",
                        desc=str(working_t_desc) if working_t_desc else ""
                    )
                    if working_t_uuid:
                        working_th.uuid = str(working_t_uuid)
                    
                    # Add references
                    if refs_str:
                        refs = [ref.strip() for ref in str(refs_str).split(ExcelConstants.SEPARATOR) if ref.strip()]
                        for ref in refs:
                            ref_parts = ref.split(":", 1)
                            if len(ref_parts) == 2:
                                ref_name, ref_url = ref_parts
                                for reference in version.references.values():
                                    if reference.name == ref_name and reference.url == ref_url:
                                        ref_key = str(uuid.uuid4())
                                        working_th.references[ref_key] = reference.uuid
                                        break
                    
                    working_th.risk_rating = IRRiskRating(
                        confidentiality=str(working_t_conf) if working_t_conf else "",
                        integrity=str(working_t_int) if working_t_int else "",
                        availability=str(working_t_av) if working_t_av else "",
                        ease_of_exploitation=str(working_t_ee) if working_t_ee else ""
                    )
                    
                    # Import mitre if present
                    if mitre_str:
                        mitre_items = [item.strip() for item in str(mitre_str).split(ExcelConstants.SEPARATOR) if item.strip()]
                        working_th.mitre = mitre_items
                    
                    # Import stride if present
                    if stride_str:
                        stride_items = [item.strip() for item in str(stride_str).split(ExcelConstants.SEPARATOR) if item.strip()]
                        working_th.stride = stride_items
                    
                    if working_t_uuid:
                        version.threats[str(working_t_uuid)] = working_th
        except Exception as e:
            logger.warning(f"Error reading Threats sheet: {e}")
        
        logger.info("Import threats finished")
    
    def _add_weaknesses_from_excel(self, version: ILEVersion, excel_file: pd.ExcelFile) -> None:
        """Add weaknesses from Excel sheet"""
        try:
            df = pd.read_excel(excel_file, sheet_name="Weaknesses", header=0)
            for _, row in df.iterrows():
                working_w_ref = row.iloc[0] if len(row) > 0 and pd.notna(row.iloc[0]) else ""
                if working_w_ref:
                    working_w_name = row.iloc[1] if len(row) > 1 and pd.notna(row.iloc[1]) else ""
                    working_w_desc = row.iloc[2] if len(row) > 2 and pd.notna(row.iloc[2]) else ""
                    working_w_impact = row.iloc[3] if len(row) > 3 and pd.notna(row.iloc[3]) else ""
                    working_w_test_steps = row.iloc[4] if len(row) > 4 and pd.notna(row.iloc[4]) else ""
                    refs_str = row.iloc[5] if len(row) > 5 and pd.notna(row.iloc[5]) else ""
                    working_w_uuid = row.iloc[6] if len(row) > 6 and pd.notna(row.iloc[6]) else ""
                    
                    working_w = IRWeakness(
                        ref=str(working_w_ref),
                        name=str(working_w_name) if working_w_name else "",
                        desc=str(working_w_desc) if working_w_desc else ""
                    )
                    if working_w_uuid:
                        working_w.uuid = str(working_w_uuid)
                    if working_w_impact:
                        working_w.impact = str(working_w_impact)
                    
                    test = IRTest(steps=str(working_w_test_steps) if working_w_test_steps else "")
                    
                    # Add test references
                    if refs_str:
                        refs = [ref.strip() for ref in str(refs_str).split(ExcelConstants.SEPARATOR) if ref.strip()]
                        for ref in refs:
                            ref_parts = ref.split(":", 1)
                            if len(ref_parts) == 2:
                                ref_name, ref_url = ref_parts
                                for reference in version.references.values():
                                    if reference.name == ref_name and reference.url == ref_url:
                                        ref_key = str(uuid.uuid4())
                                        test.references[ref_key] = reference.uuid
                                        break
                    
                    working_w.test = test
                    if working_w_uuid:
                        version.weaknesses[str(working_w_uuid)] = working_w
        except Exception as e:
            logger.warning(f"Error reading Weaknesses sheet: {e}")
        
        logger.info("Import weaknesses finished")
    
    def _add_controls_from_excel(self, version: ILEVersion, excel_file: pd.ExcelFile) -> None:
        """Add controls from Excel sheet"""
        try:
            df = pd.read_excel(excel_file, sheet_name="Controls", header=0)
            for _, row in df.iterrows():
                working_c_ref = row.iloc[0] if len(row) > 0 and pd.notna(row.iloc[0]) else ""
                if working_c_ref:
                    working_c_name = row.iloc[1] if len(row) > 1 and pd.notna(row.iloc[1]) else ""
                    working_c_desc = row.iloc[2] if len(row) > 2 and pd.notna(row.iloc[2]) else ""
                    working_c_state = row.iloc[3] if len(row) > 3 and pd.notna(row.iloc[3]) else ""
                    working_c_cost = row.iloc[4] if len(row) > 4 and pd.notna(row.iloc[4]) else ""
                    refs_str = row.iloc[5] if len(row) > 5 and pd.notna(row.iloc[5]) else ""
                    test_steps = row.iloc[6] if len(row) > 6 and pd.notna(row.iloc[6]) else ""
                    test_refs_str = row.iloc[7] if len(row) > 7 and pd.notna(row.iloc[7]) else ""
                    standards_str = row.iloc[8] if len(row) > 8 and pd.notna(row.iloc[8]) else ""
                    implementations_str = row.iloc[9] if len(row) > 9 and pd.notna(row.iloc[9]) else ""
                    base_standard_str = row.iloc[10] if len(row) > 10 and pd.notna(row.iloc[10]) else ""
                    base_standard_section_str = row.iloc[11] if len(row) > 11 and pd.notna(row.iloc[11]) else ""
                    scope_str = row.iloc[12] if len(row) > 12 and pd.notna(row.iloc[12]) else ""
                    mitre_str = row.iloc[13] if len(row) > 13 and pd.notna(row.iloc[13]) else ""
                    working_c_uuid = row.iloc[14] if len(row) > 14 and pd.notna(row.iloc[14]) else ""
                    
                    working_c = IRControl(
                        ref=str(working_c_ref),
                        name=str(working_c_name) if working_c_name else "",
                        desc=str(working_c_desc) if working_c_desc else "",
                        state=str(working_c_state) if working_c_state else "",
                        cost=str(working_c_cost) if working_c_cost else ""
                    )
                    if working_c_uuid:
                        working_c.uuid = str(working_c_uuid)
                    
                    # Add references
                    if refs_str:
                        refs = [ref.strip() for ref in str(refs_str).split(ExcelConstants.SEPARATOR) if ref.strip()]
                        for ref in refs:
                            ref_parts = ref.split(":", 1)
                            if len(ref_parts) == 2:
                                ref_name, ref_url = ref_parts
                                for reference in version.references.values():
                                    if reference.name == ref_name and reference.url == ref_url:
                                        ref_key = str(uuid.uuid4())
                                        working_c.references[ref_key] = reference.uuid
                                        break
                    
                    test = IRTest(steps=str(test_steps) if test_steps else "")
                    
                    # Add test references
                    if test_refs_str:
                        test_refs = [ref.strip() for ref in str(test_refs_str).split(ExcelConstants.SEPARATOR) if ref.strip()]
                        for ref in test_refs:
                            ref_parts = ref.split(":", 1)
                            if len(ref_parts) == 2:
                                ref_name, ref_url = ref_parts
                                for reference in version.references.values():
                                    if reference.name == ref_name and reference.url == ref_url:
                                        ref_key = str(uuid.uuid4())
                                        test.references[ref_key] = reference.uuid
                                        break
                    
                    working_c.test = test
                    
                    # Add standards
                    if standards_str:
                        standards = [std.strip() for std in str(standards_str).split(ExcelConstants.SEPARATOR) if std.strip()]
                        for standard in standards:
                            standard_parts = standard.split(":", 1)
                            if len(standard_parts) == 2:
                                supported_standard_ref, standard_ref = standard_parts
                                for standard_obj in version.standards.values():
                                    if (standard_obj.supported_standard_ref == supported_standard_ref and 
                                        standard_obj.standard_ref == standard_ref):
                                        standard_key = str(uuid.uuid4())
                                        working_c.standards[standard_key] = standard_obj.uuid
                                        break
                    
                    # Add implementations
                    if implementations_str:
                        implementations = [imp.strip() for imp in str(implementations_str).split(ExcelConstants.SEPARATOR) if imp.strip()]
                        working_c.implementations = implementations
                    
                    # Import baseStandard if present
                    if base_standard_str:
                        base_standard_items = [item.strip() for item in str(base_standard_str).split(ExcelConstants.SEPARATOR) if item.strip()]
                        working_c.base_standard = base_standard_items
                    
                    # Import baseStandardSection if present
                    if base_standard_section_str:
                        base_standard_section_items = [item.strip() for item in str(base_standard_section_str).split(ExcelConstants.SEPARATOR) if item.strip()]
                        working_c.base_standard_section = base_standard_section_items
                    
                    # Import scope if present
                    if scope_str:
                        scope_items = [item.strip() for item in str(scope_str).split(ExcelConstants.SEPARATOR) if item.strip()]
                        working_c.scope = scope_items
                    
                    # Import mitre if present
                    if mitre_str:
                        mitre_items = [item.strip() for item in str(mitre_str).split(ExcelConstants.SEPARATOR) if item.strip()]
                        working_c.mitre = mitre_items
                    
                    if working_c_uuid:
                        version.controls[str(working_c_uuid)] = working_c
        except Exception as e:
            logger.warning(f"Error reading Controls sheet: {e}")
        
        logger.info("Import controls finished")
    
    def _add_references_from_excel(self, version: ILEVersion, excel_file: pd.ExcelFile) -> None:
        """Add references from Excel sheet"""
        try:
            df = pd.read_excel(excel_file, sheet_name="References", header=0)
            for _, row in df.iterrows():
                name = row.iloc[0] if len(row) > 0 and pd.notna(row.iloc[0]) else ""
                url = row.iloc[1] if len(row) > 1 and pd.notna(row.iloc[1]) else ""
                uuid_val = row.iloc[2] if len(row) > 2 and pd.notna(row.iloc[2]) else ""
                
                if name and url:
                    reference = IRReference(name=str(name), url=str(url))
                    if uuid_val:
                        reference.uuid = str(uuid_val)
                        version.references[str(uuid_val)] = reference
        except Exception as e:
            logger.warning(f"Error reading References sheet: {e}")
        
        logger.info("Import references finished")
    
    def _add_relations_from_excel(self, lib: IRLibrary, excel_file: pd.ExcelFile) -> None:
        """Add relations from Excel sheet"""
        try:
            df = pd.read_excel(excel_file, sheet_name="Relations", header=0)
            for _, row in df.iterrows():
                rp = row.iloc[0] if len(row) > 0 and pd.notna(row.iloc[0]) else ""
                uc = row.iloc[1] if len(row) > 1 and pd.notna(row.iloc[1]) else ""
                t = row.iloc[2] if len(row) > 2 and pd.notna(row.iloc[2]) else ""
                w = row.iloc[3] if len(row) > 3 and pd.notna(row.iloc[3]) else ""
                c = row.iloc[4] if len(row) > 4 and pd.notna(row.iloc[4]) else ""
                m = row.iloc[5] if len(row) > 5 and pd.notna(row.iloc[5]) else ""
                
                if rp:  # At least risk pattern should be present
                    rel = IRRelation(
                        risk_pattern_uuid=str(rp),
                        usecase_uuid=str(uc) if uc else "",
                        threat_uuid=str(t) if t else "",
                        weakness_uuid=str(w) if w else "",
                        control_uuid=str(c) if c else "",
                        mitigation=str(m) if m else ""
                    )
                    lib.relations[rel.uuid] = rel
        except Exception as e:
            logger.warning(f"Error reading Relations sheet: {e}")
        
        logger.info("Import relations finished")
