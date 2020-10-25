from abc import abstractmethod
from typing import Any, Union, cast

from haps import Container, Inject

from botkit.builders import CallbackBuilder
from botkit.builders.htmlbuilder import HtmlBuilder
from botkit.builders.menubuilder import MenuBuilder
from botkit.builders.quizbuilder import QuizBuilder
from botkit.persistence.callback_store import ICallbackStore
from botkit.settings import botkit_settings
from botkit.utils.typed_callable import TypedCallable
from botkit.views.base import (
    IRegisterable,
    InlineResultViewBase,
    ModelViewBase,
    RenderMarkupBase,
)
from botkit.views.types import TViewState
from botkit.views.rendered_messages import (
    RenderedMediaMessage,
    RenderedMessage,
    RenderedMessageMarkup,
    RenderedPollMessage,
    RenderedTextMessage,
)

# TODO: Now that also HTML views require state it gets harder and harder to justify having these classes...


class MessageViewBase(InlineResultViewBase[TViewState], RenderMarkupBase):
    def render(self) -> RenderedMessage:
        rendered = super(MessageViewBase, self).render()

        markup = _render_message_markup(self)
        rendered.reply_markup = markup.reply_markup
        rendered.inline_buttons = markup.inline_buttons

        return rendered


class TextView(MessageViewBase[TViewState], RenderMarkupBase):
    _callback_store: ICallbackStore = Inject(botkit_settings.callback_manager_qualifier)

    @abstractmethod
    def render_body(self, builder: HtmlBuilder) -> None:
        pass

    def render(self) -> RenderedTextMessage:
        rendered = super(TextView, self).render()
        rendered.__class__ = RenderedTextMessage
        rendered = cast(RenderedTextMessage, rendered)

        builder = HtmlBuilder(CallbackBuilder(self.state, self._callback_store))
        self.render_body(builder)
        rendered.text = builder.render_html()

        return rendered


class MediaView(MessageViewBase[TViewState]):
    _callback_store: ICallbackStore = Inject(botkit_settings.callback_manager_qualifier)

    def __init__(self, state: TViewState):
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

        builder = HtmlBuilder(CallbackBuilder(self.state, self._callback_store))
        self.render_caption(builder)
        rendered.caption = builder.render_html()

        return rendered


class StickerView(MessageViewBase[TViewState]):
    @abstractmethod
    def get_sticker(self) -> str:
        pass

    def render(self) -> RenderedMessage:
        rendered = super().render()
        rendered.sticker = self.get_sticker()
        return rendered


class PollBuilder:
    pass


class PollView(ModelViewBase[TViewState], IRegisterable, RenderMarkupBase):
    def __init__(self, state: TViewState):
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
        menu_builder = MenuBuilder(
            CallbackBuilder(
                obj.state,
                Container().get_object(ICallbackStore, botkit_settings.callback_manager_qualifier),
            )
        )
        obj.render_markup(menu_builder)
        buttons = menu_builder.render()
        if not buttons or not buttons[0]:
            buttons = None

        rendered.inline_buttons = buttons

    else:
        rendered.reply_markup = obj.render_markup()

    return rendered
