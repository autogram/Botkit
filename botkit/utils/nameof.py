"""
https://github.com/alexmojaki/nameof

MIT License

Copyright (c) 2020 Alex Hall

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import dis
import inspect
from functools import lru_cache


def nameof(_):
    frame = inspect.currentframe().f_back
    return _nameof(frame.f_code, frame.f_lasti)


@lru_cache()
def _nameof(code, offset):
    instructions = list(dis.get_instructions(code))
    ((current_instruction_index, current_instruction),) = (
        (index, instruction)
        for index, instruction in enumerate(instructions)
        if instruction.offset == offset
    )
    # assert current_instruction.opname in ("CALL_FUNCTION", "CALL_METHOD"), "Did you call nameof in a weird way?"
    name_instruction = instructions[current_instruction_index - 1]
    # assert name_instruction.opname.startswith("LOAD_"), "Argument must be a variable or attribute"
    return name_instruction.argrepr


# def test():
#     assert nameof(dis) == "dis"
#     assert nameof(dis.get_instructions) == "get_instructions"
#     x = 1
#     assert nameof(x) == "x"
#
#     def foo():
#         assert nameof(x) == "x"
#
#         foo.nameof = nameof
#         assert foo.nameof(x) == "x"
#
#     foo()
#
#
# if __name__ == "__main__":
#     test()
