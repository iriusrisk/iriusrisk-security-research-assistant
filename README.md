# ISRA (IriusRisk Security Research Assistant)

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/badge/poetry-managed-60A5FA.svg)](https://python-poetry.org/)

**ISRA** is a Command Line Interface (CLI) utility developed by the Security Research Team at IriusRisk. It assists in the creation of threat model components following a "content-as-code" approach, enabling security researchers and engineers to build, manage, and enhance threat modeling components with rich metadata.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Workflow](#workflow)
- [ICM (IriusRisk Content Manager)](#icm-iriusrisk-content-manager)
- [YSC Format](#ysc-format)
- [Documentation](#documentation)
- [Notes](#notes)

## Overview

ISRA streamlines the creation and management of threat modeling components by:

- **Automating metadata generation** using AI-powered screening processes
- **Mapping to compliance standards** (ISO 27001, NIST 800-53, OWASP ASVS, etc.)
- **Integrating with IriusRisk** for seamless component deployment
- **Supporting collaborative workflows** through YAML-based component format (YSC)
- **Providing a web-based UI** (ICM) for visual component management

## Features

ISRA offers a comprehensive suite of commands for security operations:

### Core Commands

- **`about`** - Display version information and application overview
- **`component`** - Manage threat modeling components (create, modify, save, load, upload, pull)
- **`config`** - Configure ISRA settings, including GPT model selection and allowed values
- **`screening`** - Automated metadata generation:
  - STRIDE categorization for threats
  - CWE weakness mapping for countermeasures
  - MITRE ATT&CK technique references
  - Baseline standard identification (ISO 27001, NIST 800-53, ASVS4)
  - Standard section mapping
- **`standards`** - Map countermeasures to compliance standards using OpenCRE
- **`tests`** - Execute automated test suites on YAML components

### Additional Features

- **Threat Model Generation** - AI-powered threat and countermeasure creation
- **Batch Operations** - Process multiple components for release
- **Component Balancing** - Automatically balance mitigation values
- **IriusRisk Integration** - Upload and pull components from IriusRisk platform

## Prerequisites

- **Python 3.9+**
- **Poetry** (for development builds)
- **Azure OpenAI API Key** (for AI-powered features)
- **IriusRisk API credentials** (optional, for platform integration)

## Installation

### Option 1: Install from Wheel Package

```bash
pip install path/to/isra-<version>.whl
```

### Option 2: Install from Source

```bash
git clone git@github.com:iriusrisk/iriusrisk-security-research-assistant.git
cd iriusrisk-security-research-assistant
pip install .
```

### Option 3: Install with Poetry (Development)

```bash
git clone git@github.com:iriusrisk/iriusrisk-security-research-assistant.git
cd iriusrisk-security-research-assistant
poetry install
poetry shell
```

### Verify Installation

After installation, verify that ISRA is working:

```bash
isra
```

You should see the ISRA command-line interface with available commands.

## Configuration

### 1. Set Azure OpenAI API Key

ISRA uses Azure OpenAI's API for AI-powered features. Set your API key as an environment variable:

**Linux/macOS:**
```bash
export AZURE_OPENAI_API_KEY=<your-api-key>
export AZURE_OPENAI_ENDPOINT=<IriusRisk-Azure-OpenAI-Endpoint>
```

**Windows (PowerShell):**
```powershell
$env:AZURE_OPENAI_API_KEY="<your-api-key>"
$env:AZURE_OPENAI_ENDPOINT="<IriusRisk-Azure-OpenAI-Endpoint>"
```

**Windows (Command Prompt):**
```cmd
set AZURE_OPENAI_API_KEY=<your-api-key>
set AZURE_OPENAI_ENDPOINT=<IriusRisk-Azure-OpenAI-Endpoint>
```

### 2. Configure ISRA

Run the configuration commands to set up ISRA:

```bash
# View information about configurable parameters
isra config info

# Update configuration (interactive)
isra config update

# List all configuration settings
isra config list
```

## Usage

### Basic Commands

#### Get Application Information

```bash
isra about
```

Displays the current version and information about ISRA.

#### Component Management

```bash
# Create a new component
isra component new

# View component information
isra component info

# Save component (YAML by default)
isra component save --format yaml
isra component save --format xml
isra component save --format xlsx

# Load component from file
isra component load # Prompts an interactive console
isra component load --file /path/to/component.yaml

# Upload to IriusRisk
isra component upload

# Pull from IriusRisk
isra component pull
```

#### Screening Operations

```bash
# Set STRIDE categories for threats
isra screening stride

# Map CWE weaknesses to countermeasures
isra screening cwe

# Identify baseline standards
isra screening baselines

# Map standard sections
isra screening sections
```

#### Standards Mapping

```bash
# Expand standards using OpenCRE
isra standards expand
```

### Getting Help

For detailed help on any command:

```bash
# General help
isra --help

# Command-specific help
isra <command> --help
isra component --help
isra screening --help
```

## Workflow

The typical workflow for creating a threat modeling component with ISRA:

![Workflow Diagram](docs/workflow.png)

### Complete Example Workflow

**Use Case:** Create a component with threats and countermeasures for a threat model diagram.

```bash
# 1. Create a new component
isra component new

# 2. Generate threat model (threats and countermeasures)
isra component tm

# 3. Add STRIDE categorization to threats
isra screening stride

# 4. Map CWE weaknesses to countermeasures
isra screening cwe

# 5. Identify baseline standards (ISO 27001, NIST 800-53, ASVS4)
isra screening baselines

# 6. Map specific sections from baseline standards
isra screening sections

# 7. Expand standards using OpenCRE
isra standards expand

# 8. Save component in YAML format
isra component save --format yaml
```

The output is a **YSC (YAML Structured Component)** file that can be:
- Version controlled in Git
- Shared and reviewed collaboratively
- Loaded and modified later
- Uploaded to IriusRisk

### Working with Saved Components

```bash
# Load a component from file
isra component load                         # Interactive file selection
isra component load --file /path/to/file   # Load specific file

# Upload to IriusRisk platform
isra component upload

# Pull component from IriusRisk
isra component pull
```

## ICM (IriusRisk Content Manager)

ISRA includes **ICM (IriusRisk Content Manager)**, a web-based user interface for managing threat modeling components visually. ICM provides:

- **Visual Component Management** - Browse and edit components through a web interface
- **Version Control** - Manage component versions and releases
- **Marketplace Management** - Organize and publish components
- **Library Operations** - Import/export components in various formats (XML, XLSX, YAML)

### Using ICM

There are two ways to use ICM:

#### Option 1: Automatic Service (Production)

Run ICM with a single command that automatically starts both backend and frontend:

```bash
isra ile run
```

This command starts the ICM service where the backend serves the frontend on a user-defined port (configured via `isra config update`).

#### Option 2: Development Mode (Separate Backend and Frontend)

For development, you can run the backend and frontend independently:

**Start the backend:**
```bash
isra ile backend
```

**Start the frontend (in a separate terminal):**
```bash
cd frontend
npm install  # Only needed on first run
npm start
```

The frontend will run on port 3000. This setup is helpful for developing both sides independently, allowing you to see changes in real-time during development.

### Building ICM for Production

When the project is ready, generate a production build:

```bash
cd frontend
npm run build
```

This creates an optimized build of the frontend application.

### Including Frontend Build in ISRA Package

To generate a new ISRA version that includes the updated frontend build:

1. Create the frontend build (as shown above)
2. Run Poetry build:

```bash
poetry build
```

This will package ISRA with the new frontend build included.

## YSC Format

Components created with ISRA use the **YSC (YAML Structured Components)** format, which:

- **Decouples from XML** - Easier to read, write, and modify than XML
- **Supports rich metadata** - Handles various types of security data
- **Enables collaboration** - Human-readable format perfect for version control
- **Validates against schema** - Ensures component structure integrity

### Important Note on Allowed Values

While YSC format is flexible, IriusRisk only accepts specific taxonomy values. ISRA will warn you about invalid values when loading components, but automatic validation is not yet available.

To check allowed values:

```bash
isra config allowed-values
```

## Documentation

For comprehensive documentation, see:

- **[DOCS.md](docs/DOCS.md)** - Complete command reference with all options and parameters
- **[DEV.md](docs/DEV.md)** - Developer guide for contributing to ISRA
- **[CHANGELOG.md](docs/CHANGELOG.md)** - Version history and changes

## Notes

### Taxonomy Values

Components created with ISRA use the YSC format, which is more flexible than the IriusRisk XML format. However, IriusRisk only accepts specific allowed values for certain fields. ISRA will warn you about invalid values when loading components, but automatic correction is not yet implemented.

To view allowed taxonomy values:

```bash
isra config allowed-values
```

### Dependencies

ISRA uses the following key technologies:

- **Typer** - CLI framework
- **OpenAI** - AI-powered threat modeling
- **PyYAML** - YAML processing
- **FastAPI** - ICM backend server
- **React** - ICM frontend (included in package)

See `pyproject.toml` for the complete list of dependencies.

### Support

For issues, questions, or contributions, please refer to the project repository or contact the IriusRisk Security Research Team.

---

**Made with ❤️ by the IriusRisk Security Research Team**
