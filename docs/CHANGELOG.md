# Changelog


## 2.4.2 - 20250520

### Enhancements

* Added OWASP Top 10 for LLMs 2025 support

## 2.4.1 - 20250512

### Features

* New screening functions to add Mitre ATLAS to threats and countermeasures

### Enhancements

* Fixed bug related with Click (Typer's base library) that was causing an execution error
* Removed GPT model selectable in isra config update. Now the value has to be written manually

## 2.4.0 - 20250310

### Features

* New 'isra standards reset' function that removes all standards in a component
* New way to expand standards, where only those related with OpenCRE will be replaced while others will persist

## 2.3.3 - 20250219

### Enhancements

* Added Emb3d as a parameter for 'isra component info'

## 2.3.2 - 20250218

### Enhancements

* Minor bug fixes

## 2.3.1 - 20250204

### Enhancements

* Added autocomplete function in screening process
* Added support for Mitre EMB3D Framework taxonomy
* Refactored some parts of the code to be more flexible and reusable


## 2.3.0 - 20241031

### Enhancements

* Fixed bug that was preventing OpenCRE to be added to the standards list
* Improved multi-select UI to be able to select when there are more than 36 options
* Moved template functions to a new file to decouple it from other functions
* Fixed bug that was preventing ICSA-500 standard to be added to standard list
* Added new YSC tests
* Added new "Hardware Security" scope
* Added new Mitre EMB3D Framework system field type values
* Now when loading a component from a YSC file it shows the last review date

## 2.2.1 - 20240918

### Features

* First public release
* The ILE option has been removed
* Added new "operating-system" category


## 2.2.0 - 20240814

### Features

* New option in 'isra component save': --format xlsx to save component in .xlsx format
* Now the 'isra component load' accepts .xlsx files. 
* Added support for IIoT components
* Added support for Embedded device components
* Now 'isra component info --p param1/param2/param3' accepts more than one parameter as shown

## 2.1.2 - 20240724

### Features

* Added new option '--p <parameter>' to 'isra component info' to show the information of a specific parameter

### Enhancements

* Fixed problem when pulling questions from IriusRisk
* Fixed bug on resolving paths on Linux systems
* Fixed bug when pulling countermeasures with CWE references that are automatically set in IriusRisk that were causing duplicated references

## 2.1.1 - 20240606

### Enhancements

* Added X-Irius-Async header for 'isra component upload'
* When doing the screening the process shows the previous value to help the user to decide


## 2.1.0 - 20240527

### Features

* Added new 'isra screening autoscreening' that does an automatic screening without any kind of user input
* Added new 'isra screening fix' that fixes the results obtained by the autoscreening
* Removed 'isra screening threat-screening' and 'isra screening control-screening'. Replaced by autoscreening+fix
* Added new 'isra component info --parameter' to be able to see at a glance the attibutes of the elements


### Enhancements

* Added option to include feedback when asking ChatGPT to think again in a screening
* Added option to set different behaviors to set the values when doing the screening
* Added option to manually enter an input in case the value returned by ChatGPT is not correct
* Backups are now stored in a "backup" folder in appdata. Backup files have to be moved into this new folder
* Autoscreening can be configured by editing autoscreening.yaml in "config" folder in appdata if needed

## 2.0.0 - 20240507

### Features

* ISRA repository will be moved to GitHub
* Added new 'isra screening cost' to calculate the cost of implementing a countermeasure
* Added new 'isra standards show' to show the current Standards Matrix with filter options
* Added new 'isra config allowed-values' to show the values that are allowed for system fields in IriusRisk
* Removed properties related with XML folders
* Removed tests related with XML validation
* The default format to save a component is now YAML instead of XML
* Renamed screening processes: 


    isra screening threat     -> isra screening new-threat
    isra screening control    -> isra screening new-control
    isra screening threat-s   -> isra screening threat-screening
    isra screening control-s  -> isra screening control-screening

### Enhancements

* Added pattern validation to questions to avoid having double quotes on them
* Added pattern validation to taxonomies to ensure there are only printable characters
* New process to validate the answers from ChatGPT with the allowed values for the system fields
* New tests to ensure that everything gets correctly uploaded and pulled from IriusRisk
* Updated Standards Matrix with new standards: CCPA
* Improved descriptions

## 1.3.2 - 20240424

### Features

* Added new config variable: company_name. This will be added to the component definition and risk pattern to avoid
  collision with default content

### Enhancements

* General refactor to improve legibility
* Automatically generated CWE references in IR won't be pulled anymore
* New test to check for duplicated values inside taxonomies
* API errors will be shown to the user when calling IR API
* Load from XML has been refactored to be more accurate
* Pull from remote has been updated to export XML instead of using the API until it gets fixed
* CWEs are now updated after screening, even if there was a value present

## 1.3.1 - 20240411

### Features

* Added new 'isra component pull' function to pull attributes for threats and countermeasures from an IR instance
* Added new 'isra config save' and 'isra config load' functions to create config backups
* Added new 'isra component batch' and 'isra component release' to improve release method
* Added new 'isra tests components' to run tests over YAML files.

### Enhancements

* Trailing slashes and other suffixes at the end of the IR URL will be automatically removed
* Fixed wrong options in the baseline screening
* Fixed upload method that failed on some cases when updating lists

## 1.3.0 - 20240409

### Enhancements

* The YAML validator now prints all the errors at the same time
* Added "cost" to schema
* Added hints while waiting for ChatGPT answers
* Fixed many load/save bugs
* Modified custom fields to the right refs
* General code refactor to be more clear

## 1.2.1 - 20240330

### Enhancements

* The baseline standard section is now a list in the YAML format
* The standards expand function now handles more than one section
* Added references to threats and countermeasures
* Added more validations to YSC schema

## 1.2.0 - 20240320

### Features

* New option to upload files to IriusRisk directly from ISRA
* Added --format option to "isra component save" to indicate if the output will be in XML or YAML. XML by default
* Added --force option to "isra component restart" to avoid answering yes or no
* Added new method to load YAML files by using the same "load" function
* Now questionnaire rules can be imported back into ISRA
* Now you don't need to restart the component before loading a new one

### Enhancements

* There was a misunderstood about what the "scope" screening should produce. Now there are two methods: scope and
  audience. Scope tries to find the best scope for a countermeasure, while audience finds who should be the reader
* Questions now shouldn't be generated with plural forms such as "we" or "ours"
* Some methods have been moved to auxiliary functions
* Now the "isra standards expand" function shows which standards have been added to each control
* Fixed bug that was appending || to empty custom values
* Now mitigation values are balanced after loading a component
* Added YAML schema validation when saving a YAML file

## 1.1.0 - 20240212

### Features

* Added --preview option to "isra component save" function to see the XML output without saving it to a file
* Added --full option to "isra component info" to show descriptions and other things that are not relevant
* Added new screening processes to manually create threats and countermeasures, for a more accurate result
* Added new screening function to find a Mitre ATT&CK Mitigation for a given countermeasure

### Enhancements

* Added version number to "isra about"
* Changed "Unsure" answer generated with the question generator to "Not sure" for readability purposes
* Changed "Audience" to "Scope" for readability purposes
* Added a mechanism to attempt to create a threat model until 10 unsuccessful attempts are done
* More tests added to pytest suite
* When doing a screening, if a custom field was present with an empty value it will be counted for the screening process
* Added process to use OpenAI Assistant. If no assistant is defined it will just call ChatGPT
* Added "v2-components" to the available categories
* Now you can append multiple custom fields in some screening functions
* The method to create base standard has been split into "baselines" and "sections"
* Added function to remove non-ASCII characters from ChatGPT response (only for a few common cases)
* Tests are now automatically run in the application folder if no working directory has been specified in the
  configuration

## 1.0.0 - 20240206

### Features

* Initial release