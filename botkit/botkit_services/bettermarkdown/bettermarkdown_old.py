import random
import re
import traceback
from collections import OrderedDict

import lorem
import pws
from logzero import logger as log

from commons.core.helpers import mdformat

PARA_BR = r'(?:\n){,2}'
OPTIONAL_WHITESPACE = r'\s{,2}'


# region better markdown
BETTER_MARKDOWN = dict()
ORDERED = OrderedDict([
    (r'\b![\s(.*)\s](.*)\b', '[%](%r)'),  # list (-)
    (r'^(t) (.*)$', '% - %'),  # list (-)
    (rf'^> (.*)$', '▍ __%r__'),  # quote
    # (r'^(?:>>>|»>) (.*)$', '▍`%r`'),  # code??
    (r'^- (.*)$', '●  %'),  # list (-)
    (rf'^{OPTIONAL_WHITESPACE}\* (.*)$', '►  %'),  # list (*)
    (r'^\+ (.*)$', '➢ %'),  # list (+)
    (r'^(?i)o (.*)$', '▢  **%r**'),  # todoitem
    (r'^(?i)x (.*)$', '✓  __%r__'),  # done index
    (r'^! (.*)$', '✗ __%__'),  # aborted index
    (r'^(?i)oe (.*)$', '⚪️  **%r**'),  # todoitem emoji
    (r'^(?i)xe (.*)$', '✅  __%r__'),  # done index emoji
    (r'^!e (.*)$', '❌  __%__'),  # aborted index emoji
    (rf'{PARA_BR}^#\s(.*?)(?:\s*#)?${PARA_BR}', '\n\n\n⏩  **%r**\n\n'),  # h1
    (rf'{PARA_BR}^##\s(.*?)(?:\s*##)?${PARA_BR}', '\n\n➖ **%r** ➖\n\n'),  # h2
    (rf'{PARA_BR}^###\s(.*?)(?:\s*###)?${PARA_BR}', '\n\n〰  %  〰\n\n'),  # h3
    (r'^####\s(.*?)(?:\s*####)?$', '◾️ __%r__'),  # h4
    (r'^#####\s(.*?)(?:\s*#####)?$', '⚞ **%r** ⚟'),  # h5
    (r'^######\s(.*?)(?:\s*######)?$', '⚞ **%r** ⚟'),  # h6
    (fr'{PARA_BR}/{{5,}}{PARA_BR}', '\n\n`≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡`\n\n'),  # horizontal ruler
    (fr'{PARA_BR}={{5,}}{PARA_BR}', '\n\n`===========================`\n\n'),  # horizontal ruler
    (rf'^{PARA_BR}[-—]{{5,}}{PARA_BR}$', '\n\n`---------------------------`\n\n'),  # horizontal ruler
    (r'^say> (.*)$', '💬 %'),
    (r'()`%`', '💬 %'),
    # (r'#! (.*) !#', ''),
    (r'^(.*)\.{3}', '%…'),
    (r'^([0-9])*\.\s+(.*)$', lambda g: f"{mdformat.number_as_unicode(int(g[0]))}.  {g[1]}"),
    (r"<c\s(.*)\sc>", '```%r```'),
    (r"'''", '```'),
    (r'(?:(?<=\W)|^)-(.+?)-(?:(?=\W)|$)', (lambda g: mdformat.strikethrough(g[0]), re.DOTALL)),  # strikethrough
    (r'(?:(?<=\W)|^)#(.+?)#(?:(?=\W)|$)', (lambda g: mdformat.smallcaps(g[0]), re.DOTALL)),  # smallcaps
    # (r'^([0-9])*\. (.*)$', lambda g: mdformat.number_as_emoji(int(g[0])) + ' ' + g[1])
])
STATIC = {
    r'^\/r\/([a-zA-Z0-9]*)(?:(?=\W)|$)': 'https://www.reddit.com/r/%r',
    r'^(?i)<bat 1> (.*)$': '🤷🏼‍♂️  __%r__',
    r'^(?i)<bat 2> (.*)$': '🦇 __%r__',
    r'\blorem([0-9]?)\b': lambda g: '\n'.join(lorem.sentence() for _ in range(int(g[0]) if g[0] else 1)),
    r'^(.+)x([0-9]+)$': lambda g: (g[0].strip() + ' ') * int(g[1]),
    r'\?(?=\S)(.*?)(?<=\S)\?': lambda g: web_search(g),  # ?search for this?
    r'\[(.*?)\]\((.*?)\)': lambda g: full_search(g),
    r'___(.*)___': lambda g: ' '.join(g[0]),
    r'\bmoon\b': '🌚',
    r'»>': '>>>',
    r'^(?i)topkek$': '🔝🍪',
    r'^uw$': "you're welcome 😉",
    r'\bstronkk\b': "💪🏻😁☝🏻",
    r'\bkek\b': lambda _: random.choice(("kektarine 🍑🍎", "kektus 🌵")),
    r'<->': '↔',
    r'(—>|-->)': '→',
    r'shrug': '¯\_(ツ)_/¯',
    r'\?!': '‽',
    r'(?i)\booo\b': 'ಠ_ಠ',
    r'soon': '🔜',
    r':dash:': '―',
    r'1/2': '½',
    r'1/7': '⅐',
    r'1/9': '⅑',
    r'1/10': '⅒',
    r'1/3': '⅓',
    r'2/3': '⅔',
    r'1/5': '⅕',
    r'2/5': '⅖',
    r'3/5': '⅗',
    r'4/5': '⅘',
    r'1/6': '⅙',
    r'5/6': '⅚',
    r'1/8': '⅛',
    r'3/8': '⅜',
    r'5/8': '⅝',
    r'7/8': '⅞',
    r'\(Y\)': '👍🏻',
}
BETTER_MARKDOWN.update(ORDERED)
BETTER_MARKDOWN.update(STATIC)
# endregion

