from abc import abstractmethod
from typing import Any, Union

from botkit.builders.htmlbuilder import HtmlBuilder
from botkit.builders.inlinemenubuilder import InlineMenuBuilder
from botkit.builders.quizbuilder import QuizBuilder
from botkit.utils.typed_callable import TypedCallable
from botkit.views.base import (
    IRegisterable,
    InlineResultViewBase,
    ModelViewBase,
    RenderMarkupBase,
    RenderedMessage,
    RenderedMessageMarkup,
    RenderedPollMessage,
    TState,
)


class MessageViewBase(InlineResultViewBase[TState], RenderMarkupBase):
    def render(self) -> RenderedMessage:
        rendered = super(MessageViewBase, self).render()

        markup = _render_message_markup(self)
        rendered.reply_markup = markup.reply_markup
        rendered.inline_buttons = markup.inline_buttons

        return rendered


class TextView(MessageViewBase[TState], RenderMarkupBase):
    @abstractmethod
    def render_body(self, builder: HtmlBuilder) -> None:
        pass

    def render(self) -> RenderedMessage:
        rendered = super(TextView, self).render()

        builder = HtmlBuilder()
        self.render_body(builder)
        rendered.text = builder.render()

        return rendered


class MediaView(MessageViewBase[TState]):
    def __init__(self, state: TState):
        super().__init__(state)

    @abstractmethod
    def get_media(self) -> Any:
        pass

    @abstractmethod  # TODO: could be optional, but better enforce every photo to have a caption?
    def render_caption(self, builder: HtmlBuilder) -> None:
        pass

    def render(self) -> RenderedMessage:
        rendered = super().render()
        rendered.media = self.get_media()

        builder = HtmlBuilder()
        self.render_caption(builder)
        rendered.caption = builder.render()

        return rendered


class StickerView(MessageViewBase[TState]):
    @abstractmethod
    def get_sticker(self) -> str:
        pass

    def render(self) -> RenderedMessage:
        rendered = super().render()
        rendered.sticker = self.get_sticker()
        return rendered


class PollBuilder:
    pass


class PollView(ModelViewBase[TState], IRegisterable, RenderMarkupBase):
    def __init__(self, state: TState):
        raise NotImplementedError("Only QuizView is implemented so far")
        super().__init__(state)

    @abstractmethod
    def render_poll(self, builder: PollBuilder) -> None:
        pass

    def render(self) -> RenderedPollMessage:
        markup = _render_message_markup(self)

        typed_render = TypedCallable(self.render_poll)

        builder = QuizBuilder()
        self.render_poll(builder)

        return RenderedPollMessage(
            reply_markup=markup.reply_markup,
            inline_buttons=markup.inline_buttons,
            **builder.render(),
        )


class QuizView(ModelViewBase, IRegisterable, RenderMarkupBase):
    @abstractmethod
    def render_quiz(self, builder: QuizBuilder) -> None:
        ...

    def render(self) -> RenderedPollMessage:
        markup = _render_message_markup(self)

        builder = QuizBuilder()
        self.render_quiz(builder)

        return RenderedPollMessage(
            reply_markup=markup.reply_markup,
            inline_buttons=markup.inline_buttons,
            **builder.render(),
        )


def _render_message_markup(obj: Union[ModelViewBase, RenderMarkupBase]) -> RenderedMessageMarkup:
    rendered = RenderedMessageMarkup()

    inspected_render = TypedCallable(obj.render_markup)

    if inspected_render.num_parameters > 1:
        raise ValueError(f"Too many parameters for {inspected_render.name}")

    elif inspected_render.num_parameters == 1:
        menu_builder = InlineMenuBuilder(obj.state)
        obj.render_markup(menu_builder)
        buttons = menu_builder.render()
        if not buttons or not buttons[0]:
            buttons = None

        rendered.inline_buttons = buttons

    else:
        rendered.reply_markup = obj.render_markup()

    return rendered
