from typing import List
from uuid import uuid4

from mistune import InlineLexer, InlineGrammar

from commons.coreservices.bettermarkdown.aliases import Alias, INLINE, BLOCK

for k, v in BLOCK.items():
    INLINE.append(
        Alias(str(uuid4()), k, v)
    )


class InlineRulesContainer(InlineGrammar):
    def __init__(self, aliases: List[Alias]):
        for a in aliases:
            setattr(self, a.name, a.pattern)


class BetterMarkdownLexer(InlineLexer):

    def __init__(self, renderer, aliases: List[Alias], **kwargs):
        self.aliases = aliases

        rules_container = InlineRulesContainer(aliases)

        for a in self.aliases:
            print(f'Adding {a} as rule `output_{a.name}`')

            setattr(self, f'output_{a.name}', a.output)
            self.default_rules.insert(0, a.name)

        super().__init__(renderer, rules_container, **kwargs)
