from pathlib import Path

import sys

from importlib.metadata import version

try:
    __version__ = version(__name__)
except:
    __version__ = None


# TODO: is this necessary?
sys.path.append(Path(__file__).parent.parent.__str__())
