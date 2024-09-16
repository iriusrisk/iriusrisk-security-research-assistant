# `isra`

IriusRisk Security Research Assistant

Amazing CLI tool from our beloved Security Research Team

**Usage**:

```console
$ isra [OPTIONS] COMMAND [ARGS]...
```

**Commands**:

* `about`: Information about this application
* `component`: Component creation
* `config`: Configuration settings
* `screening`: Screening processes
* `standards`: Standard mapping processes
* `tests`: Testing suite

## `isra about`

Information about this application

**Usage**:

```console
$ isra about [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `isra component`

Component creation

**Usage**:

```console
$ isra component [OPTIONS] COMMAND [ARGS]...
```

**Commands**:

* `balance`: Balances the mitigation values of the...
* `batch`: Includes the component into a batch that...
* `clean`: Removes all the generated files
* `info`: Shows current component status
* `load`: Loads an existing component from a file
* `new`: Starts the creation of a new component
* `pull`: Pulls the name, descriptions and metadata...
* `release`: Uploads all batches found to IriusRisk
* `restart`: Removes the current component
* `save`: Saves the component in an IriusRisk XML
* `tm`: Creates a threat model with threats and...
* `upload`: Uploads a component into an IriusRisk...

### `isra component balance`

Balances the mitigation values of the countermeasures so that the values add up to 100 for each threat

**Usage**:

```console
$ isra component balance [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `isra component batch`

Includes the component into a batch that will be uploaded to IriusRisk when the release command is executed

**Usage**:

```console
$ isra component batch [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `isra component clean`

Removes all the generated files

**Usage**:

```console
$ isra component clean [OPTIONS]
```

**Options**:

* `--force / --no-force`: Flag to clean all components automatically  [default: no-force]
* `--help`: Show this message and exit.

### `isra component info`

Shows current component status

**Usage**:

```console
$ isra component info [OPTIONS]
```

**Options**:

* `--full / --no-full`: Shows all properties  [default: no-full]
* `--parameter / --no-parameter`: Shows parameter information  [default: no-parameter]
* `--p TEXT`: Shows parameter information for a given parameter
* `--help`: Show this message and exit.

### `isra component load`

Loads an existing component from a file

**Usage**:

```console
$ isra component load [OPTIONS]
```

**Options**:

* `--file TEXT`: Path to file to import
* `--help`: Show this message and exit.

### `isra component new`

Starts the creation of a new component

**Usage**:

```console
$ isra component new [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `isra component pull`

Pulls the name, descriptions and metadata of threats and countermeasure of a component from IriusRisk

**Usage**:

```console
$ isra component pull [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `isra component release`

Uploads all batches found to IriusRisk

**Usage**:

```console
$ isra component release [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `isra component restart`

Removes the current component

**Usage**:

```console
$ isra component restart [OPTIONS]
```

**Options**:

* `--force / --no-force`: Flag to remove temporal component automatically  [default: no-force]
* `--help`: Show this message and exit.

### `isra component save`

Saves the component in an IriusRisk XML

**Usage**:

```console
$ isra component save [OPTIONS]
```

**Options**:

* `--format TEXT`: Indicate the file format of the source (xml, yaml, xlsx). 'yaml' by default  [default: yaml]
* `--preview / --no-preview`: Show a preview of the output without storing anything  [default: no-preview]
* `--help`: Show this message and exit.

### `isra component tm`

Creates a threat model with threats and countermeasures automatically with ChatGPT or from a file
based on the current component name and description

**Usage**:

```console
$ isra component tm [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `isra component upload`

Uploads a component into an IriusRisk instance

**Usage**:

```console
$ isra component upload [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `isra config`

Configuration settings

**Usage**:

```console
$ isra config [OPTIONS] COMMAND [ARGS]...
```

**Commands**:

* `allowed-values`: Prints all allowed values for IriusRisk's...
* `info`: Shows info about config parameters
* `list`: Shows all properties
* `load`: Loads a configuration file
* `reset`: Resets configuration (in case we need to...
* `save`: Saves a configuration file
* `update`: Updates a property with a specific value

### `isra config allowed-values`

Prints all allowed values for IriusRisk's system fields

**Usage**:

```console
$ isra config allowed-values [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `isra config info`

Shows info about config parameters
 

**Usage**:

```console
$ isra config info [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `isra config list`

Shows all properties

**Usage**:

```console
$ isra config list [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `isra config load`

Loads a configuration file

**Usage**:

```console
$ isra config load [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `isra config reset`

Resets configuration (in case we need to force an update)

**Usage**:

```console
$ isra config reset [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `isra config save`

Saves a configuration file

**Usage**:

```console
$ isra config save [OPTIONS]
```

**Options**:

* `--name TEXT`: Name of the new config file
* `--help`: Show this message and exit.

### `isra config update`

Updates a property with a specific value

**Usage**:

```console
$ isra config update [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `isra screening`

Screening processes

**Usage**:

```console
$ isra screening [OPTIONS] COMMAND [ARGS]...
```

**Commands**:

* `attack`: Adds a Mitre ATT&CK technique reference to...
* `attack-mit`: Adds a Mitre ATT&CK Mitigation reference...
* `autoscreening`: Automated screening process
* `baselines`: Set baseline standards for countermeasures
* `cia`: Adds CIA values for threats
* `cost`: Adds cost values for countermeasures
* `cwe`: Finds best CWE weakness for a countermeasure
* `fix`: Tries to fix anything that doesn't fit the...
* `new-control`: Generates a countermeasure based on the...
* `new-threat`: Generates a threat based on the current...
* `question`: Creates a set of questions for the...
* `scope`: Adds an intended scope for a countermeasure
* `sections`: Set baseline standards sections for...
* `stride`: Adds a STRIDE category to a threat

### `isra screening attack`

Adds a Mitre ATT&CK technique reference to a threat

**Usage**:

```console
$ isra screening attack [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `isra screening attack-mit`

Adds a Mitre ATT&CK Mitigation reference to a countermeasure

**Usage**:

```console
$ isra screening attack-mit [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `isra screening autoscreening`

Automated screening process

**Usage**:

```console
$ isra screening autoscreening [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `isra screening baselines`

Set baseline standards for countermeasures

**Usage**:

```console
$ isra screening baselines [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `isra screening cia`

Adds CIA values for threats

**Usage**:

```console
$ isra screening cia [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `isra screening cost`

Adds cost values for countermeasures

**Usage**:

```console
$ isra screening cost [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `isra screening cwe`

Finds best CWE weakness for a countermeasure

**Usage**:

```console
$ isra screening cwe [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `isra screening fix`

Tries to fix anything that doesn't fit the YSC schema

**Usage**:

```console
$ isra screening fix [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `isra screening new-control`

Generates a countermeasure based on the current component name and description

**Usage**:

```console
$ isra screening new-control [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `isra screening new-threat`

Generates a threat based on the current component name and description

**Usage**:

```console
$ isra screening new-threat [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `isra screening question`

Creates a set of questions for the countermeasures in a component that will change the status
depending on the given answer

**Usage**:

```console
$ isra screening question [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `isra screening scope`

Adds an intended scope for a countermeasure

**Usage**:

```console
$ isra screening scope [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `isra screening sections`

Set baseline standards sections for countermeasures

**Usage**:

```console
$ isra screening sections [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `isra screening stride`

Adds a STRIDE category to a threat

**Usage**:

```console
$ isra screening stride [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `isra standards`

Standard mapping processes

**Usage**:

```console
$ isra standards [OPTIONS] COMMAND [ARGS]...
```

**Commands**:

* `expand`: This function will expand the standard set...
* `show`: Shows the current standard mapping used to...

### `isra standards expand`

This function will expand the standard set of a countermeasure by using the base standard

**Usage**:

```console
$ isra standards expand [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `isra standards show`

Shows the current standard mapping used to propagate standards

**Usage**:

```console
$ isra standards show [OPTIONS]
```

**Options**:

* `--standard-name TEXT`: Filter by standard name
* `--standard-section TEXT`: Filter by standard section
* `--help`: Show this message and exit.

## `isra tests`

Testing suite

**Usage**:

```console
$ isra tests [OPTIONS] COMMAND [ARGS]...
```

**Commands**:

* `components`: Tests that run for YAML components

### `isra tests components`

Tests that run for YAML components

**Usage**:

```console
$ isra tests components [OPTIONS] COMMAND [ARGS]...
```

**Commands**:

* `all`: Run all tests
* `component`: Run pytest with tests that affect each...
* `components`: Run pytest with tests that affect all...

#### `isra tests components all`

Run all tests

**Usage**:

```console
$ isra tests components all [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `isra tests components component`

Run pytest with tests that affect each component separately

**Usage**:

```console
$ isra tests components component [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

#### `isra tests components components`

Run pytest with tests that affect all components at the same time

**Usage**:

```console
$ isra tests components components [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.
