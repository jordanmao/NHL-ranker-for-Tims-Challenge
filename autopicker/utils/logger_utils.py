import json
import textwrap
import sys


def log_http_error(message, logger, response, http_err):
    logger.error(message + ':\n' + textwrap.indent(f'{http_err}\n{json.dumps(response.json(), indent=4)}', '\t'))
    sys.exit(http_err)
