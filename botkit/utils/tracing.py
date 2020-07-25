import inspect


def get_caller_frame_info() -> inspect.FrameInfo:
    """
    Use `get_caller_frame_info()[3]` for the name of the calling function.
    """
    curframe = inspect.currentframe()
    calframe = inspect.getouterframes(curframe, 2)
    return calframe[2]

