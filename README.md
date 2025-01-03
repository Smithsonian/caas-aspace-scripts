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
  - [jsonlines](https://github.com/wbolster/jsonlines)
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


### [new_subjects.py](python_scripts/new_subjects.py)
This script creates new subjects from a provided CSV.  It is currently customized to support the needs of NMAI, but
this hardcoded NMAI metadata can be changed/updated in the future.

#### Requirements:
- ArchivesSnake
- Environment-based ArchivesSpace username, password, API URL in a .env.{environment} file:
  - On your local:
    1. Create a new `.env.dev` file containing local credentials
    2. `export ENV=dev`
    3. Run script
  - On test:
    1. Create a new `.env.test` file containing test credentials
    2. `export ENV=test`
    3. Run script
  - On prod:
    1. Create a new `.env.prod` file containing prod credentials
    2. `export ENV=prod`
    3. CAREFULLY run script
- logs directory for storing local log files

#### [newsubjects_tests.py](tests/newsubjects_tests.py)

Unittests for [newsubjects_tests.py](tests/newsubjects_tests.py)

#### Requirements:
- test_data/subjects_testdata.py file, containing the following:
  - `test_new_subject_metadata = {JSON representation of a new subject}` for testing.
  - `duplicate_new_subject = test_new_subject_metadata` ensures we can count on `duplicate_new_subject` to produce a not
  unique error during testing.
- test_data/newsubjects_testdata.csv - a csv file of new subjects to be created, containing:
  - new_title
  - new_scope_note
  - new_EMu_ID


### [update_subjects.py](python_scripts/update_subjects.py)
This script updates existing ArchivesSpace subjects from a provided CSV.  It is currently customized to support the 
needs of NMAI, but can be changed/updated in the future.

#### Requirements:
- ArchivesSnake
- Environment-based ArchivesSpace username, password, API URL in a .env.{environment} file:
  - On your local:
    1. Create a new `.env.dev` file containing local credentials
    2. `export ENV=dev`
    3. Run script
  - On test:
    1. Create a new `.env.test` file containing test credentials
    2. `export ENV=test`
    3. Run script
  - On prod:
    1. Create a new `.env.prod` file containing prod credentials
    2. `export ENV=prod`
    3. CAREFULLY run script
- logs directory for storing local log files

#### [updatesubjects_tests.py](tests/updatesubjects_tests.py)

Unittests for [updatesubjects_tests.py](tests/updatesubjects_tests.py)

#### Requirements:
- test_data/subjects_testdata.py file, containing the following:
  - `test_update_subject_metadata = {JSON representation of an existing subject}` for testing.  If `newsubjects_tests.py` has
    been run previously, you can use one of the subjects created by that test.
- test_data/newsubjects_testdata.csv - a csv file of changes to be made to an existing subject, containing:
  - aspace_subject_id - id of the subject to update, this can match that in test_data/subjects_testdata.py
  - new_title
  - new_scope_note
  - new_EMu_ID


### [merge_subjects.py](python_scripts/merge_subjects.py)
This script creates new subjects from a provided CSV.  It is currently customized to support the needs of NMAI, but
this hardcoded NMAI metadata can be changed/updated in the future.

#### Requirements:
- ArchivesSnake
- Environment-based ArchivesSpace username, password, API URL in a .env.{environment} file:
  - On your local:
    1. Create a new `.env.dev` file containing local credentials
    2. `export ENV=dev`
    3. Run script
  - On test:
    1. Create a new `.env.test` file containing test credentials
    2. `export ENV=test`
    3. Run script
  - On prod:
    1. Create a new `.env.prod` file containing prod credentials
    2. `export ENV=prod`
    3. CAREFULLY run script
- logs directory for storing local log files

#### [mergesubjects_tests.py](tests/mergesubjects_tests.py)

Unittests for [mergesubjects_tests.py](tests/mergesubjects_tests.py)

#### Requirements:
- test_data/subjects_testdata.py file, containing the following:
  - `test_merge_subject_destination = {JSON representation of an existing subject that will survive the merge}` for testing.  
    If `newsubjects_tests.py` has been run previously, you can use one of the subjects created by that test.
  - `test_merge_subject_candidate = {JSON representation of an existing subject that will be removed during the merge}` for testing.  
    If `newsubjects_tests.py` has been run previously, you can use one of the subjects created by that test.
- test_data/mergesubjects_testdata.csv - a csv file of subjects to be merged, containing:
  - aspace_subject_id - id of the merge destination/subject to be retained. If newsubjects_tests.py previously run, this can be
    one of the subjects created by those tests.
  - title - title of the merge destination/subject to be retained.  The title must match the existing subject with the above id.
  - aspace_subject_id2 - id of the merge candidate/subject to be removed. If newsubjects_tests.py previously run, this can be
    one of the subjects created by those tests.
  - Merge into - title of the merge candidate/subject to be removed.  The title must match the existing subject with the above id.


## Getting Started

### Dependencies
Not every script requires every package as listed in the requirements.txt file. If you need to use a script, check the 
import statements at the top to see which specific packages are needed.

- [ArchivesSnake](https://github.com/archivesspace-labs/ArchivesSnake) - Library used for interacting with the 
ArchivesSpace API
- [loguru](https://pypi.org/project/loguru/) - Library used for generating log files
- [jsonlines](https://github.com/wbolster/jsonlines) - Library used for creating and appending to jsonl files for 
storage of JSON data
- [python-dotenv](https://github.com/theskumar/python-dotenv) - Library used for writing environment variables for 
script info like credentials

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

- Mark Custer - Manager of the Community Applications and Archival Support Team at the Smithsonian Institution
- Corey Schmidt - IT Specialist at the Smithsonian Institution
- Lora Woodford - IT Specialist at the Smithsonian Institution

## Acknowledgements

- ArchivesSpace community