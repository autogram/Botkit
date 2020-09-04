# from typing import Optional
#
# from botkit.inlinequeries.contexts import PrefixBasedInlineModeContext
#
#
# def parse(text: str, prefix: str, delimiter: Optional[str] = None):
#     ctx = PrefixBasedInlineModeContext(prefix, delimiter=delimiter or ": ")
#     return ctx.parse_input(text)
#
#
# def fmt(remove_trigger_setting: str, prefix: str, delimiter: Optional[str] = None):
#     ctx = PrefixBasedInlineModeContext(prefix, delimiter=delimiter or ": ")
#     return ctx.format_query(remove_trigger_setting)
#
#
# # region parse_input tests
#
#
# def test_happy_path():
#     assert parse("henlo: fren", "henlo", ": ") == "fren"
#
#
# def test_newline_chars():
#     assert parse("henlo:\nfren\nand\nbois", "henlo") == "fren\nand\nbois"
#
#
# def test_case_sensitivity():
#     assert parse("hEnLo: frEn", "HENLO") == "frEn"
#
#
# def test_no_spaces():
#     assert parse("henlo:fren", "henlo:") == "fren"
#
#
# def test_whitespace():
#     assert parse("henlo:  fren  ", "henlo  : ") == "fren"
#     assert parse("henlo :  fren  ", "henlo", ":") == "fren"
#
#
# def test_custom_delimiter():
#     assert parse("henlo +  fren  ", "henlo", "+") == "fren"
#
#
# def test_whitespace_as_delimiter():
#     assert parse("prefix test", "prefix", " ") == "test"
#
#
# # endregion
#
# # region format_query tests
#
#
# def test_format_input_happy_path():
#     assert fmt(remove_trigger_setting="test", prefix="lala", delimiter=": ") == "lala: test"
#
#
# def test_format_input_delimiter_in_prefix():
#     assert fmt(remove_trigger_setting=" test ", prefix="lala: ", delimiter=": ") == "lala: test"
#
#
# def test_format_input_whitespace():
#     assert fmt(remove_trigger_setting=" test ", prefix="lala", delimiter=": ") == "lala: test"
#
#
# def test_format_input_newlines():
#     assert fmt(remove_trigger_setting=" a\nb\nc ", prefix="lala", delimiter=": ") == "lala: a\nb\nc"
#
#
# # endregion
