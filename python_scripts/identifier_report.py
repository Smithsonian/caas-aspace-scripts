import csv
import json

from collections import namedtuple
from loguru import logger
from pathlib import Path


logger.remove()
log_path = Path(f'../logs', 'remove-missingtitles_{time:YYYY-MM-DD}.log')
logger.add(str(log_path), format="{time}-{level}: {message}")

def read_csv(missing_titles_csv):
    """
    Takes a csv input of ASpace objects with "Missing Title" in them - ran from SQL query - and returns a list of all
    dictionaries of all the objects metadata, including their identifiers, repository ID, ASpace ID, and URI

    Args:
        missing_titles_csv (str): filepath for the missing titles csv listing metadata for resources or archival
    objects

    Returns:
        missingtitle_objects (list): a list of URIs (dict) with "Missing Title" in their notes
    """
    missingtitle_objects = []
    try:
        open_csv = open(missing_titles_csv, 'r', encoding='UTF-8')
        missingtitle_objects = csv.DictReader(open_csv)
    except IOError as csverror:
        logger.error(f'ERROR reading csv file: {csverror}')
        print(f'ERROR reading csv file: {csverror}')
    else:
        return missingtitle_objects

testfile = read_csv(str(Path(f'../test_data/resource_accession_IDs_all.csv')))

unique_characters = {}

for row in testfile:
    new_row = json.loads(row['identifier'])
    for id_value in new_row:
        if id_value is not None and id_value.isalnum() is False:
            for character in id_value:
                if character not in unique_characters and character.isalnum() is False:
                    unique_characters[character] = 1
                elif character in unique_characters and character.isalnum() is False:
                    unique_characters[character] = unique_characters[character] + 1

print(unique_characters)
