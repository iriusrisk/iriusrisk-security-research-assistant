"""
XLSX export service for IriusRisk Library Editor API
"""

import logging
from typing import List
from pathlib import Path

import pandas as pd
import xlsxwriter
from xlsxwriter.utility import xl_col_to_name

from isra.src.ile.backend.app.configuration import ExcelConstants
from isra.src.ile.backend.app.models import (
    ILEVersion, IRLibrary
)
from isra.src.ile.backend.app.services.data_service import DataService

logger = logging.getLogger(__name__)


class XLSXExportService:
    """Service for exporting libraries to XLSX format"""
    
    def __init__(self):
        self.data_service = DataService()
    
    def export_library_xlsx(self, lib: IRLibrary, version: ILEVersion, version_path: str) -> None:
        """Export library to XLSX file"""
        xlsx_file_path = Path(version_path) / lib.filename.replace("xml", "xlsx")
        
        try:
            # Create ExcelWriter with xlsxwriter engine
            with pd.ExcelWriter(xlsx_file_path, engine='xlsxwriter') as writer:
                workbook = writer.book
                
                # Create sheet content - each method creates DataFrame and writes it
                # Then applies styling using xlsxwriter
                self._create_risk_patterns_sheet(writer, workbook, lib)
                self._create_rules_sheet(writer, workbook, lib)
                self._create_library_properties_sheet(writer, workbook, lib)
                self._create_relations_sheet(writer, workbook, lib)
                self._create_references_sheet(writer, workbook, lib, version)
                self._create_usecases_sheet(writer, workbook, lib, version)
                self._create_threats_sheet(writer, workbook, lib, version)
                self._create_weaknesses_sheet(writer, workbook, lib, version)
                self._create_controls_sheet(writer, workbook, lib, version)
                self._create_components_sheet(writer, workbook, lib, version)
                self._create_standards_sheet(writer, workbook, lib, version)
                self._create_supported_standards_sheet(writer, workbook, lib, version)
            
            logger.info(f"Export process finished: {xlsx_file_path}")
            
        except Exception as e:
            logger.error(f"Exception while saving {lib.ref} to XLSX: {e}")
            raise RuntimeError(f"Failed to export library to XLSX: {e}") from e
    
    def _create_format(self, workbook: xlsxwriter.Workbook, color: str, header: bool = False) -> xlsxwriter.format.Format:
        """Create xlsxwriter format with color and styling"""
        format_dict = {
            'bg_color': f"#{color}",
            'border': 1,
            'border_color': '#FFFFFF',
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': not header,
        }
        if header:
            format_dict['bold'] = True
            format_dict['font_color'] = '#FFFFFF'
        else:
            format_dict['font_color'] = '#000000'
        
        return workbook.add_format(format_dict)
    
    def _apply_column_widths(self, worksheet: xlsxwriter.worksheet.Worksheet, num_cols: int, width: float = 30.0) -> None:
        """Apply column widths to worksheet"""
        for i in range(num_cols):
            worksheet.set_column(i, i, width)
    
    def _apply_row_heights(self, worksheet: xlsxwriter.worksheet.Worksheet, num_rows: int, height: float = 15.0) -> None:
        """Apply row heights to worksheet"""
        for i in range(num_rows):
            worksheet.set_row(i, height)
    
    def _create_references_sheet(self, writer: pd.ExcelWriter, workbook: xlsxwriter.Workbook, lib: IRLibrary, version: ILEVersion) -> None:
        """Create references sheet"""
        # Create DataFrame
        data = []
        for reference in version.references.values():
            data.append({
                'Name': reference.name,
                'URL': reference.url,
                'UUID': reference.uuid
            })
        
        df = pd.DataFrame(data)
        df.to_excel(writer, sheet_name='References', index=False, header=True)
        
        # Apply styling
        worksheet = writer.sheets['References']
        header_format = self._create_format(workbook, ExcelConstants.RISK_PATTERN_HEADER, header=True)
        
        # Format header row
        for col_num in range(len(df.columns)):
            worksheet.write(0, col_num, df.columns[col_num], header_format)
        
        # Format data rows with alternating colors
        for row_num in range(1, len(df) + 1):
            color = ExcelConstants.RISK_PATTERN_COLOR_1 if row_num % 2 == 1 else ExcelConstants.RISK_PATTERN_COLOR_2
            row_format = self._create_format(workbook, color, header=False)
            for col_num in range(len(df.columns)):
                worksheet.write(row_num, col_num, df.iloc[row_num - 1, col_num], row_format)
        
        # Set column widths
        worksheet.set_column(0, 0, 100.0)
        worksheet.set_column(1, 1, 100.0)
        worksheet.set_column(2, 2, 30.0)
    
    def _create_risk_patterns_sheet(self, writer: pd.ExcelWriter, workbook: xlsxwriter.Workbook, lib: IRLibrary) -> None:
        """Create risk patterns sheet"""
        # Create DataFrame
        data = []
        for rp in lib.risk_patterns.values():
            data.append({
                'Ref': rp.ref,
                'Name': rp.name,
                'Desc': rp.desc,
                'UUID': rp.uuid
            })
        
        df = pd.DataFrame(data)
        df.to_excel(writer, sheet_name='Risk Patterns', index=False, header=True)
        
        # Apply styling
        worksheet = writer.sheets['Risk Patterns']
        header_format = self._create_format(workbook, ExcelConstants.RISK_PATTERN_HEADER, header=True)
        
        # Format header row
        for col_num in range(len(df.columns)):
            worksheet.write(0, col_num, df.columns[col_num], header_format)
        
        # Format data rows with alternating colors
        for row_num in range(1, len(df) + 1):
            color = ExcelConstants.RISK_PATTERN_COLOR_1 if row_num % 2 == 1 else ExcelConstants.RISK_PATTERN_COLOR_2
            row_format = self._create_format(workbook, color, header=False)
            for col_num in range(len(df.columns)):
                worksheet.write(row_num, col_num, df.iloc[row_num - 1, col_num], row_format)
        
        self._adjust_height_and_width(worksheet, len(df) + 1, ExcelConstants.RISK_PATTERNS_LAST_HEADER)
    
    def _create_usecases_sheet(self, writer: pd.ExcelWriter, workbook: xlsxwriter.Workbook, lib: IRLibrary, version: ILEVersion) -> None:
        """Create use cases sheet"""
        # Create DataFrame
        data = []
        usecases = self._get_list_from_relations(lib, "usecases")
        
        for uc_ref in usecases:
            usecase = version.usecases.get(uc_ref)
            if usecase:
                data.append({
                    'Ref': usecase.ref,
                    'Name': usecase.name,
                    'Desc': usecase.desc,
                    'UUID': usecase.uuid
                })
        
        df = pd.DataFrame(data)
        df.to_excel(writer, sheet_name='Use Cases', index=False, header=True)
        
        # Apply styling
        worksheet = writer.sheets['Use Cases']
        header_format = self._create_format(workbook, ExcelConstants.USE_CASE_HEADER, header=True)
        
        # Format header row
        for col_num in range(len(df.columns)):
            worksheet.write(0, col_num, df.columns[col_num], header_format)
        
        # Format data rows with alternating colors
        for row_num in range(1, len(df) + 1):
            color = ExcelConstants.USE_CASE_COLOR_1 if row_num % 2 == 1 else ExcelConstants.USE_CASE_COLOR_2
            row_format = self._create_format(workbook, color, header=False)
            for col_num in range(len(df.columns)):
                worksheet.write(row_num, col_num, df.iloc[row_num - 1, col_num], row_format)
        
        self._adjust_height_and_width(worksheet, len(df) + 1, ExcelConstants.RISK_PATTERNS_LAST_HEADER)
    
    def _create_threats_sheet(self, writer: pd.ExcelWriter, workbook: xlsxwriter.Workbook, lib: IRLibrary, version: ILEVersion) -> None:
        """Create threats sheet"""
        # Create DataFrame
        data = []
        threats = self._get_list_from_relations(lib, "threats")
        
        for threat_ref in threats:
            threat = version.threats.get(threat_ref)
            if threat:
                # Format references
                threat_references = [f"{key}:{value}" for key, value in threat.references.items()]
                refs = ExcelConstants.SEPARATOR.join(threat_references)
                
                data.append({
                    'Ref': threat.ref,
                    'Name': threat.name,
                    'Desc': threat.desc,
                    'Confidentiality': threat.risk_rating.confidentiality if threat.risk_rating else "",
                    'Integrity': threat.risk_rating.integrity if threat.risk_rating else "",
                    'Availability': threat.risk_rating.availability if threat.risk_rating else "",
                    'Ease Of Exploitation': threat.risk_rating.ease_of_exploitation if threat.risk_rating else "",
                    'References': refs,
                    'Mitre': ExcelConstants.SEPARATOR.join(threat.mitre or []),
                    'STRIDE': ExcelConstants.SEPARATOR.join(threat.stride or []),
                    'UUID': threat.uuid
                })
        
        df = pd.DataFrame(data)
        df.to_excel(writer, sheet_name='Threats', index=False, header=True)
        
        # Apply styling
        worksheet = writer.sheets['Threats']
        header_format = self._create_format(workbook, ExcelConstants.THREAT_HEADER, header=True)
        
        # Format header row
        for col_num in range(len(df.columns)):
            worksheet.write(0, col_num, df.columns[col_num], header_format)
        
        # Format data rows with alternating colors
        for row_num in range(1, len(df) + 1):
            color = ExcelConstants.THREAT_COLOR_1 if row_num % 2 == 1 else ExcelConstants.THREAT_COLOR_2
            row_format = self._create_format(workbook, color, header=False)
            for col_num in range(len(df.columns)):
                worksheet.write(row_num, col_num, df.iloc[row_num - 1, col_num], row_format)
        
        self._adjust_height_and_width(worksheet, len(df) + 1, ExcelConstants.RISK_PATTERNS_LAST_HEADER)
    
    def _create_weaknesses_sheet(self, writer: pd.ExcelWriter, workbook: xlsxwriter.Workbook, lib: IRLibrary, version: ILEVersion) -> None:
        """Create weaknesses sheet"""
        # Create DataFrame
        data = []
        weaknesses = self._get_list_from_relations(lib, "weaknesses")
        
        for weakness_ref in weaknesses:
            weakness = version.weaknesses.get(weakness_ref)
            if weakness:
                # Format test references
                test_references = [f"{key}:{value}" for key, value in weakness.test.references.items()]
                t_refs = ExcelConstants.SEPARATOR.join(test_references)
                
                data.append({
                    'Ref': weakness.ref,
                    'Name': weakness.name,
                    'Desc': weakness.desc,
                    'Impact': weakness.impact,
                    'Test Steps': weakness.test.steps,
                    'Test References': t_refs,
                    'UUID': weakness.uuid
                })
        
        df = pd.DataFrame(data)
        df.to_excel(writer, sheet_name='Weaknesses', index=False, header=True)
        
        # Apply styling
        worksheet = writer.sheets['Weaknesses']
        header_format = self._create_format(workbook, ExcelConstants.WEAKNESS_HEADER, header=True)
        
        # Format header row
        for col_num in range(len(df.columns)):
            worksheet.write(0, col_num, df.columns[col_num], header_format)
        
        # Format data rows with alternating colors
        for row_num in range(1, len(df) + 1):
            color = ExcelConstants.WEAKNESS_COLOR_1 if row_num % 2 == 1 else ExcelConstants.WEAKNESS_COLOR_2
            row_format = self._create_format(workbook, color, header=False)
            for col_num in range(len(df.columns)):
                worksheet.write(row_num, col_num, df.iloc[row_num - 1, col_num], row_format)
        
        self._adjust_height_and_width(worksheet, len(df) + 1, ExcelConstants.RISK_PATTERNS_LAST_HEADER)
    
    def _create_controls_sheet(self, writer: pd.ExcelWriter, workbook: xlsxwriter.Workbook, lib: IRLibrary, version: ILEVersion) -> None:
        """Create controls sheet"""
        # Create DataFrame
        data = []
        controls = self._get_list_from_relations(lib, "controls")
        
        for control_ref in controls:
            control = version.controls.get(control_ref)
            if control:
                # Format references
                control_references = [f"{key}:{value}" for key, value in control.references.items()]
                refs = ExcelConstants.SEPARATOR.join(control_references)
                
                # Format test references
                test_references = [f"{key}:{value}" for key, value in control.test.references.items()]
                t_refs = ExcelConstants.SEPARATOR.join(test_references)
                
                # Format standards
                standard_list = [f"{key}:{value}" for key, value in control.standards.items()]
                sts = ExcelConstants.SEPARATOR.join(standard_list)
                
                # Format implementations
                impl = ExcelConstants.SEPARATOR.join(control.implementations)
                
                data.append({
                    'Ref': control.ref,
                    'Name': control.name,
                    'Desc': control.desc,
                    'State': control.state,
                    'Cost': control.cost,
                    'References': refs,
                    'Test Steps': control.test.steps,
                    'Test References': t_refs,
                    'Standards': sts,
                    'Implementations': impl,
                    'Base Standard': ExcelConstants.SEPARATOR.join(control.base_standard or []),
                    'Base Standard Section': ExcelConstants.SEPARATOR.join(control.base_standard_section or []),
                    'Scope': ExcelConstants.SEPARATOR.join(control.scope or []),
                    'MITRE': ExcelConstants.SEPARATOR.join(control.mitre or []),
                    'UUID': control.uuid
                })
        
        df = pd.DataFrame(data)
        df.to_excel(writer, sheet_name='Controls', index=False, header=True)
        
        # Apply styling
        worksheet = writer.sheets['Controls']
        header_format = self._create_format(workbook, ExcelConstants.COUNTERMEASURE_HEADER, header=True)
        
        # Format header row
        for col_num in range(len(df.columns)):
            worksheet.write(0, col_num, df.columns[col_num], header_format)
        
        # Format data rows with alternating colors
        for row_num in range(1, len(df) + 1):
            color = ExcelConstants.COUNTERMEASURE_COLOR_1 if row_num % 2 == 1 else ExcelConstants.COUNTERMEASURE_COLOR_2
            row_format = self._create_format(workbook, color, header=False)
            for col_num in range(len(df.columns)):
                worksheet.write(row_num, col_num, df.iloc[row_num - 1, col_num], row_format)
        
        self._adjust_height_and_width(worksheet, len(df) + 1, ExcelConstants.RISK_PATTERNS_LAST_HEADER)
    
    def _create_relations_sheet(self, writer: pd.ExcelWriter, workbook: xlsxwriter.Workbook, lib: IRLibrary) -> None:
        """Create relations sheet"""
        # Create DataFrame
        data = []
        for rel in lib.relations.values():
            data.append({
                'Risk Pattern': rel.risk_pattern_uuid,
                'Use Case': rel.usecase_uuid,
                'Threat': rel.threat_uuid,
                'Weakness': rel.weakness_uuid,
                'Control': rel.control_uuid,
                'Mitigation': rel.mitigation
            })
        
        df = pd.DataFrame(data)
        df.to_excel(writer, sheet_name='Relations', index=False, header=True)
        
        # Apply styling
        worksheet = writer.sheets['Relations']
        header_format = self._create_format(workbook, ExcelConstants.RISK_PATTERN_HEADER, header=True)
        
        # Format header row
        for col_num in range(len(df.columns)):
            worksheet.write(0, col_num, df.columns[col_num], header_format)
        
        # Format data rows with alternating colors
        for row_num in range(1, len(df) + 1):
            color = ExcelConstants.RISK_PATTERN_COLOR_1 if row_num % 2 == 1 else ExcelConstants.RISK_PATTERN_COLOR_2
            row_format = self._create_format(workbook, color, header=False)
            for col_num in range(len(df.columns)):
                worksheet.write(row_num, col_num, df.iloc[row_num - 1, col_num], row_format)
        
        self._adjust_height_and_width(worksheet, len(df) + 1, ExcelConstants.RISK_PATTERNS_LAST_HEADER)
    
    def _create_rules_sheet(self, writer: pd.ExcelWriter, workbook: xlsxwriter.Workbook, lib: IRLibrary) -> None:
        """Create rules sheet"""
        # Build rows for rules - each rule may span multiple rows due to conditions/actions
        headers = ["Rule Name", "Module", "Generated by GUI", "Condition Name", "Condition Value", 
                  "Condition Field", "Action Name", "Action Value", "Action Project"]
        
        # Create empty DataFrame to initialize sheet
        df = pd.DataFrame(columns=headers)
        df.to_excel(writer, sheet_name='Rules', index=False, header=True)
        
        worksheet = writer.sheets['Rules']
        
        # Format headers
        header_formats = {
            'Rule Name': self._create_format(workbook, ExcelConstants.RULE_HEADER, header=True),
            'Module': self._create_format(workbook, ExcelConstants.RULE_HEADER, header=True),
            'Generated by GUI': self._create_format(workbook, ExcelConstants.RULE_HEADER, header=True),
            'Condition Name': self._create_format(workbook, ExcelConstants.RULE_CONDITION_HEADER, header=True),
            'Condition Value': self._create_format(workbook, ExcelConstants.RULE_CONDITION_HEADER, header=True),
            'Condition Field': self._create_format(workbook, ExcelConstants.RULE_CONDITION_HEADER, header=True),
            'Action Name': self._create_format(workbook, ExcelConstants.RULE_ACTION_HEADER, header=True),
            'Action Value': self._create_format(workbook, ExcelConstants.RULE_ACTION_HEADER, header=True),
            'Action Project': self._create_format(workbook, ExcelConstants.RULE_ACTION_HEADER, header=True)
        }
        
        # Write headers
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header, header_formats[header])
        
        # Rules data
        working_row = 1
        rule_color = True
        condition_color = True
        action_color = True
        
        for rule in lib.rules:
            rule_start_row = working_row
            r_color = ExcelConstants.RULE_COLOR_1 if rule_color else ExcelConstants.RULE_COLOR_2
            rule_format = self._create_format(workbook, r_color, header=False)
            
            # Count max rows needed
            max_rows = max(len(rule.conditions), len(rule.actions), 1)
            rule_end_row = rule_start_row + max_rows - 1
            
            # Write rule name, module, GUI (will be merged later)
            worksheet.write(working_row, 0, rule.name, rule_format)
            worksheet.write(working_row, 1, rule.module, rule_format)
            worksheet.write(working_row, 2, rule.gui, rule_format)
            
            # Write conditions
            cond_row = rule_start_row
            for cond in rule.conditions:
                c_color = ExcelConstants.RULE_CONDITION_COLOR_1 if condition_color else ExcelConstants.RULE_CONDITION_COLOR_2
                cond_format = self._create_format(workbook, c_color, header=False)
                worksheet.write(cond_row, 3, cond.name, cond_format)
                worksheet.write(cond_row, 4, cond.value, cond_format)
                worksheet.write(cond_row, 5, cond.field, cond_format)
                condition_color = not condition_color
                cond_row += 1
            
            # Write actions
            act_row = rule_start_row
            for act in rule.actions:
                a_color = ExcelConstants.RULE_ACTION_COLOR_1 if action_color else ExcelConstants.RULE_ACTION_COLOR_2
                act_format = self._create_format(workbook, a_color, header=False)
                worksheet.write(act_row, 6, act.name, act_format)
                worksheet.write(act_row, 7, act.value, act_format)
                worksheet.write(act_row, 8, act.project, act_format)
                action_color = not action_color
                act_row += 1
            
            # Merge cells for rule name, module, and GUI if needed
            if max_rows > 1:
                worksheet.merge_range(rule_start_row, 0, rule_end_row, 0, rule.name, rule_format)
                worksheet.merge_range(rule_start_row, 1, rule_end_row, 1, rule.module, rule_format)
                worksheet.merge_range(rule_start_row, 2, rule_end_row, 2, rule.gui, rule_format)
            
            working_row = rule_end_row + 1
            rule_color = not rule_color
        
        self._adjust_height_and_width(worksheet, working_row, ExcelConstants.RULES_LAST_HEADER)
    
    def _create_library_properties_sheet(self, writer: pd.ExcelWriter, workbook: xlsxwriter.Workbook, lib: IRLibrary) -> None:
        """Create library properties sheet"""
        # Create DataFrame
        data = [
            {'General': 'Library Name', 'Values': lib.name},
            {'General': 'Library Ref', 'Values': lib.ref},
            {'General': 'Library Desc', 'Values': lib.desc},
            {'General': 'Revision', 'Values': lib.revision},
            {'General': 'Enabled', 'Values': lib.enabled}
        ]
        
        df = pd.DataFrame(data)
        df.to_excel(writer, sheet_name='Library properties', index=False, header=True)
        
        # Apply styling
        worksheet = writer.sheets['Library properties']
        header_format = self._create_format(workbook, ExcelConstants.LIBRARY_PROPERTY_HEADER, header=True)
        
        # Format header row
        for col_num in range(len(df.columns)):
            worksheet.write(0, col_num, df.columns[col_num], header_format)
        
        # Format data rows with alternating colors
        for row_num in range(1, len(df) + 1):
            color = ExcelConstants.LIBRARY_PROPERTY_COLOR_1 if row_num % 2 == 0 else ExcelConstants.LIBRARY_PROPERTY_COLOR_2
            row_format = self._create_format(workbook, color, header=False)
            for col_num in range(len(df.columns)):
                worksheet.write(row_num, col_num, df.iloc[row_num - 1, col_num], row_format)
        
        self._adjust_height_and_width(worksheet, 7, ExcelConstants.RISK_PATTERNS_LAST_HEADER)
    
    def _create_components_sheet(self, writer: pd.ExcelWriter, workbook: xlsxwriter.Workbook, lib: IRLibrary, version: ILEVersion) -> None:
        """Create components sheet"""
        # Create DataFrame
        data = []
        categories_by_ref = {cat.ref: cat for cat in version.categories.values()}
        
        for cd in lib.component_definitions.values():
            category = categories_by_ref.get(cd.category_ref)
            
            data.append({
                'Component Definition Name': cd.name,
                'Component Definition Ref': cd.ref,
                'Component Definition Desc': cd.desc,
                'Category Name': category.name if category else "",
                'Category Ref': cd.category_ref,
                'Category UUID': category.uuid if category else "",
                'Risk Patterns': ",".join(cd.risk_pattern_refs),
                'Visible': cd.visible,
                'Component UUID': cd.uuid
            })
        
        df = pd.DataFrame(data)
        df.to_excel(writer, sheet_name='Components', index=False, header=True)
        
        # Apply styling
        worksheet = writer.sheets['Components']
        header_format = self._create_format(workbook, ExcelConstants.LIBRARY_COMPONENT_HEADER, header=True)
        
        # Format header row
        for col_num in range(len(df.columns)):
            worksheet.write(0, col_num, df.columns[col_num], header_format)
        
        # Format data rows with alternating colors
        for row_num in range(1, len(df) + 1):
            color = ExcelConstants.LIBRARY_COMPONENT_COLOR_1 if row_num % 2 == 1 else ExcelConstants.LIBRARY_COMPONENT_COLOR_2
            row_format = self._create_format(workbook, color, header=False)
            for col_num in range(len(df.columns)):
                worksheet.write(row_num, col_num, df.iloc[row_num - 1, col_num], row_format)
        
        self._adjust_height_and_width(worksheet, len(df) + 1, ExcelConstants.RISK_PATTERNS_LAST_HEADER)
    
    def _create_standards_sheet(self, writer: pd.ExcelWriter, workbook: xlsxwriter.Workbook, lib: IRLibrary, version: ILEVersion) -> None:
        """Create standards sheet"""
        # Create DataFrame
        data = []
        for standard in version.standards.values():
            data.append({
                'Supported Standard Ref': standard.supported_standard_ref,
                'Standard Ref': standard.standard_ref,
                'Standard UUID': standard.uuid
            })
        
        df = pd.DataFrame(data)
        df.to_excel(writer, sheet_name='Standards', index=False, header=True)
        
        # Apply styling
        worksheet = writer.sheets['Standards']
        header_format = self._create_format(workbook, ExcelConstants.LIBRARY_STANDARD_HEADER, header=True)
        
        # Format header row
        for col_num in range(len(df.columns)):
            worksheet.write(0, col_num, df.columns[col_num], header_format)
        
        # Format data rows with alternating colors
        for row_num in range(1, len(df) + 1):
            color = ExcelConstants.LIBRARY_STANDARD_COLOR_1 if row_num % 2 == 1 else ExcelConstants.LIBRARY_STANDARD_COLOR_2
            row_format = self._create_format(workbook, color, header=False)
            for col_num in range(len(df.columns)):
                worksheet.write(row_num, col_num, df.iloc[row_num - 1, col_num], row_format)
        
        self._adjust_height_and_width(worksheet, len(df) + 1, ExcelConstants.RISK_PATTERNS_LAST_HEADER)
    
    def _create_supported_standards_sheet(self, writer: pd.ExcelWriter, workbook: xlsxwriter.Workbook, lib: IRLibrary, version: ILEVersion) -> None:
        """Create supported standards sheet"""
        # Create DataFrame
        data = []
        for supported_standard in version.supported_standards.values():
            data.append({
                'Supported Standard Name': supported_standard.supported_standard_name,
                'Supported Standard Ref': supported_standard.supported_standard_ref,
                'Supported Standard UUID': supported_standard.uuid
            })
        
        df = pd.DataFrame(data)
        df.to_excel(writer, sheet_name='Supported standards', index=False, header=True)
        
        # Apply styling
        worksheet = writer.sheets['Supported standards']
        header_format = self._create_format(workbook, ExcelConstants.LIBRARY_STANDARD_HEADER, header=True)
        
        # Format header row
        for col_num in range(len(df.columns)):
            worksheet.write(0, col_num, df.columns[col_num], header_format)
        
        # Format data rows with alternating colors
        for row_num in range(1, len(df) + 1):
            color = ExcelConstants.LIBRARY_STANDARD_COLOR_1 if row_num % 2 == 1 else ExcelConstants.LIBRARY_STANDARD_COLOR_2
            row_format = self._create_format(workbook, color, header=False)
            for col_num in range(len(df.columns)):
                worksheet.write(row_num, col_num, df.iloc[row_num - 1, col_num], row_format)
        
        self._adjust_height_and_width(worksheet, len(df) + 1, ExcelConstants.RISK_PATTERNS_LAST_HEADER)
    
    def _adjust_height_and_width(self, worksheet: xlsxwriter.worksheet.Worksheet, limit_row: int, limit_col: int) -> None:
        """Adjust height and width of Excel file"""
        for i in range(limit_col):
            worksheet.set_column(i, i, 30.0)
        
        for i in range(limit_row):
            worksheet.set_row(i, 15.0)
    
    def _get_list_from_relations(self, lib: IRLibrary, attrib: str) -> List[str]:
        """Get list of elements from relations"""
        values_in_library = set()
        for rel in lib.relations.values():
            if attrib == "controls" and rel.control_uuid:
                values_in_library.add(rel.control_uuid)
            elif attrib == "weaknesses" and rel.weakness_uuid:
                values_in_library.add(rel.weakness_uuid)
            elif attrib == "threats" and rel.threat_uuid:
                values_in_library.add(rel.threat_uuid)
            elif attrib == "usecases" and rel.usecase_uuid:
                values_in_library.add(rel.usecase_uuid)
        
        return list(values_in_library)
