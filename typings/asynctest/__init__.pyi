"""
This type stub file was generated by pyright.
"""

import unittest
from unittest import *
from .case import *
from .mock import *
from ._fail_on import *
from .helpers import *
from .selector import *

"""
The package asynctest is built on top of the standard :mod:`unittest` module
and cuts down boilerplate code when testing libraries for :mod:`asyncio`.

asynctest imports the standard unittest package, overrides some of its features
and adds new ones. A test author can import asynctest in place of
:mod:`unittest` safely.

It is divided in submodules, but they are all imported at the top level,
so :class:`asynctest.case.TestCase` is equivalent to :class:`asynctest.TestCase`.

Currently, asynctest targets the "selector" model. Hence, some features will
not (yet) work with Windows' proactor.
"""
