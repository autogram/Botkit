from pathlib import Path

import sys

from importlib.metadata import version

try:
    __version__ = version(__name__)
except:
    __version__ = None

