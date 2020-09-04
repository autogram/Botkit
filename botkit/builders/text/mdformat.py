MAX_LINE_CHARACTERS = 31


def smallcaps(text):
    SMALLCAPS_CHARS = "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"
    lowercase_ord = 96
    uppercase_ord = 64

    result = ""
    for i in text:
        index = ord(i)
        if 122 >= index >= 97:
            result += SMALLCAPS_CHARS[index - lowercase_ord - 1]
        elif 90 >= index >= 65:
            result += SMALLCAPS_CHARS[index - uppercase_ord - 1]
        elif index == 32:
            result += " "

    return result


def strikethrough(text: str):
    SPEC = "̶"
    return "".join([x + SPEC if x != " " else " " for x in text])


UNICODE_NUMBERS = "➊ ➋ ➌ ➍ ➎ ➏ ➐ ➑ ➒ ➓"


def number_as_unicode(n):
    if n not in range(1, 10):
        raise ValueError("Sorry, can't do anything with this number.")

    return UNICODE_NUMBERS[int(n) * 2 - 2]


def centered(text):
    result = "\n".join([line.center(MAX_LINE_CHARACTERS) for line in text.splitlines()])
    return result


# def success(text):
#     return '{} {}'.format(Emoji.WHITE_HEAVY_CHECK_MARK, text, hide_keyboard=True)
#
#
# def love(text):
#     return '💖 {}'.format(text, hide_keyboard=True)
#
#
# def failure(text):
#     return '{} {}'.format(Emoji.CROSS_MARK, text)
#
#
# def action_hint(text):
#     return '💬 {}'.format(text)
#
#
# def none_action(text):
#     return '{} {}'.format(Emoji.NEGATIVE_SQUARED_CROSS_MARK, text)
