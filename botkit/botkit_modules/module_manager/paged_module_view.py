from botkit.builders.htmlbuilder import HtmlBuilder
from botkit.builders.inlinemenubuilder import InlineMenuBuilder
from .view_models import ModuleInfosCollectionModel, ModuleInlineContext
from botkit.views.views import TextView


class PagedModuleView(TextView[ModuleInfosCollectionModel]):
    def render_body(self, builder: HtmlBuilder) -> None:
        for m in self.state.page_items:
            builder.bold(m.name)
            if not m.is_enabled:
                builder.spc().italic("(disabled)")

            builder.para

            if m.route_descriptions:
                builder.text("Routes: ")

                for r in m.route_descriptions:
                    builder.br().bullet()

                    if m.is_enabled:
                        builder.text(r)
                    else:
                        builder.strike(r)
            else:
                builder.text("No routes.")

            builder.para.br()

    def render_markup(self, builder: InlineMenuBuilder) -> None:
        row_builder = builder.rows[99]
        if self.state.has_previous_page:
            row_builder.action_button("⬅️", "page_back", self.state)
        row_builder.switch_inline_button(
            str(self.state.current_page_number), ModuleInlineContext("Module")
        )
        if self.state.has_next_page:
            row_builder.action_button("➡️", "page_forward", self.state)

        for n, info in enumerate(self.state.page_items):
            if info.route_descriptions and info.name not in "ModuleManagerModule":
                caption = HtmlBuilder()
                caption.text("Disable" if info.is_enabled else "Enable")
                caption.spc().text(info.name)
                builder.rows[n + 1].action_button(
                    caption.render(), "disable" if info.is_enabled else "enable", self.state,
                )
