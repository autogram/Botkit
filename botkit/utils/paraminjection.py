from inspect import signature, Parameter, _empty
from pprint import pprint

from typing import (
    Callable,
    Type,
    Union,
    Dict,
    cast
)


class ParameterInjector:
    available_references: Dict[Type, object]

    def __init__(self, available_references: Dict[Type, object]):
        self.available_references = available_references

    def _find_contravariant_argument(self, param_type: Type) -> Union[_empty, object]:
        exact_match = self.available_references.get(param_type, None)
        if exact_match is not None:
            # Exact type match
            return exact_match

        covariant_match = next((p for p in self.available_references if issubclass(p, param_type)), _empty)
        return self.available_references[covariant_match]

    def map_kwargs(
        self, callback: Callable, follow_wrapped: bool = True
    ) -> Dict[str, object]:
        sig = signature(callback, follow_wrapped=follow_wrapped)

        # pprint(sig.parameters)

        result: Dict[str, object] = dict()

        for param_name, parameter in sig.parameters.items():
            print(parameter.default)
            parameter = cast(Parameter, parameter)

            # TODO: add try catch for "TypeError: Subscripted generics cannot be used with class and instance checks"
            possible_targets = [
                a
                for a in self.available_references
                if issubclass(a, parameter.annotation)
            ]

            if len(possible_targets) > 1:
                raise ValueError(
                    f"More than one possible target for parameter {parameter.__repr__()}:"
                    f" {possible_targets}"
                )
            elif not possible_targets:
                if parameter.default is not _empty:
                    # parameter has default value but we cannot determine it
                    continue
                else:
                    raise ValueError(
                        f"Parameter {parameter.__repr__()} cannot be filled. TODO: more info"
                    )

            target = possible_targets[0]

            param = self._find_contravariant_argument(parameter.annotation)
            print(param)

            if param is not _empty:
                result[param_name] = param
            else:
                if parameter.default == Parameter.empty:
                    raise ValueError(
                        "Non-default parameter in callback signature whose type blabla"
                    )
                else:
                    pass  # ignore

            pprint(result)

        return result

        if not used_arg_types:
            raise ValueError(
                f"No type hints specified for callback '{callback.__name__}'."
            )

        pyrogram_types = {Message, CallbackQuery, InlineQuery, Poll, User}

        if Update in used_arg_types:
            found_arg_type = Update
        else:
            found_arg_type = None

        for arg in used_arg_types:
            if issubclass(arg, Client):
                pass
            if any((t for t in pyrogram_types if issubclass(arg, t))):
                if found_arg_type is not None:
                    raise ValueError(
                        "More than one possible apply type found, cannot determine the kind of callback."
                    )
                else:
                    found_arg_type = arg

        if not found_arg_type:
            raise ValueError(
                f"No matching callback type found for signature {type_hints}"
            )

        kwargs = dict(callback=callback, filters=filters)
        if issubclass(found_arg_type, Message):
            return MessageHandler(**kwargs)
        elif issubclass(found_arg_type, CallbackQuery):
            return CallbackQueryHandler(**kwargs)
        elif issubclass(found_arg_type, InlineQuery):
            return InlineQueryHandler(**kwargs)
        elif issubclass(found_arg_type, Poll):
            return PollHandler(**kwargs)
        elif issubclass(found_arg_type, User):
            return UserStatusHandler(**kwargs)
        elif found_arg_type is Update:
            return RawUpdateHandler(callback=callback)
        else:
            raise ValueError(
                f"Could not find a matching Pyrogram callback class for type {found_arg_type}."
            )
