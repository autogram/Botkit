from pathlib import Path

import sys

import logzero

sys.path.append(Path(__file__).parent.parent.__str__())

logzero.LogFormatter.DEFAULT_FORMAT = (
    "%(color)s[%(levelname)1.1s %(asctime)s %(name)s %(module)s:%(lineno)d]%(end_color)s %("
    "message)s"
)
