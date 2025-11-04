"""
IO facade for IriusRisk Library Editor API
"""

from typing import BinaryIO
from isra.src.ile.backend.app.models import ILEVersion, IRLibrary
from isra.src.ile.backend.app.services.io.xml_import_service import XMLImportService
from isra.src.ile.backend.app.services.io.xlsx_import_service import XLSXImportService
from isra.src.ile.backend.app.services.io.xml_export_service import XMLExportService
from isra.src.ile.backend.app.services.io.xlsx_export_service import XLSXExportService
from isra.src.ile.backend.app.services.io.ysc_import_service import YSCImportService


class IOFacade:
    """IO facade for handling file import/export operations"""
    
    def __init__(self):
        self.xml_import_service = XMLImportService()
        self.xlsx_import_service = XLSXImportService()
        self.xml_export_service = XMLExportService()
        self.xlsx_export_service = XLSXExportService()
        self.ysc_import_service = YSCImportService()
    
    def import_library_xml(self, filename: str, library: BinaryIO, version_element: ILEVersion) -> None:
        """Import library from XML"""
        self.xml_import_service.import_library_xml(filename, library, version_element)
    
    def import_library_xlsx(self, filename: str, library: BinaryIO, version_element: ILEVersion) -> None:
        """Import library from XLSX"""
        self.xlsx_import_service.import_library_xlsx(filename, library, version_element)

    def import_ysc_component(self, filename: str, library: BinaryIO, version_element: ILEVersion) -> None:
        """Import component from YSC"""
        self.ysc_import_service.import_ysc_component(filename, library, version_element)
    
    def export_library_xml(self, lib: IRLibrary, version: ILEVersion, version_path: str) -> None:
        """Export library to XML"""
        self.xml_export_service.export_library_xml(lib, version, version_path)
    
    def export_library_xlsx(self, lib: IRLibrary, version: ILEVersion, version_path: str) -> None:
        """Export library to XLSX"""
        self.xlsx_export_service.export_library_xlsx(lib, version, version_path)
