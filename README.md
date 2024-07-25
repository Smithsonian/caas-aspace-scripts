# Smithsonian ArchivesSpace Scripts
## Overview
A collection of Python/SQL scripts for data cleanup, management, and others related to the Smithsonian's ArchivesSpace 
implementation.

### [update_znames.py](python_scripts/update_znames.py)

This script collects all users from ArchivesSpace, parses their usernames to separate any starting with 'z-' and
ending with '-expired-' into just the text in-between, then updates the username in ArchivesSpace with the new 
username

#### Requirements:
- ArchivesSnake
- ArchivesSpace username, password, API URL
- test_data/znames_testdata.py file, with `viewer_user = {ArchivesSpace viewer user metadata}` for testing. Can get this
from your API by getting a `client.get` request for the `viewer' user in your ArchivesSpace instance.

#### [znames_tests.py](tests/znames_tests.py)

Unittests for [znames_tests.py](tests/znames_tests.py)

## Getting Started

### Dependencies
Not every script requires every package as listed in the requirements.txt file. If you need to use a script, check the 
import statements at the top to see which specific packages are needed.

- [ArchivesSnake](https://github.com/archivesspace-labs/ArchivesSnake) - Library used for interacting with the 
ArchivesSpace API

### Installation

1. Download the repository via cloning to your local IDE or using GitHub's Code button and Download as ZIP
2. Run `pip install requirements.txt` or check the import statements for the script you want to run and install those 
packages
3. Create a secrets.py file with the following information:
   1. An ArchivesSpace admin username (as_un = ""), password (as_pw = "")
   2. The URLs to your ArchivesSpace staging (as_api_stag = "") and production (as_api = "") API instances
   3. Your ArchivesSpace's staging database credentials, including username (as_dbstag_un = ""), 
   password (as_dbstag_pw = ""), hostname (as_dbstag_host = ""), database name (as_dbstag_database = ""), and 
   port (as_dbstag_port = "")
4. Run the script as `python3 <name_of_script.py>`

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

## Author

- Corey Schmidt - IT Specialist at the Smithsonian Institution

## Acknowledgements

- ArchivesSpace community