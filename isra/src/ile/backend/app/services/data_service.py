"""
Data service for IriusRisk Content Manager API
"""

from typing import Dict, List, Set, Optional
from isra.src.ile.backend.app.configuration.safety import Safety
from isra.src.ile.backend.app.models import (
    ILEProject, ILEVersion, IRBaseElement, IRLibrary,
    IRRiskPatternItem, IRUseCaseItem, IRThreatItem, 
    IRWeaknessItem, IRControlItem, IRRelation,
    IRProjectReport, IRVersionReport, IRLibraryReport
)


class DataService:
    """Service for managing project data and generating reports"""
    
    _instance: Optional['DataService'] = None
    
    def __new__(cls) -> 'DataService':
        """
        Singleton pattern implementation
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.project: ILEProject = None
            self._initialized = True
    
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
        """Get relations organized in tree structure
        
        Tree structure: Risk pattern > Use case > Threat > Weakness > Control
        
        Handles various cases:
        - Relations from risk pattern directly to control (skipping threat/weakness)
        - Relations without weakness but with control (orphaned control at threat level)
        - Relations with weakness without control
        - Relations without weaknesses nor controls
        - Relations without threats
        - Always requires risk pattern and use case (minimum)
        
        Note: If a control exists without a threat, it cannot be represented in the tree
        structure and will be skipped, as orphaned controls must be at threat level.
        """
        risk_patterns = {}
        
        for r in lib.relations.values():
            # Extract UUIDs (not refs, despite variable naming legacy)
            rp_uuid = r.risk_pattern_uuid
            u_uuid = r.usecase_uuid
            t_uuid = r.threat_uuid
            w_uuid = r.weakness_uuid
            c_uuid = r.control_uuid
            mit = r.mitigation
            
            # Risk pattern and use case are always required (minimum)
            if rp_uuid == "" or u_uuid == "":
                continue  # Skip invalid relations
            
            # Get or create risk pattern
            rp = risk_patterns.get(rp_uuid)
            if rp is None:
                rp = IRRiskPatternItem(ref=rp_uuid)
                risk_patterns[rp.ref] = rp
            
            # Get or create use case
            uc = rp.usecases.get(u_uuid)
            if uc is None:
                uc = IRUseCaseItem(ref=u_uuid)
                rp.usecases[uc.ref] = uc
            
            # If there's a control, mitigation must be present
            if c_uuid != "" and mit == "":
                continue  # Skip relations with control but no mitigation
            
            # If there's a control but no threat, we cannot represent it in the tree
            # structure (orphaned controls require a threat). Still create RP -> UC structure.
            if c_uuid != "" and t_uuid == "":
                # Skip this relation as control cannot be represented without threat
                # RP and UC were already created above, so structure exists for other relations
                continue
            
            # Handle threat level (if threat exists)
            if t_uuid != "":
                # Get or create threat
                t = uc.threats.get(t_uuid)
                if t is None:
                    t = IRThreatItem(ref=t_uuid)
                    uc.threats[t.ref] = t
                
                # Case: Has weakness and control
                if w_uuid != "" and c_uuid != "":
                    # Get or create weakness
                    w = t.weaknesses.get(w_uuid)
                    if w is None:
                        w = IRWeaknessItem(ref=w_uuid)
                        t.weaknesses[w.ref] = w
                    
                    # Add control to weakness
                    if c_uuid not in w.controls:
                        c = IRControlItem(ref=c_uuid, mitigation=mit)
                        w.controls[c.ref] = c
                
                # Case: No weakness but has control (orphaned control at threat level)
                elif w_uuid == "" and c_uuid != "":
                    if c_uuid not in t.orphaned_controls:
                        c = IRControlItem(ref=c_uuid, mitigation=mit)
                        t.orphaned_controls[c_uuid] = c
                
                # Case: Has weakness but no control
                elif w_uuid != "" and c_uuid == "":
                    if w_uuid not in t.weaknesses:
                        w = IRWeaknessItem(ref=w_uuid)
                        t.weaknesses[w.ref] = w
                
                # Case: No weakness and no control (just threat)
                # Nothing to do, threat already created above
        
        return risk_patterns
    
    def get_project_report(self) -> IRProjectReport:
        """Get project report"""
        project_report = IRProjectReport(
            ref=self.project.ref,
            name=self.project.name,
            desc=self.project.desc
        )
        
        for v in self.project.versions.values():
            version_report = self.create_version_report(v.version)
            library_reports = []
            for l in v.libraries.values():
                library_report = self.create_library_report(v.version, l.ref)
                library_reports.append(library_report)
            version_report.library_reports = library_reports
            project_report.version_reports.append(version_report)
        
        return project_report
    
    def create_version_report(self, version_ref: str) -> IRVersionReport:
        """Create version report"""
        v = self.get_version(version_ref)
        if v is None:
            raise ValueError(f"Version '{version_ref}' not found")
        
        # Calculate all the counts
        num_libraries = len(v.libraries)
        num_risk_patterns = sum(len(lib.risk_patterns) for lib in v.libraries.values())
        num_usecases = len(v.usecases)
        num_threats = len(v.threats)
        num_weaknesses = len(v.weaknesses)
        num_controls = len(v.controls)
        num_references = len(v.references)
        num_standards = len(v.standards)
        num_categories = len(v.categories)
        num_components = sum(len(lib.component_definitions) for lib in v.libraries.values())
        num_rules = sum(len(lib.rules) for lib in v.libraries.values())
        
        # Create library reports
        library_reports = []
        for l in v.libraries.values():
            library_report = self.create_library_report(v.version, l.ref)
            library_reports.append(library_report)
        
        # Create the version report with all data
        version_report = IRVersionReport(
            version=v.version,
            num_libraries=num_libraries,
            num_risk_patterns=num_risk_patterns,
            num_usecases=num_usecases,
            num_threats=num_threats,
            num_weaknesses=num_weaknesses,
            num_controls=num_controls,
            num_references=num_references,
            num_standards=num_standards,
            num_categories=num_categories,
            num_components=num_components,
            num_rules=num_rules,
            library_reports=library_reports
        )
        
        return version_report
    
    def create_library_report(self, version_ref: str, library_ref: str) -> IRLibraryReport:
        """Create library report"""
        v = self.get_version(version_ref)
        if v is None:
            raise ValueError(f"Version '{version_ref}' not found")
        
        l = v.get_library(library_ref)
        if l is None:
            raise ValueError(f"Library '{library_ref}' not found in version '{version_ref}'")
        
        # Calculate counts
        library_usecases: Set[str] = set()
        library_threats: Set[str] = set()
        
        for re in l.relations.values():
            library_usecases.add(re.usecase_uuid)
            library_threats.add(re.threat_uuid)
        
        # Create the library report with all data
        library_report = IRLibraryReport(
            library_ref=l.ref,
            library_name=l.name,
            library_desc=l.desc,
            revision=l.revision,
            enabled=l.enabled,
            library_filename=l.filename,
            num_component_definitions=len(l.component_definitions),
            num_risk_patterns=len(l.risk_patterns),
            num_rules=len(l.rules),
            num_usecases=len(library_usecases),
            num_threats=len(library_threats)
        )
        
        return library_report
