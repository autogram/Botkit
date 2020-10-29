"""
This type stub file was generated by pyright.
"""

class AlreadyConfigured(Exception):
    ...


class ConfigurationError(Exception):
    ...


class NotConfigured(Exception):
    ...


class UnknownDependency(TypeError):
    ...


class UnknownScope(TypeError):
    ...


class CallError(TypeError):
    ...


class UnknownConfigVariable(ConfigurationError):
    ...

