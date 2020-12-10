from pathlib import Path

import sys

from importlib.metadata import version

from ._settings import _BotkitSettings

try:
    __version__ = version(__name__)
except:
    __version__ = None

settings = _BotkitSettings()
botkit_settings = settings
