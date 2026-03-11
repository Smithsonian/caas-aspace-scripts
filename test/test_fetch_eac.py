# This script consists of unittests for shared fetch_eac.py
import contextlib
import io
import os
import shutil
import unittest

from test.vcr_utils import vcr
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
from python_scripts.repeatable.fetch_eac import *

@vcr.use_cassette()
def setUpModule():
    # Hardcode to dev env
    env_file = find_dotenv('.env.dev')
    load_dotenv(env_file)
    global local_aspace
    local_aspace = ASpaceAPI(os.getenv('as_api'), os.getenv('as_un'), os.getenv('as_pw'))

class TestMakeOrCreatePath(unittest.TestCase):

    def tearDown(self):
        if os.path.exists('./test/fixtures/output'):
            shutil.rmtree('./test/fixtures/output')

    def test_make_or_create_file_path(self):
        """Tests finding or creating output directory"""
        output_path = Path('./test/fixtures/output')
        self.assertFalse(output_path.exists(), f"File should not exist: {output_path}")

        sample_row = {'repo_id': '2', 'agent_type': 'corporate_entities', 'agent_id': '3'}
        eac_file = make_or_create_file_path(output_path, sample_row)

        # We've created our output dir and file
        self.assertTrue(output_path.exists())
        self.assertEqual(eac_file, f'{output_path}/corporate_entities_3.xml')

class TestGetEac(unittest.TestCase):
    
    @vcr.use_cassette
    def test_get_eac(self):
        """Tests getting single EAC"""
        sample_row = {'repo_id': '2', 'agent_type': 'corporate_entities', 'agent_id': '3'}
        eac = get_eac(local_aspace, sample_row)
        self.assertIn('<eac-cpf', eac)
        self.assertIn('Primary 1', eac)
    
    @vcr.use_cassette
    def test_get_missing_eac(self):
        """Tests attempting to get an EAC that doesn't exist"""
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            sample_row = {'repo_id': '2', 'agent_type': 'corporate_entities', 'agent_id': '30'}
            get_eac(local_aspace, sample_row)
        self.assertTrue(r"""Failed to retrieve '/repositories/2/archival_contexts/corporate_entities/30.xml'""" in f.getvalue())
        self.assertTrue(r"""AgentCorporateEntity not found""" in f.getvalue())

if __name__ == "__main__":
    unittest.main(verbosity=2)