from injector import Scope, ScopeDecorator


class PerUpdateScope(Scope):
    def get(self, key, provider):
        return provider


per_update = ScopeDecorator(PerUpdateScope)