PLACEHOLDER = '%'
PLACEHOLDER_RAW = '%r'
BACKREF = r'\{counter}'
BACKREF_RAW = r'\r{counter}'
ESCAPE_NEGATIVE_LOOKBEHIND = r'(?<!\\)'


class _ReplacementCounter(object):
    """ Replaces consecutive % placeholders with \1, \2, … backreferences """

    def __init__(self):
        self.counter = 0

    def __call__(self, match):
        self.counter += 1

        # Account for escaped placeholders
        escaped = match.group(1)
        if escaped == '\\':
            return match.group(2)

        placeholder = match.group(2)
        if placeholder == PLACEHOLDER:
            return BACKREF.format(counter=self.counter)
        elif placeholder == PLACEHOLDER_RAW:
            return BACKREF_RAW.format(counter=self.counter)


def remove_formatting(value):
    return value.replace('```', '').replace('`', '').replace('**', '').replace('__', '')


def replace_aliases(text, replacements_dict):
    result = dict()
    for variable, output in replacements_dict.items():
        if isinstance(output, tuple):
            output = output[0]
        if not callable(output):
            replace_counter = _ReplacementCounter()
            output = re.sub(fr'(\\?)(%r?)', replace_counter, output)
        result[variable] = output

    for pattern, replacement in result.items():
        flags = re.MULTILINE
        if isinstance(replacement, tuple):
            replacement, elem_flags = replacement
            flags = flags | elem_flags
        if callable(replacement):
            text = re.sub(pattern, lambda g: replacement(g.groups()), text, flags=flags)
        else:
            try:
                def substitute(match):
                    if not match:
                        return replacement

                    def escape_or_replace(m):
                        try:
                            backreference_value = match.group(int(m.group(2)))
                        except:
                            raise ValueError(f"There is no capturing group defined in the pattern {pattern}, "
                                             f"but a backreference is used.")
                        if m.group(1) == 'r':
                            return remove_formatting(backreference_value)
                        return backreference_value

                    return re.sub(r'\\(r?)([0-9])', escape_or_replace, replacement)

                text = re.sub(pattern, substitute, text, flags=flags)
            except:
                traceback.print_exc()
    return text


def random_hello():
    return random.choice(['Hi!', 'Hi there!'])


def _search_bing(query):
    log.info(query)
    response = pws.Bing.search(query=query, num=1, country_code='en-us')
    link_result = response['results'][0]['link']
    log.info(f"Search results for \"{query}\": {response['results']}")
    return link_result


def web_search(g):
    query = g[0]
    try:
        return f"[{query}]({_search_bing(query)})"
    except:
        traceback.print_exc()
        return query


def full_search(g):
    text = g[0]
    query = g[1]

    if '.' in query:
        return f"[{text}]({query})"

    query += ' ' + text

    try:
        return f"[{text}]({_search_bing(query)})"
    except:
        traceback.print_exc()
        return text
