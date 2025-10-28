"""
Data service for IriusRisk Library Editor API
"""

from typing import Dict, List, Set
from isra.src.ile.backend.app.configuration.safety import Safety
from isra.src.ile.backend.app.models import (
    ILEProject, ILEVersion, IRBaseElement, IRLibrary,
    IRRiskPatternItem, IRUseCaseItem, IRThreatItem, 
    IRWeaknessItem, IRControlItem, IRRelation,
    IRProjectReport, IRVersionReport, IRLibraryReport
)


class DataService:
    """Service for managing project data and generating reports"""
    
    def __init__(self):
        self.project: ILEProject = None
    
    def set_project(self, project: ILEProject) -> None:
        """Set current project with validation"""
        if not Safety.is_safe_input(project.ref):
            raise ValueError("Project name is not valid. Project names must be alphanumeric w/o hyphen")
        self.project = project
    
    def get_project(self) -> ILEProject:
        """Get current project"""
        if self.project is None:
            # Create a default project if none exists
            default_project = ILEProject(
                ref="default",
                name="Default Project", 
                desc="Default project created automatically"
            )
            self.project = default_project
        return self.project
    
    def get_version(self, version: str) -> ILEVersion:
        """Get version by reference"""
        return self.project.versions.get(version)
    
    def get_library(self, version: str, library: str) -> IRLibrary:
        """Get library by version and library reference"""
        return self.project.versions.get(version).libraries.get(library)
    
    def put_version(self, version: ILEVersion) -> None:
        """Add version with validation"""
        if version.version in self.project.versions:
            raise ValueError("Version already exists")
        if not Safety.is_safe_input(version.version):
            raise ValueError("Version name is not valid. Version names must be alphanumeric w/o hyphen")
        self.project.versions[version.version] = version
    
    def put_library(self, version: str, library: IRLibrary) -> None:
        """Add library to version"""
        v = self.project.versions.get(version)
        v.libraries[library.ref] = library
    
    def remove_version(self, version: str) -> None:
        """Remove version"""
        self.project.versions.pop(version, None)
    
    def remove_library(self, version: str, library: str) -> None:
        """Remove library from version"""
        self.project.versions.get(version).libraries.pop(library, None)
    
    def get_relations_in_tree(self, lib: IRLibrary) -> Dict[str, IRRiskPatternItem]:
        """Get relations organized in tree structure"""
        risk_patterns = {}
        
        for r in lib.relations.values():
            rp_ref = r.risk_pattern_uuid
            u_ref = r.usecase_uuid
            t_ref = r.threat_uuid
            w_ref = r.weakness_uuid
            c_ref = r.control_uuid
            mit = r.mitigation
            
            rp = risk_patterns.get(rp_ref)
            if rp is None:
                rp = IRRiskPatternItem(rp_ref)
                risk_patterns[rp.ref] = rp
            
            if u_ref != "":
                uc = rp.usecases.get(u_ref)
                if uc is None:
                    uc = IRUseCaseItem(u_ref)
                    rp.usecases[uc.ref] = uc
                
                if t_ref != "":
                    t = uc.threats.get(t_ref)
                    if t is None:
                        t = IRThreatItem(t_ref)
                        uc.threats[t.ref] = t
                    
                    if w_ref != "" and c_ref != "":
                        # Empty threat, nothing to do
                        w = t.weaknesses.get(w_ref)
                        if w is None:
                            w = IRWeaknessItem(w_ref)
                            c = IRControlItem(c_ref, mit)
                            w.controls[c.ref] = c
                            t.weaknesses[w_ref] = w
                        else:
                            c = IRControlItem(c_ref, mit)
                            t.weaknesses[w_ref].controls[c.ref] = c
                    elif w_ref == "" and c_ref != "":
                        # Threat with orphaned control
                        if c_ref not in t.orphaned_controls:
                            c = IRControlItem(c_ref, mit)
                            t.orphaned_controls[c_ref] = c
                    elif w_ref != "":
                        # Threat with empty weakness
                        if w_ref not in t.weaknesses:
                            w = IRWeaknessItem(w_ref)
                            t.weaknesses[w_ref] = w
        
        return risk_patterns
    
    def get_project_report(self) -> IRProjectReport:
        """Get project report"""
        project_report = IRProjectReport(
            project=IRBaseElement(
                ref=self.project.ref,
                name=self.project.name,
                desc=self.project.desc
            )
        )
        
        for v in self.project.versions.values():
            version_report = self.create_version_report(v.version)
            library_reports = []
            for l in v.libraries.values():
                library_report = self.create_library_report(v.version, l.ref)
                library_reports.append(library_report)
            version_report.library_report = library_reports
            project_report.version_reports.append(version_report)
        
        return project_report
    
    def create_version_report(self, version_ref: str) -> IRVersionReport:
        """Create version report"""
        v = self.get_version(version_ref)
        version_report = IRVersionReport()
        version_report.version = v.version
        
        version_report.num_libraries = len(v.libraries)
        version_report.num_risk_patterns = sum(len(lib.risk_patterns) for lib in v.libraries.values())
        version_report.num_usecases = len(v.usecases)
        version_report.num_threats = len(v.threats)
        version_report.num_weaknesses = len(v.weaknesses)
        version_report.num_controls = len(v.controls)
        version_report.num_references = len(v.references)
        version_report.num_standards = len(v.standards)
        version_report.num_categories = len(v.categories)
        version_report.num_components = sum(len(lib.component_definitions) for lib in v.libraries.values())
        version_report.num_rules = sum(len(lib.rules) for lib in v.libraries.values())
        
        library_reports = []
        for l in v.libraries.values():
            library_report = self.create_library_report(v.version, l.ref)
            library_reports.append(library_report)
        version_report.library_report = library_reports
        
        return version_report
    
    def create_library_report(self, version_ref: str, library_ref: str) -> IRLibraryReport:
        """Create library report"""
        l = self.get_version(version_ref).get_library(library_ref)
        library_report = IRLibraryReport()
        
        library_report.library_ref = l.ref
        library_report.library_name = l.name
        library_report.library_desc = l.desc
        library_report.revision = l.revision
        library_report.enabled = l.enabled
        library_report.library_filename = l.filename
        library_report.num_component_definitions = len(l.component_definitions)
        library_report.num_risk_patterns = len(l.risk_patterns)
        library_report.num_rules = len(l.rules)
        
        library_usecases: Set[str] = set()
        library_threats: Set[str] = set()
        
        for re in l.relations.values():
            library_usecases.add(re.usecase_uuid)
            library_threats.add(re.threat_uuid)
        
        library_report.num_usecases = len(library_usecases)
        library_report.num_threats = len(library_threats)
        
        return library_report
