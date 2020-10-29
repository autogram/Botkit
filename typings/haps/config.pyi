"""
This type stub file was generated by pyright.
"""

from types import FunctionType
from typing import Any, Optional, Type

_NONE = object()
class Configuration:
    """
    Configuration container, a simple object to manage application config
    variables.
    Variables can be set manually, from the environment, or resolved
    via custom function.

    """
    _lock = ...
    _instance: Configuration = ...
    def __new__(cls, *args, **kwargs) -> Configuration:
        ...
    
    def get_var(self, var_name: str, default: Optional[Any] = ...) -> Any:
        """
        Get a config variable. If a variable is not set, a resolver is not
        set, and no default is given
        :class:`~haps.exceptions.UnknownConfigVariable` is raised.

        :param var_name: Name of variable
        :param default: Default value
        :return: Value of config variable
        """
        ...
    
    @classmethod
    def resolver(cls, var_name: str) -> FunctionType:
        """
        Variable resolver decorator. Function or method decorated with it is
        used to resolve the config variable.

        .. note::
            Variable is resolved only once.
            Next gets are returned from the cache.

        :param var_name: Variable name
        :return: Function decorator
        """
        ...
    
    @classmethod
    def env_resolver(cls, var_name: str, env_name: str = ..., default: Any = ...) -> Configuration:
        """
        Method for configuring environment resolver.

        :param var_name: Variable name
        :param env_name: An optional environment variable name. If not set\
            haps looks for `HAPS_var_name`
        :param default: Default value for variable. If it's a callable,\
            it is called before return. If not provided\
            :class:`~haps.exceptions.UnknownConfigVariable` is raised
        :return: :class:`~haps.config.Configuration` instance for easy\
                  chaining
        """
        ...
    
    @classmethod
    def set(cls, var_name: str, value: Any) -> Configuration:
        """
        Set the variable

        :param var_name: Variable name
        :param value: Value of variable
        :return: :class:`~haps.config.Configuration` instance for easy\
                  chaining
        """
        ...
    


class Config:
    """
    Descriptor providing config variables as a class properties.

    .. code-block:: python

        class SomeClass:
            my_var: VarType = Config()
            custom_property_name: VarType = Config('var_name')

    """
    def __init__(self, var_name: str = ..., default=...) -> None:
        """

        :param var_name: An optional variable name. If not set the property\
                name is used.
        :param default: Default value for variable. If it's a callable,\
            it is called before return. If not provided\
            :class:`~haps.exceptions.UnknownConfigVariable` is raised
        """
        ...
    
    def __get__(self, instance: Config, owner: Type) -> Any:
        ...
    
    def __set_name__(self, owner: Type, name: str) -> None:
        ...
    


