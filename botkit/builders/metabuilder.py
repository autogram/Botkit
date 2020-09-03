class MetaBuilder(object):
    def __init__(self):
        self.description = None
        self.title = None

    @property
    def is_dirty(self) -> bool:
        return self.description or self.title
