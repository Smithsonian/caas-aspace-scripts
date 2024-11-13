# Smithsonian ArchivesSpace Scripts
## Overview
A collection of Python/SQL scripts for data cleanup, management, and others related to the Smithsonian's ArchivesSpace 
implementation.

### Metadata Cleanup Scripts
#### [remove_missingtitles.py](python_scripts/remove_missingtitles.py)
This script takes a CSV of resources and archival objects from every repository with "Missing Title" titles in note 
lists and removes the title from the metadata, then posts the update to ArchivesSpace

##### Tests:
- [missingtitles_tests.py](tests/missingtitles_tests.py)

##### Requirements:
- Packages:
  - [ArchivesSnake](https://github.com/archivesspace-labs/ArchivesSnake)
  - [loguru](https://github.com/Delgan/loguru)
- ArchivesSpace username, password, API URL in a secrets.py file
- logs directory for storing local log files
- test_data/missingtitles_testdata.py file, with the following:
  - `test_object_metadata = {ArchivesSpace resource or archival object metadata}` for testing. Can get this from your 
API by using a `client.get` request for a resource or archival object that has a "Missing Title" in one of its notes 
with a list.
  - `test_notes = [ArchivesSpace resource or archival object notes list]` for testing. Can get this from your 
API using a `client.get` request for a resource or archival object that has a "Missing Title" in one of its notes 
with a list and taking all the data found in `"notes" = [list of notes]`
- test_data/MissingTitles_BeGone.csv - a csv file containing the URIs of the objects that have "Missing Title" in their
notes. URIs should be in the 4th spot (`row[3]`)

#### [update_znames.py](python_scripts/update_znames.py)

This script collects all users from ArchivesSpace, parses their usernames to separate any starting with 'z-' and
ending with '-expired-' into just the text in-between, then updates the username in ArchivesSpace with the new 
username

##### Tests:
- [znames_tests.py](tests/znames_tests.py)

##### Requirements:
- Packages:
  - [ArchivesSnake](https://github.com/archivesspace-labs/ArchivesSnake)
  - [loguru](https://github.com/Delgan/loguru)
- ArchivesSpace username, password, API URL in a secrets.py file
- logs directory for storing local log files
- test_data/znames_testdata.py file, with `viewer_user = {ArchivesSpace viewer user metadata}` for testing. Can get this
from your API by getting a `client.get` request for the `viewer' user in your ArchivesSpace instance.

#### [delete_dometadata.py](python_scripts/delete_dometadata.py)
This script iterates through all the digital objects in every repository in SI's ArchivesSpace instance - except Test, 
Training, and NMAH-AF, parses them for any data in the following fields: agents, dates, extents, languages, notes, 
and subjects, and then deletes any data within those fields except digitized date and uploads the updated digital 
object back to ArchivesSpace

##### Tests:
- [dometadata_tests.py](tests/dometadata_tests.py)

##### Requirements:
- Packages:
  - [ArchivesSnake](https://github.com/archivesspace-labs/ArchivesSnake)
  - [loguru](https://github.com/Delgan/loguru)
- ArchivesSpace username, password, API URL in a secrets.py file
- logs directory for storing local log files
- test_data/dometadata_testdata.py file, with the following variables:
  - `test_record_type = string` - the object endpoint ArchivesSpace uses; ex. 'digital_objects'
  - `test_object_id = int` - the number of the digital object you want to use for testing (must have metadata in 
above-mentioned fields)
  - `test_object_repo_uri = string` - the repository URI where the test digital object is; ex. '/repositories/12'
  - `test_object_user_identifier = string` - the identifier that user's input in the digital_object_id field for testing; 
ex. 'NMAI.AC.066.ref21.1'
  - `test_digital_object_dates = dict` - JSON data from a digital object that contains multiple date subrecords
  - `test_digital_object_dates_deleted = dict` JSON data from the same digital object as above but without any data in
the dates field (i.e. `dates = []`)

### Reporting Scripts

#### [eepa_cameroonreport.py](python_scripts/eepa_cameroonreport.py)
This script takes CSV files listing specific collections from EEPA repository, extracts the resource URIs listed in
each CSV, uses the ArchivesSpace API to grab the Abstract or Scope and Contents note from the JSON data, and writes
the note to the provided CSV in a new column.

##### Tests:
- [eepacameroon_tests.py](tests/eepacameroon_tests.py)

##### Requirements:
- CSV input(s) containing the following columns: ead_id,title,dates,publish,level,extents,uri
  - Note: This script originally had 3 CSVs to iterate through, but any number of CSVs should work
- ArchivesSnake
- ArchivesSpace username, password, API URL in a secrets.py file
- logs directory for storing local log files
- test_data/eepacameroon_testdata.py file, with 3 variables:
  - `test_abstract_only_json = dict` - JSON data from a resource that contains only an abstract note
  - `test_scope_only_json = dict` - JSON data from a resource that contains only a scope note
  - `test_no_abstract_scope_json = dict` - JSON data from a resource that contains no abstract or scope note
  - Note for the above variables and values: these are for testing. You can get these from your API by running a 
`client.get` request for resources using their URI and the .json() function to return data in JSON format.

#### [identifier_report.py](python_scripts/identifier_report.py)

This script reads a CSV containing all the resource and accession identifiers in ArchivesSpace and prints a
dictionary containing all the unique, non-alphanumeric characters in the identifiers and their counts

##### Requirements:
- CSV input containing the following columns: id, repo_id, identifier, title, ead_id, recordType
  - identifier should be structured like so: "['id_0','id_1','id_2','id_3']"

## Getting Started

### Dependencies
Not every script requires every package as listed in the requirements.txt file. If you need to use a script, check the 
import statements at the top to see which specific packages are needed.

- [ArchivesSnake](https://github.com/archivesspace-labs/ArchivesSnake) - Library used for interacting with the 
ArchivesSpace API
- [loguru](https://pypi.org/project/loguru/) - Library used for generating log files

### Installation

1. Download the repository via cloning to your local IDE or using GitHub's Code button and Download as ZIP
2. Run `pip install requirements.txt` or check the import statements for the script you want to run and install those 
packages
3. Create a secrets.py file with the following information:
   1. An ArchivesSpace admin username (as_un = ""), password (as_pw = "")
   2. The URLs to your ArchivesSpace staging (as_api_stag = "") and production (as_api_prod = "") API instances
   3. Your ArchivesSpace's staging database credentials, including username (as_dbstag_un = ""), 
   password (as_dbstag_pw = ""), hostname (as_dbstag_host = ""), database name (as_dbstag_database = ""), and 
   port (as_dbstag_port = "")
4. Create a logs folder in your project's local directory for storing log files
5. Run the script as `python3 <name_of_script.py>`

### Script Arguments
Each script has its own parameters, most not requiring any arguments to run. However, you will want to take time to 
adjust the script to meet your own needs. For instance, you may want to set up a 'data' and/or 'reports' folder in your 
code's directory to store exported CSV's, Excel spreadsheets, or any other outputs that are generated from the script. 
See the [Overview](#Overview) section for more info on what each script does.

## Workflow
1. Select which script you would like to run
2. Run the script with the following command for python scripts: `python3 <name_of_script.py>`
   1. If there are arguments, make sure to fill out those arguments after the python script name. Most scripts just 
   need the information listed in secrets.py file created in the installation step above.
   2. If the script is not a python script, but an SQL statement, you can either download the SQL file or copy the code
   to your local SQL developer environment and run it there.

## Authors

- Corey Schmidt - IT Specialist at the Smithsonian Institution
- Mark Custer - Manager of the Community Applications and Archival Support Team at the Smithsonian Institution

## Acknowledgements

- ArchivesSpace community