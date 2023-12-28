import json
import textwrap
import sys
from logging import Logger
from requests import Response
from requests.exceptions import HTTPError


def log_http_error(message: str, logger: Logger, response: Response, http_err: HTTPError) -> None:
    logger.error(message + ':\n' + textwrap.indent(f'{http_err}\n{json.dumps(response.json(), indent=4)}', '\t'))
    sys.exit(http_err)
