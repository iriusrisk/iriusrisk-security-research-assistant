# ISRA Dev Guide

Here's a list of things to take into account when adding changes.

### Expected workflow

![](workflow.png)

### Dependencies

This project uses Poetry to handle dependencies. Dependencies can be found in the pyproject.toml file.
To create a new virtual environment use the following:
    
    poetry install


### Testing ISRA

    poetry shell

### Build and install

This project uses Poetry to build the wheel package.

    poetry build

The dist folder will contain the .whl file for pip.


### How to install in CLI

    pip install path/to/isra-<version>.whl

If the installation was successful the following command should work:

    isra

Now, the first thing to do is to configure the OpenAI API key so that ChatGPT functionalities can work. It's up to you and your system to set the environment variable. E.g.:

    export OPENAI_API_KEY=<api-key>

After that, run the following:

    isra config info
    isra config update
    <select gpt_model>
    <select gpt model to use>
    isra config list

### Basic usage

See README.md to find the complete list of commands.

ISRA has been created with the following workflow in mind:

    1. isra component new          # Create a new component from zero
    2. isra component tm           # Create a TM for this component using ChatGPT
    3. isra screening <command>    # Iterates over the elements to perform actions
    4. isra standards <command>    # Iterates over countermeasures to add/propagate standards
    5. isra component save         # Saves the component in IriusRisk XML format

### Generate README.md automatically

Use Typer-CLI to automatically generate the docs of a Typer application:

    typer isra\main.py utils docs --name isra --output docs/DOCS.md

This requires Typer-CLI to be installed locally.

### Generate SCHEMA.md automaticall

Use json-schema-for-humans to automatically generate a Markdown file:

    generate-schema-doc --config template_name=md --config expand_buttons .\isra\src\resources\ysc_schema.json .\docs\SCHEMA.md