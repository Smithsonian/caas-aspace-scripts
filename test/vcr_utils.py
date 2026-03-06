import inspect
import json
import os

from vcr import VCR

def filter_json_response_body(fields, replacement='[REDACTED]'):
    """
    A callback function factory that creates a function to scrub 
    specific fields from a JSON response body.
    """
    def before_record_callback(response):
        string_body = response['body']['string'].decode('utf8')
        try:
            body = json.loads(string_body)
            
            for field in fields:
                if field in body:
                    body[field] = replacement
            
            response['body']['string'] = json.dumps(body).encode()
            return response
        # Response could be something other than JSON (e.g. xml export endpoints)
        except json.JSONDecodeError:
            return response
    
    return before_record_callback

vcr = VCR(
    before_record_response=filter_json_response_body(fields=['session']),
    filter_headers=[('X-ArchivesSpace-Session', '[REDACTED]')],
    filter_post_data_parameters=[('password', '[REDACTED]')],
    func_path_generator = lambda test: "test/fixtures/vcr_cassettes/{}/{}.yaml".format(os.path.basename(inspect.getfile(test)).replace('.py', ''), test.__name__)
)
