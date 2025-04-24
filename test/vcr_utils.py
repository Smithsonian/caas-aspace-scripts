import inspect
import os

from vcr import VCR

vcr = VCR(
    filter_headers=[('X-ArchivesSpace-Session', '[REDACTED]')],
    filter_post_data_parameters=[('password', '[REDACTED]')],
    func_path_generator = lambda test: "test/fixtures/vcr_cassettes/{}/{}.yaml".format(os.path.basename(inspect.getfile(test)).replace('.py', ''), test.__name__)
)