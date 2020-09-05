from botkit.builders.htmlbuilder import HtmlBuilder
from botkit.builders.inlinemenubuilder import InlineMenuBuilder
from .view_models import ModuleInfosCollectionModel, ModuleInlineContext
from botkit.views.views import TextView


class PagedModuleView(TextView[ModuleInfosCollectionModel]):
    def render_body(self, builder: HtmlBuilder) -> None:
        for m in self.state.page_items:
            builder.bold(m.name)
            if not m.is_active:
                builder.spc().italic("(deactivated)")

            builder.enforce_min_width(70)

            if m.route_descriptions:
                builder.text("Routes: ")

                for r in m.route_descriptions:
                    builder.br().list_item("")

                    if m.is_active:
                        builder.text(r)
                    else:
                        builder.strike(r)
            else:
                builder.text("No routes.")

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
            if info.name not in "ModuleManagerModule":
                caption = HtmlBuilder()
                caption.text("Deactivate" if info.is_active else "Activate")
                caption.spc().text(info.name)
                builder.rows[n + 1].action_button(
                    caption.render(), "deactivate" if info.is_active else "activate", self.state,
                )
