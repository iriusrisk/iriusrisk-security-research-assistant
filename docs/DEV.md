# ISRA Developer Guide

This document provides a comprehensive overview of the ISRA (IriusRisk Security Research Assistant) codebase, explaining what each part does and how they work together.

## Table of Contents

1. [Overview](#overview)
2. [Project Structure](#project-structure)
3. [Core CLI Modules](#core-cli-modules)
4. [ICM/ILE Backend](#icmile-backend)
5. [Frontend Application](#frontend-application)
6. [Utilities and Helpers](#utilities-and-helpers)
7. [Resources](#resources)
8. [Configuration System](#configuration-system)
9. [Testing Framework](#testing-framework)
10. [Development Workflow](#development-workflow)

## Overview

ISRA is a Command Line Interface (CLI) tool with an integrated web-based UI (ICM - IriusRisk Content Manager) for creating and managing threat modeling components. The application follows a "content-as-code" approach, using YAML-based component format (YSC) for version control and collaboration.

### Architecture

- **CLI Layer**: Typer-based command-line interface (`isra/main.py`)
- **Core Modules**: Component management, screening, standards, threat modeling
- **Backend API**: FastAPI server for ICM web interface (`isra/src/ile/backend/`)
- **Frontend**: React-based web UI (`frontend/`)
- **Utilities**: Shared functions for XML, YAML, API, GPT interactions
- **Resources**: Prompts, schemas, mappings, and external data

## Project Structure

```
iriusrisk-security-research-assistant/
├── isra/                          # Main Python package
│   ├── main.py                    # CLI entry point (Typer app)
│   └── src/                       # Source code modules
│       ├── component/             # Component management
│       ├── config/                # Configuration system
│       ├── ile/                   # ICM backend
│       ├── screening/             # AI-powered screening
│       ├── standards/             # Standards mapping
│       ├── tm/                    # Threat model generation
│       ├── tests/                 # Test suite
│       ├── utils/                 # Utility functions
│       ├── v2/                    # Version 2 data models
│       ├── srt/                   # Security Research Tools
│       └── resources/             # Static resources
├── frontend/                      # React web application
│   ├── src/                       # React source code
│   │   ├── components/            # React components
│   │   ├── index.js               # React app entry point
│   │   └── ...
│   └── build/                     # Production build
├── docs/                          # Documentation
├── pyproject.toml                 # Poetry dependencies
└── README.md                      # User documentation
```

## Core CLI Modules

### 1. Component Module (`isra/src/component/`)

**Purpose**: Manages threat modeling components in YSC (YAML Structured Components) format.

**Key Files**:
- `component.py`: Main component operations (create, save, load, upload, pull)
- `template.py`: Template management and current component state

**Main Functions**:
- `create_new_component()`: Creates a new component with metadata
- `save_yaml()` / `save_xml()` / `save_xlsx()`: Exports components in different formats
- `load_init()`: Loads a component from file
- `upload_xml()`: Uploads component to IriusRisk platform
- `pull_remote_component_xml()`: Downloads component from IriusRisk
- `balance_mitigation_values_process()`: Automatically balances mitigation values

**Component Structure**:
- Component definition (metadata, category, description)
- Threats (security threats with STRIDE, MITRE ATT&CK mappings)
- Weaknesses (CWE mappings)
- Controls/Countermeasures (mitigations with standards mappings)
- Use cases
- Risk patterns
- Relations (threat-control relationships)

### 2. Configuration Module (`isra/src/config/`)

**Purpose**: Manages application configuration and settings.

**Key Files**:
- `config.py`: Configuration management (load, save, update)
- `constants.py`: Application constants, prefixes, field names

**Configuration Properties**:
- `components_dir`: Directory for YAML components
- `libraries_dir`: Directory for XML libraries
- `gpt_model`: GPT model selection
- `ile_root_folder`: ICM working directory
- `ile_port`: ICM server port
- `component_input_path` / `component_output_path`: Component I/O paths
- `openai_assistant_id`: OpenAI Assistant ID
- `iriusrisk_url` / `iriusrisk_api_token`: IriusRisk API credentials
- `company_name`: Company prefix for component refs
- `openai_client`: OPENAI or AZURE client selection

**Configuration Storage**:
- Main config: `~/.isra/config/isra.yaml`
- Autoscreening config: `~/.isra/config/autoscreening.yaml`
- Temporary files: `~/.isra/config/temp.irius`, `threat_model.json`

### 3. Screening Module (`isra/src/screening/`)

**Purpose**: AI-powered metadata generation for threats and countermeasures.

**Key Files**:
- `screening.py`: CLI commands for screening operations
- `screening_service.py`: Core screening logic and GPT interactions

**Screening Commands**:
- `stride`: Adds STRIDE categories to threats
- `attack`: Adds MITRE ATT&CK Enterprise techniques to threats
- `attack_mit`: Adds MITRE ATT&CK mitigations to countermeasures
- `embed` / `embed_mit`: Adds MITRE EMB3D techniques/mitigations
- `atlas` / `atlas_mit`: Adds MITRE ATLAS techniques/mitigations
- `scope`: Adds intended scope to countermeasures
- `baselines`: Identifies baseline standards (ISO 27001, NIST 800-53, ASVS4)
- `sections`: Maps specific sections from baseline standards
- `cwe`: Maps CWE weaknesses to countermeasures
- `cia`: Adds CIA triad values
- `cost`: Sets proper cost values
- `autoscreening`: Runs all screening operations automatically

**How It Works**:
1. Iterates over threats or controls in the current component
2. Uses GPT prompts to analyze each element
3. Extracts relevant metadata (STRIDE, MITRE, CWE, etc.)
4. Saves the metadata to the component

### 4. Standards Module (`isra/src/standards/`)

**Purpose**: Maps countermeasures to compliance standards using OpenCRE.

**Key Files**:
- `standards.py`: Standards expansion and mapping operations

**Main Functions**:
- `expand_process()`: Expands standards using OpenCRE mappings
- `set_standard_on_components()`: Maps standards from Excel tables
- `get_standard_from_opencre()`: Retrieves related standards from OpenCRE+ mappings

**Standards Supported**:
- ISO 27001 / ISO 27002:2022
- NIST 800-53
- OWASP ASVS4
- NIST 800-63
- FedRAMP
- OWASP Top 10
- PCI DSS
- Cloud Controls Matrix
- CWE

### 5. Threat Model Module (`isra/src/tm/`)

**Purpose**: Generates threat models using AI.

**Key Files**:
- `tm.py`: Threat model generation and editing

**Main Functions**:
- `create_threat_model()`: Uses GPT to generate threats and countermeasures
- `edit_threats_countermeasures()`: Interactive editor for threat model

**Workflow**:
1. User provides component description
2. GPT generates threats and countermeasures
3. User can edit, delete, or modify generated elements
4. Threat model is saved to the component

### 6. Tests Module (`isra/src/tests/`)

**Purpose**: Automated testing suite for components and libraries.

**Key Files**:
- `tests.py`: Test command interface
- `components/`: Component-specific tests
- `libraries/`: Library-specific tests
- `integrity_tests_*.py`: Integrity validation tests

**Test Categories**:
- **Component Tests**: Validate individual component structure and content
- **Library Tests**: Validate library structure and relationships
- **Standards Tests**: Validate standards mappings
- **All Components**: Cross-component validation
- **All Libraries**: Cross-library validation

**Test Execution**:
```bash
isra tests components all          # Run all component tests
isra tests components component    # Test individual components
isra tests libraries all           # Run all library tests
```

### 7. SRT Module (`isra/src/srt/`)

**Purpose**: Security Research Tools - batch processing and release management.

**Key Files**:
- `srt.py`: Batch operations and release building

**Main Functions**:
- `build()`: Creates releases from multiple components
- Batch processing: Processes multiple YAML files
- Component balancing: Automatically balances mitigation values
- Standards expansion: Expands standards for all components

**Workflow**:
1. Reads list of component files (or scans directory)
2. For each component:
   - Loads YAML
   - Balances mitigation values
   - Expands standards
   - Adds to batch for upload

## ICM Backend

**Location**: `isra/src/ile/backend/`

**Purpose**: FastAPI backend server for the ICM web interface.

### Architecture

The backend follows a layered architecture:

```
Controllers (API endpoints)
    ↓
Facades (Business logic abstraction)
    ↓
Services (Business logic)
    ↓
IO Services (File operations)
```

### Directory Structure

```
backend/
├── main.py                    # FastAPI app initialization
└── app/
    ├── configuration/         # Configuration management
    │   ├── config_factory.py  # Configuration factory
    │   ├── environment.py     # Environment config
    │   ├── properties_manager.py  # Properties management
    │   └── safety.py          # Security utilities
    ├── controllers/           # API route handlers
    │   ├── project_controller.py
    │   ├── version_controller.py
    │   ├── library_controller.py
    │   ├── changelog_controller.py
    │   ├── test_controller.py
    │   └── marketplace_controller.py
    ├── facades/               # Business logic layer
    │   ├── project_facade.py
    │   ├── version_facade.py
    │   ├── library_facade.py
    │   └── io_facade.py
    ├── services/              # Core business logic
    │   ├── project_service.py
    │   ├── version_service.py
    │   ├── library_service.py
    │   ├── test_service.py
    │   ├── changelog_service.py
    │   ├── data_service.py
    │   └── io/                # Import/Export services
    │       ├── xml_import_service.py
    │       ├── xml_export_service.py
    │       ├── xlsx_import_service.py
    │       ├── xlsx_export_service.py
    │       └── ysc_import_service.py
    ├── models/                # Data models
    │   ├── base.py            # Base element classes
    │   ├── elements.py        # Core element models
    │   ├── project.py         # Project models
    │   ├── reports.py         # Report models
    │   ├── graph.py           # Graph/visualization models
    │   └── requests.py        # Request/Response models
    └── resources/
        └── XSD_Schema/        # XML Schema definitions (100+ files)
```

### Key Components

#### Controllers

Handle HTTP requests and responses:

- **Project Controller**: Project CRUD operations, version management
- **Version Controller**: Version operations, element management
- **Library Controller**: Library operations, risk patterns, relations
- **Changelog Controller**: Changelog generation and comparison
- **Test Controller**: Test execution and reporting
- **Marketplace Controller**: Marketplace operations

#### Services

Core business logic:

- **Project Service**: Manages projects (create, load, save, export)
- **Version Service**: Manages versions and their elements
- **Library Service**: Manages libraries, risk patterns, relations
- **Test Service**: Executes tests and generates reports
- **Changelog Service**: Generates changelogs between versions/libraries
- **Data Service**: Data aggregation and statistics

#### IO Services

File import/export:

- **XML Import/Export**: IriusRisk XML format
- **XLSX Import/Export**: Excel format
- **YSC Import**: YAML Structured Components format

#### Models

Data structures:

- **Base Models**: `IRBaseElement`, `IRBaseElementNoUUID`
- **Element Models**: `IRThreat`, `IRWeakness`, `IRControl`, `IRComponentDefinition`, `IRRiskPattern`, etc.
- **Project Models**: `ILEProject`, `ILEVersion`
- **Report Models**: Various report structures
- **Graph Models**: Node/Link structures for visualizations

### API Endpoints

All API endpoints are prefixed with `/api`:

- `/api/project/*`: Project operations
- `/api/version/*`: Version operations
- `/api/library/*`: Library operations
- `/api/changelog/*`: Changelog operations
- `/api/test/*`: Test operations
- `/api/marketplace/*`: Marketplace operations
- `/health`: Health check

### Static File Serving

The backend can serve the compiled React frontend:
- Static assets: `/static/*`
- React app: Root path and all non-API routes
- API routes: `/api/*` (takes precedence)

## Frontend Application

**Location**: `frontend/`

**Technology**: React with Material-UI

### Structure

```
frontend/src/
├── index.js                   # App entry point, routing, main layout
├── components/
│   ├── project/               # Project management
│   │   ├── Project.js
│   │   └── operations/       # Project operations
│   ├── version/               # Version management
│   │   ├── Version.js
│   │   └── operations/        # Version operations
│   ├── library/               # Library management
│   │   ├── Library.js
│   │   └── operations/        # Library operations
│   ├── marketplace/           # Marketplace
│   │   └── Marketplace.js
│   └── utils/                 # Utility components
└── assets/                    # Images, logos
```

### Key Components

#### Main App (`index.js`)

- **Dashboard**: Main layout with drawer navigation
- **Router**: React Router for client-side routing
- **State Management**: Custom hooks for project/version state
- **Activity Indicator**: Global loading indicator
- **Context Menu**: Right-click context menus

#### Project Components

- **Project.js**: Project overview and management
- **CreateProject.js**: Create new project
- **LoadProject.js**: Load existing project
- **ManageVersion.js**: Version management (create, copy, delete)
- **MergeLibraries.js**: Merge multiple libraries
- **CreateChangelogBetweenVersions.js**: Generate changelogs
- **CleanFolders.js**: Clean up project folders

#### Version Components

- **Version.js**: Version overview
- **CreateElements.js**: Bulk element creation
- **ManageThreats.js**: Threat management
- **ManageWeaknesses.js**: Weakness management
- **ManageControls.js**: Control/countermeasure management
- **ManageStandards.js**: Standards management
- **ManageReferences.js**: Reference management
- **ManageLibraries.js**: Library management within version
- **ManageCategories.js**: Category management
- **ImportLibraryToVersion.js**: Import library to version
- **CreateReports.js**: Generate reports
- **RunContentTests.js**: Execute tests
- **AdvancedRelationCanvas.js**: Visual relation editor

#### Library Components

- **Library.js**: Library overview
- **ManageComponents.js**: Component management
- **ManageRelations.js**: Relation management
- **ManageRiskPatterns.js**: Risk pattern management
- **SetMitigationValues.js**: Set mitigation values
- **CreateRulesGraph.js**: Rules graph visualization

#### Marketplace Components

- **Marketplace.js**: Marketplace overview
- **ManageReleaseNotes.js**: Release notes management

### Routing

Routes are defined in `index.js`:

- `/`: Home page
- `/project`: Project management
- `/project/createProject`: Create project
- `/project/loadProject`: Load project
- `/project/manageVersion`: Manage versions
- `/version/:id`: Version view
- `/version/:id/manageThreats`: Manage threats
- `/version/:id/:lib`: Library view
- `/marketplace`: Marketplace

### API Communication

Uses `axios` for HTTP requests to the backend API:
- Base URL: Configured via `REACT_APP_API_URL` (defaults to backend port)
- All requests go to `/api/*` endpoints

## Utilities and Helpers

**Location**: `isra/src/utils/`

### Key Utility Modules

#### `api_functions.py`

IriusRisk API integration:
- `upload_xml()`: Upload component to IriusRisk
- `pull_remote_component_xml()`: Download component from IriusRisk
- `get_category()` / `post_category()`: Category operations
- `get_component_definition()` / `post_component_definition()`: Component operations
- `get_library()` / `post_library()`: Library operations
- `add_to_batch()` / `release_component_batch()`: Batch operations

#### `gpt_functions.py`

OpenAI/Azure OpenAI integration:
- `query_chatgpt()`: Sends messages to GPT API
- `get_prompt()`: Loads prompt templates from resources

#### `yaml_functions.py`

YAML file operations:
- `load_yaml_file()`: Loads YAML file
- `save_yaml_file()`: Saves YAML file
- `validate_yaml()`: Validates against YSC schema

#### `xml_functions.py`

XML file operations:
- `load_xml_file()`: Loads IriusRisk XML
- `save_xml_file()`: Saves IriusRisk XML
- `import_content_into_template()`: Imports XML into component template
- `export_content_into_category_library()`: Exports component to XML library
- `create_*_element()`: Creates XML elements for threats, controls, etc.

#### `xlsx_functions.py`

Excel file operations:
- `load_xlsx_file()`: Loads Excel file
- `save_xlsx_file()`: Saves Excel file

#### `text_functions.py`

Text processing utilities:
- `extract_json()`: Extracts JSON from text
- `get_company_name_prefix()`: Gets company prefix
- `get_allowed_system_field_values()`: Gets allowed taxonomy values

#### `structure_functions.py`

Data structure operations:
- Component structure manipulation
- Element reference management

#### `questionary_wrapper.py`

Interactive CLI prompts:
- `qselect()`: Single selection
- `qmulti()`: Multiple selection
- `qtext()`: Text input
- `qconfirm()`: Confirmation
- `qpath()`: Path selection

#### `log_functions.py`

Logging utilities

#### `decorators.py`

Decorators:
- `get_time()`: Timing decorator

## Resources

**Location**: `isra/src/resources/`

### Key Resources

#### Prompts (`prompts/`)

GPT prompt templates (28 files):
- `generate_threat_model.md`: Threat model generation
- `get_stride_category.md`: STRIDE categorization
- `get_attack_technique.md`: MITRE ATT&CK mapping
- `get_proper_cwe.md`: CWE mapping
- `get_baseline_standard_ref.md`: Baseline standard identification
- `get_baseline_standard_section.md`: Standard section mapping
- And many more...

#### Schemas and Mappings

- `ysc_schema.json`: YSC format JSON schema
- `cre_mappings_plus.yaml`: OpenCRE+ mappings for standards expansion
- `output_system_fields_values.yaml`: Allowed taxonomy values
- `rules.yaml`: Scoring rules
- `marketplace_structure.json`: Marketplace structure definition

#### External Data

- `cwec_v4.13.xml`: CWE database
- `external_info/`:
  - `asvs.jsonl`: OWASP ASVS data
  - `cwe.jsonl`: CWE data
  - `mitre_attack_mitigations.jsonl`: MITRE ATT&CK mitigations

## Configuration System

### Configuration Files

1. **Main Config** (`~/.isra/config/isra.yaml`):
   - Application settings
   - API credentials
   - Directory paths
   - Model selection

2. **Autoscreening Config** (`~/.isra/config/autoscreening.yaml`):
   - Autoscreening preferences
   - Screening operation settings

3. **Temporary Files**:
   - `temp.irius`: Current component in memory
   - `threat_model.json`: Current threat model

### Configuration Management

- `isra config info`: Shows configurable parameters
- `isra config update`: Interactive configuration update
- `isra config list`: Lists all configuration values
- `isra config allowed-values`: Shows allowed taxonomy values

### Environment Variables

- `AZURE_OPENAI_API_KEY`: Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT`: Azure OpenAI endpoint
- `OPENAI_API_KEY`: OpenAI API key (alternative)
- `APPDIR`: Application directory (for ICM)
- `SERVER_PORT`: Server port (for ICM)
- `SERVER_HOST`: Server host (for ICM)
- `SERVE_STATIC`: Enable static file serving
- `STATIC_DIR`: Static files directory

## Testing Framework

### Test Structure

```
isra/src/tests/
├── tests.py                    # Test command interface
├── components/                 # Component tests
│   ├── test_component.py      # Individual component tests
│   └── test_all_components.py # Cross-component tests
├── libraries/                  # Library tests
│   ├── test_library.py        # Individual library tests
│   ├── test_all_libraries.py  # Cross-library tests
│   └── test_standards.py      # Standards tests
└── integrity_tests_*.py       # Integrity validation
```

### Test Execution

Uses `pytest`:
```bash
isra tests components all
isra tests libraries all
```

### Test Types

1. **Component Tests**: Validate component structure, required fields, references
2. **Library Tests**: Validate library structure, relationships, consistency
3. **Standards Tests**: Validate standards mappings, references
4. **Integrity Tests**: Cross-component/library validation

## Development Workflow

### Expected Workflow

```
1. isra component new          # Create new component
2. isra component tm           # Generate threat model with AI
3. isra screening stride       # Add STRIDE categories
4. isra screening cwe          # Map CWE weaknesses
5. isra screening baselines    # Identify baseline standards
6. isra screening sections    # Map standard sections
7. isra standards expand       # Expand standards via OpenCRE
8. isra component save         # Save component (YAML/XML/XLSX)
```

### Setup for Development

1. **Install Dependencies**:
   ```bash
   poetry install
   poetry shell
   ```

2. **Configure Environment**:
   ```bash
   export AZURE_OPENAI_API_KEY=<key>
   export AZURE_OPENAI_ENDPOINT=<endpoint>
   isra config update
   ```

3. **Build Frontend** (for ICM):
   ```bash
   cd frontend
   npm install
   npm run build
   ```

4. **Run Tests**:
   ```bash
   isra tests components all
   ```

### Building and Packaging

1. **Build Frontend**:
   ```bash
   cd frontend
   npm run build
   ```

2. **Build Python Package**:
   ```bash
   poetry build
   ```

3. **Install from Wheel**:
   ```bash
   pip install dist/isra-<version>.whl
   ```

### Running ICM

**Production Mode** (backend serves frontend):
```bash
isra ile run
```

**Development Mode** (separate backend and frontend):
```bash
# Terminal 1: Backend
isra ile backend

# Terminal 2: Frontend
cd frontend
npm start
```

### Code Generation

**Generate Command Documentation**:
```bash
typer isra/main.py utils docs --name isra --output docs/DOCS.md
```

**Generate Schema Documentation**:
```bash
generate-schema-doc --config template_name=md --config expand_buttons \
  isra/src/resources/ysc_schema.json docs/SCHEMA.md
```

## Key Concepts

### YSC Format (YAML Structured Components)

Human-readable YAML format for components:
- Easier to edit than XML
- Version control friendly
- Validates against JSON schema
- Converts to/from IriusRisk XML

### Component Lifecycle

1. **Creation**: `component new` - Creates empty component
2. **Threat Modeling**: `component tm` - Generates threats/controls
3. **Screening**: `screening *` - Adds metadata
4. **Standards**: `standards expand` - Maps compliance standards
5. **Validation**: `tests` - Validates component
6. **Export**: `component save` - Saves in various formats
7. **Upload**: `component upload` - Uploads to IriusRisk

### ICM Project Structure

```
project/
├── config/          # Project configuration
├── projects/        # Project definitions
├── versions/        # Version definitions
└── output/          # Generated outputs
```

### Element References

All elements use prefixes:
- Components: `CD-V2-*`
- Risk Patterns: `RP-V2-*`
- Use Cases: `UC-*`
- Threats: `T-*`
- Countermeasures: `C-*`

## Troubleshooting

### Common Issues

1. **Configuration not found**: Run `isra config update`
2. **GPT API errors**: Check API key and endpoint
3. **Frontend not loading**: Ensure `npm run build` was executed
4. **Import errors**: Check file paths and formats
5. **Test failures**: Validate component structure and references

### Debugging

- Check logs in `~/.isra/` directory
- Use `isra config list` to verify configuration
- Validate YAML against schema: `validate_yaml()`
- Check API responses in backend logs

---

**For user documentation, see [README.md](../README.md)**  
**For command reference, see [DOCS.md](DOCS.md)**
