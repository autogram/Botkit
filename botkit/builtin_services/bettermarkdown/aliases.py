import re
from collections import OrderedDict
from typing import Pattern, Callable, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from parse import Match
else:
    Match = "Match"

PLACEHOLDER = "%"


class PlaceholderCounter(object):
    """ Replaces consecutive % placeholders with \1, \2, … backreferences """

    def __init__(self):
        self.counter = -1

    def __call__(self, match):
        self.counter += 1

        # Account for escaped placeholders
        escaped = match.group(1)
        if escaped == "\\":
            return match.group(2)

        # TODO: debug to see why sometimes it adds {2} instead of {0} (e.g. for "say> %")
        placeholder = match.group(2)
        if placeholder == PLACEHOLDER:
            return "{" + str(self.counter) + "}"


class Alias:
    def __init__(
        self,
        name: str,
        pattern: str or Pattern,
        render: Callable[[Match], str] or str,
        ignorecase: bool = True,
    ):
        self.name = name

        # flags = re.DOTALL
        # if ignorecase:
        #     flags = flags | re.IGNORECASE
        # self.pattern = re.compile(pattern, flags=flags)
        flags = 0
        if ignorecase:
            flags = re.IGNORECASE
        self.pattern = re.compile(pattern, flags=flags)

        if callable(render):
            self.render = render
        elif isinstance(render, str):
            self.render = re.sub(fr"(\\?)(%?)", PlaceholderCounter(), render)
        else:
            print(f"type {type(render)} unknown.")

    def output(self, m):
        if callable(self.render):
            return self.render(m)

        groups = m.groups()

        if groups:
            return self._render_default(groups)
        else:
            return self._render_default()

    def _render_default(self, groups: Tuple = None):
        assert isinstance(self.render, str)

        if groups:
            print(self.render)
            print(*groups)
            return self.render.format(*groups)
        else:
            return self.render

    def __repr__(self):
        return f"Alias({self.name}, {self.pattern}, render={self.render})"


INLINE = [  # numbered list
    Alias("elipsis", r"\.{3}", f"…")
    # emphasis = re.compile(
    #     r'^\b_((?:__|[^_])+?)_\b'  # _word_
    #     r'|'
    #     r'^\*((?:\*\*|[^\*])+?)\*(?!\*)'  # *word*
    # )
]
BLOCK = OrderedDict(
    [
        # (r'^(?i)o (.*)$', '▢  **%r**'),  # todoitem
        # (r'^(?i)x (.*)$', '✓  __%r__'),  # done index
        # (r'^! (.*)$', '✗ __%__'),  # aborted index
        # (r'^(?i)oe (.*)$', '⚪️  **%r**'),  # todoitem emoji
        # (r'^(?i)xe (.*)$', '✅  __%r__'),  # done index emoji
        # (r'^!e (.*)$', '❌  __%__'),  # aborted index emoji
        # (r'^say>? (.*)$', '💬 %'),
        # (r'()`%`', '💬 %'),
        # (r'^(.*)\.{3}', '%…'),
        # (r'^([0-9])*\.\sender+(.*)$', lambda g: f"{mdformat.number_as_unicode(int(g[0]))}.  {g[1]}"),
        # (r"<c\sender(.*)\sc>", '```%r```'),
        # (r"'''", '```'),
        ### Difficult ones:
        # (r'^(?:>>>|»>) (.*)$', '▍`%r`'),  # code??
        # (r'#! (.*) !#', ''),
        # (r'(?:(?<=\W)|^)-(.+?)-(?:(?=\W)|$)', (lambda g: mdformat.strikethrough(g[0]), re.DOTALL)),  # strikethrough
        # (r'(?:(?<=\W)|^)#(.+?)#(?:(?=\W)|$)', (lambda g: mdformat.smallcaps(g[0]), re.DOTALL)),  # smallcaps
        # (r'^([0-9])*\. (.*)$', lambda g: mdformat.number_as_emoji(int(g[0])) + ' ' + g[1])
    ]
)
