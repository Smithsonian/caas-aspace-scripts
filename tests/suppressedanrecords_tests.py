# This script consists of unittests for suppress_edanrecords.py
import contextlib
import io
import unittest

from python_scripts.repeatable.suppress_edanrecords import *
from python_scripts.utilities import *

# Hardcode to dev env
env_file = find_dotenv('.env.dev')
load_dotenv(env_file)
local_aspace = ASpaceAPI(os.getenv('as_api'), os.getenv('as_un'), os.getenv('as_pw'))


class TestPrepareEDANData(unittest.TestCase):

    def test_jwt_encoding(self):
        """Test that a good jwt encoding is returned when calling prepare_edan_data()"""
        encoded_payload = prepare_edan_data()
        decoded_payload = jwt.decode(encoded_payload, os.getenv('edan_key'), algorithms="HS256")
        self.assertEqual(decoded_payload['iss'], os.getenv('edan_iss'))
        self.assertEqual(decoded_payload['jwtid'], os.getenv('edan_jwtid'))
        self.assertIsInstance(decoded_payload['iat'], int)

    def test_jwt_algorithm(self):
        """Test an alternative algorithm to see if exception is caught and passed"""
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            encoded_payload = prepare_edan_data(jwt_algorithm="&&&&&")
        self.assertTrue(
            r"""prepare_edan_data() error: An error occurred with the algorithm provided: Algorithm not supported""" in
            f.getvalue())
        self.assertIsNone(encoded_payload)


if __name__ == "__main__":
    unittest.main(verbosity=2)
