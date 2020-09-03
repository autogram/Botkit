from pyrogram.types import InlineKeyboardButton

from botkit.inlinequeries.contexts import IInlineModeContext, DefaultInlineModeContext


def switch_inline_button(
    caption: str = "Try me inline!",
    in_context: IInlineModeContext = DefaultInlineModeContext,
    current_chat: bool = True,
) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        caption,
        **{
            "switch_inline_query" + "_current_chat"
            if current_chat
            else "": in_context.format_query()
        },
    )
