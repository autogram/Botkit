"""
__init__.py

Contains most of the Easy logic.

"""

import re


class Easy(object):
    """
    Easy.

    Makes Regular Expressions really, really easy.
    """

    def __init__(self):

        self.flags = ""
        self._literals = []
        self._groups_used = 0
        self.clear()

    def clear(self):
        """
        Reset the current state.
        """

        self._min = -1
        self._max = -1
        self._of = ""
        self._of_any = False
        self._of_group = -1
        self._from = ""
        self._not_from = ""
        self._like = ""
        self._either = ""
        self._reluctant = False
        self._capture = False

    def flush(self):
        """
        If there's anything in the state, add the current state to the stack and clear.

        Returns nothing.

        """

        if (
            self._of != ""
            or self._of_any
            or self._of_group > 0
            or self._from != ""
            or self._not_from != ""
            or self._like != ""
        ):
            capture_literal = "" if self._capture else "?:"
            quantity_literal = self.getQuantityLiteral()
            character_literal = self.getCharacterLiteral()
            reluctant_literal = "?" if self._reluctant else ""
            self._literals.append(
                "("
                + capture_literal
                + "(?:"
                + character_literal
                + ")"
                + quantity_literal
                + reluctant_literal
                + ")"
            )
            self.clear()

        return

    def getQuantityLiteral(self):
        """
        Gets the 'quantity' literal.

        Returns a string.
        """

        if self._min != -1:
            if self._max != -1:
                return "{" + str(self._min) + "," + str(self._max) + "}"
            return "{" + str(self._min) + ",}"
        else:
            return "{0," + str(self._max) + "}"

    def getCharacterLiteral(self):
        """
        Gets the 'character' literal.

        Returns a string.
        """
        if self._of != "":
            return str(self._of)

        if self._of_any:
            return "."

        if self._of_group > 0:
            return "\\" + str(self._of_group)

        if self._from != "":
            return "[" + str(self._from) + "]"

        if self._not_from != "":
            return "[^" + str(self._not_from) + "]"

        if self._like != "":
            return str(self._like)

    def getLiteral(self):
        """
        Flush, and return the joined literal.
        """
        self.flush()
        return "".join(self._literals)

    def combineGroupNumberingAndGetLiteral(self, regex):
        """

        """

        literal = self.incrementGroupNumbering(regex.getLiteral(), self._groups_used)
        self._groups_used = self._groups_used + regex._groups_used
        return literal

    def incrementGroupNumbering(self, literal, increment):
        """
        """
        if increment > 0:

            def repl(groupReference):
                groupNumber = int(groupReference[2:]) + increment
                return int(groupReference[0:2]) + groupNumber

            subbed = re.sub(r"/[^\\]\\\d+/g", repl, literal)
            return subbed
        return literal

    def addFlag(self, flag):
        """
        If we don't have the flag already, add it.
        """
        if self.flags.find(flag) == -1:
            self.flags = self.flags + flag
        return self

    def ignoreCase(self):
        """
        """
        self.addFlag("i")
        return self

    def multiLine(self):
        """
        """
        self.addFlag("m")
        return self

    def globalMatch(self):
        """
        Global matching.

        THIS DOES NOT WORK.

        TODO. FIX THIS.

        """
        self.addFlag("g")
        return self

    def startOfInput(self):
        """
        """
        self._literals.append("(?:^)")
        return self

    def startOfLine(self):
        """
        """
        self.multiLine()
        return self.startOfInput()

    def endOfInput(self):
        """
        """
        self.flush()
        self._literals.append("(?:$)")
        return self

    def endOfLine(self):
        """
        """
        self.multiLine()
        return self.endOfInput()

    def either(self, r):
        """
        """
        if type(r) == type(""):
            return self.eitherLike(Easy().exactly(1).of(r))
        else:
            self.eitherLike(r)

    def eitherLike(self, r):
        """
        """
        self.flush()
        self._either = self.combineGroupNumberingAndGetLiteral(r)
        return self

    def orr(self, r):
        """
        I hate the naming of this, but it chokes with the natural 'or'.

        """
        if type(r) == type(""):
            return self.or_like(Easy().exactly(1).of(r))
        else:
            return self.or_like(r)

    def or_like(self, r):
        """
        """
        either = self._either
        orr = self.combineGroupNumberingAndGetLiteral(r)
        if either == "":
            lastOr = self._literals[-1]
            lastOr = lastOr[:-1]
            self._literals[-1] = lastOr
            self._literals.append("|(?:" + orr + "))")
        else:
            self._literals.append("(?:(?:" + either + ")|(?:" + orr + "))")
        self.clear()
        return self

    def neither(self, r):
        if type(r) == type(""):
            return self.not_ahead(Easy().exactly(1).of(r))
        return self.not_ahead(r)

    def nor(self, r):
        if this._min == 0 and self._of_any:
            self._min = -1
            self._of_any = False
        self.neither(r)
        return self.min(0).ofAny()

    def exactly(self, n):
        self.flush()
        self._min = n
        self._max = n
        return self

    def min(self, n):
        self.flush()
        self._min = n
        return self

    def max(self, n):
        self.flush()
        self._max = n
        return self

    def of(self, s):
        self._of = self._sanitize(s)
        return self

    def ofAny(self):
        self._of_any = True
        return self

    def ofGroup(self, n):
        self._of_group = n
        return self

    def From(self, s):
        self._from = self._sanitize(s.join(""))
        return self

    def notFrom(self, s):
        self._notFrom = self._sanitize(s.join(""))
        return self

    def like(self, r):
        self._like = self.combineGroupNumberingAndGetLiteral(r)
        return self

    def reluctantly(self):
        self._reluctant = True
        return self

    def ahead(self, r):
        self.flush()
        self._literals.append("(?=" + self.combineGroupNumberingAndGetLiteral(r) + ")")
        return self

    def not_ahead(self, r):
        self.flush()
        self._literals.append("(?!" + self.combineGroupNumberingAndGetLiteral(r) + ")")
        return self

    def as_group(self):
        self._capture = True
        self._groups_used = self._groups_used + 1
        return self

    def then(self, s):
        return self.exactly(1).of(s)

    def find(self, s):
        return self.then(s)

    def some(self, s):
        return self.min(1).From(s)

    def maybeSome(self, s):
        return self.min(0).From(s)

    def maybe(self, s):
        return self.max(1).of(s)

    def something(self):
        return self.min(1).ofAny()

    def anything(self):
        return self.min(0).ofAny()

    def anything_but(self, s):
        if len(s) == 1:
            return self.min(0).notFrom([s])
        self.not_ahead(Easy().exactly(1).of(s))
        return self.min(0).ofAny()

    def any(self):
        return self.exactly(1).ofAny()

    def line_break(self):
        self.flush()
        self._literals.append("(?:\\r\\n|\\r|\\n)")
        return self

    def line_breaks(self):
        return self.like(Easy().line_break())

    def whitespace(self):
        if self._min == -1 and self._max == -1:
            self.flush()
            self._literals.append("(?:\\s")
            return self
        self._like = "\\s"
        return self

    def non_whitespace(self):
        if self._min == -1 and self._max == -1:
            self.flush()
            self._literals.append("(?:\\S)")
            return self
        self._like = "\\S"
        return self

    def tab(self):
        self.flush()
        self._literals.append("(?:\\t)")
        return self

    def tabs(self):
        return self.like(Easy().tab())

    def digit(self):
        self.flush()
        self._literals.append("(?:\\d)")
        return self

    def non_digit(self):
        self.flush()
        self._literals.append("(?:\\D)")
        return self

    def digits(self):
        return self.like(Easy().digit())

    def non_digits(self):
        return self.like(Easy().non_digit())

    def letter(self):
        self.exactly(1)
        self._notFrom = "A-Za-z"
        return self

    def non_letter(self):
        self.exactly(1)
        self._notFrom = "A-Za-z"
        return self

    def lower_char(self):
        self.exactly(1)
        self._from = "a-z"
        return self

    def lower_chats(self):
        self._from = "a-z"
        return self

    def upper_letter(self):
        self.exactly(1)
        self._from = "A-Z"
        return self

    def upper_letters(self):
        self._from = "A-Z"
        return self

    def append(self, r):
        self.exactly(1)
        self._like = self.combineGroupNumberingAndGetLiteral(r)
        return self

    def optional(self, r):
        self.max(1)
        self._like = self.combineGroupNumberingAndGetLiteral(r)
        return self

    ##
    #  re usage and convenience methods.
    ##

    def _sanitize(self, s):
        """
        Escape special chars.

        I'm not sure if this is a satisfactory approach compared to the original: "/([.*+?^=!:${}()|\[\]\/\\])/g

        """
        return re.escape(s)

    def get_regex(self):
        self.flush()
        joined = "".join(self._literals)

        if self.flags != "":
            flags = 0
            if "m" in self.flags:
                flags |= re.M
            if "i" in self.flags:
                flags |= re.I
            compiled = re.compile(joined, flags)
        else:
            compiled = re.compile(joined)
        return compiled

    def test(self, test):
        """
        For an Easy, given a test string, does this findall == 1?
        """
        reg = self.get_regex()
        all_results = re.findall(reg, test)
        if len(all_results) == 0:
            return False
        else:
            return True

    def match(self, match):
        """
        Convenience wrapper for re's match function.
        """
        reg = self.get_regex()
        return re.match(reg, match)

    def search(self, search):
        """
        Convenience wrapper for re's search function.
        """
        reg = self.get_regex()
        return re.search(reg, search)
