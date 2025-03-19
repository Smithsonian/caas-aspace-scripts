# Smithsonian ArchivesSpace Scripts
## Overview
A collection of Python/SQL scripts for data cleanup, management, and others related to the Smithsonian's ArchivesSpace 
implementation. Detailed descriptions of the various scripts can be found in the Wiki [Script Descriptions](https://github.com/Smithsonian/caas-aspace-scripts/wiki/Script-Descriptions) page. 
Also in the Wiki, you can find best practices for [logging](https://github.com/Smithsonian/caas-aspace-scripts/wiki/Logging), [testing](https://github.com/Smithsonian/caas-aspace-scripts/wiki/Testing), and [environment management](https://github.com/Smithsonian/caas-aspace-scripts/wiki/Environments).

## Getting Started

### Dependencies
Not every script requires every package as listed in the requirements.txt file. If you need to use a script, check the 
import statements at the top to see which specific packages are needed.

- [ArchivesSnake](https://github.com/archivesspace-labs/ArchivesSnake) - Library used for interacting with the ArchivesSpace API.
- [loguru](https://pypi.org/project/loguru/) - Library used for generating log files.
- [jsonlines](https://github.com/wbolster/jsonlines) - Library used for creating and appending to jsonl files for storage of JSON data.
- [python-dotenv](https://github.com/theskumar/python-dotenv) - Library used for writing environment variables for script info like credentials.

### Installation

1. Download the repository via cloning to your local IDE or using GitHub's Code button and Download as ZIP.
2. Run `pip install requirements.txt` or check the import statements for the script you want to run and install those 
packages.
3. Create dotenv files (dev, test, and prod) by following the [Environments](https://github.com/Smithsonian/caas-aspace-scripts/wiki/Environments) Wiki page.
4. Create a logs folder in your project's local directory for storing log files. More information about logging can be 
found in the [logging](https://github.com/Smithsonian/caas-aspace-scripts/wiki/Logging) Wiki page.
5. Run the script as `python3 <name_of_script.py>` followed by the appropriate arguments.
   1. -dR or --dry_run: This usually means print out the changed data, but do not post anything to ArchivesSpace.
   2. --version: The version of the script you are running.
   3. -h or --help: Print out information regarding the script, arguments, and argument parameters.

### Script Arguments
Each script has its own parameters, most not requiring any arguments to run. However, you will want to take time to 
adjust the script to meet your own needs. For instance, you may want to set up a 'data' and/or 'reports' folder in your 
code's test_data directory to store exported CSV's, Excel spreadsheets, or any other outputs that are generated from the
script. See the [Script Descriptions](https://github.com/Smithsonian/caas-aspace-scripts/wiki/Script-Descriptions) Wiki page for more info on what each script does.

## Workflow
1. Select which script you would like to run
2. Run the script with the following command for python scripts: `python3 <name_of_script.py>`
   1. If there are arguments, make sure to fill out those arguments after the python script name. Most scripts just 
   need the information listed in dotenv file created in the installation step above.
   2. If the script is not a python script, but an SQL statement, you can either download the SQL file or copy the code
   to your local SQL developer environment and run it there.

## Authors

- Mark Custer - Manager of the Community Applications and Archival Support Team at the Smithsonian Institution
- Corey Schmidt - IT Specialist at the Smithsonian Institution
- Lora Woodford - IT Specialist at the Smithsonian Institution

## Acknowledgements

- ArchivesSpace community