import contextlib

import difflib
import os
import re
import sys
import urllib.parse
from io import StringIO


def multiple_replace(repl, text, *flags):
    # Create a regular expression  from the dictionary keys
    regex = re.compile(r"(%s)" % "|".join(repl.keys()), *flags)
    return regex.sub(
        lambda mo: repl[
            [k for k in repl if re.search(k, mo.string[mo.start() : mo.end()], *flags)][0]
        ],
        text,
    )


@contextlib.contextmanager
def stdout_io(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old


def urlencode(text):
    return urllib.parse.quote(text)
