from botkit.builders.text.basetextbuilder import BaseTextBuilder
from botkit.builders.text.emoji import replace_aliases
from botkit.builders.text.mdformat import number_as_emoji


class IconographyBuilder(BaseTextBuilder):
    def emoji_spc(self):
        """ Renders the horizontal width of an emoji as two `en` whitespace characters (U+2002) """
        self.parts.append("	 	 ")
        return self

    def emojize(self, alias: str):
        self.parts.append(replace_aliases(alias))
        return self

    def bullet(self):
        self.parts.append("▪️")
        return self

    def number_as_emoji(self, num: int):
        self.parts.append(number_as_emoji(num))
        return self
