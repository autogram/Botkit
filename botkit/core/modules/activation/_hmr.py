import asyncio
import importlib
import importlib.util
import inspect
import os
import re
from dataclasses import dataclass

import sys
from asyncio import Future
from asyncio.exceptions import CancelledError
from pathlib import Path
from types import ModuleType
from typing import Dict, Iterable, List, Optional, Set, cast

from boltons.iterutils import flatten
from watchgod import RegExpWatcher, awatch

from botkit.core.modules._module import Module
from botkit.core.services import service
from botkit.utils.botkit_logging.setup import create_logger


@dataclass
class _ModuleDepsInfo:
    module: Module
    file_path: str
    python_module: ModuleType

    @property
    def is_builtin(self) -> bool:
        return self.python_module.__name__.startswith("botkit.")

    @property
    def display_name(self) -> str:
        return self.module.get_name()

    @classmethod
    def from_module(cls, module: Module) -> "_ModuleDepsInfo":
        py_module_name = module.__class__.__module__
        py_module = sys.modules.get(py_module_name)

        if py_module is None:
            raise ModuleNotFoundError(f"Could not find module {py_module_name} in sys.modules.")

        file_path = inspect.getfile(py_module)
        return _ModuleDepsInfo(module=module, file_path=file_path, python_module=py_module)


@service
class HotModuleReloadWorker:
    def __init__(self):
        self._worker_future: Optional[Future] = None
        self.log = create_logger("hmr")

    def start(self, modules: List[Module]):
        if self._worker_future:
            self._worker_future.cancel()
        self._worker_future = asyncio.ensure_future(self.__run(modules))

    def reload_module(self, module: Module) -> None:
        pass

    async def __run(self, modules: List[Module]) -> None:
        modules: List[Module] = list(modules)
        try:
            # module_files = self._get_module_dependencies(modules)
            # modules_by_files: Dict[str, Module] = {m.__class__.__module__: m for m in modules}
            #
            # user_module_names: List[str] = list(
            #     (x for x in flatten(modules_by_files.keys()) if not str(x).startswith("botkit."))
            # )
            #
            invalid: List[Module] = []
            # modules_to_watch: List[ModuleType] = []
            # for m in user_module_names:
            #     py_module = sys.modules.get(m)
            #
            #     if py_module is not None:
            #         modules_to_watch.append(py_module)
            #     else:
            #         invalid.append(m)
            #         # self.log.error(f"Could not find module '{m}' in sys.modules")
            #
            # print("Invalid:")
            # print(invalid)
            #
            # files_to_watch: List[str] = [inspect.getfile(m) for m in modules_to_watch]
            module_infos: List[_ModuleDepsInfo] = []
            for m in modules:
                try:
                    info = _ModuleDepsInfo.from_module(m)

                    if info.is_builtin:
                        continue

                    module_infos.append(info)
                except ModuleNotFoundError:
                    invalid.append(m)

            files_to_watch = [x.file_path for x in module_infos]
            common_base_dir = os.path.commonprefix(files_to_watch)
            joined_paths = "|".join(map(re.escape, files_to_watch))
            joined_paths_reg = re.compile(f"({joined_paths})")

            async for changes in awatch(
                common_base_dir,
                watcher_cls=RegExpWatcher,
                watcher_kwargs=dict(re_files=joined_paths_reg, re_dirs=None),
            ):
                for change in changes:
                    update_type, file_changed = cast(tuple, change)

                    if not (
                        module_to_reload := next(
                            (x for x in module_infos if file_changed == x.file_path), None
                        )
                    ):
                        continue

                    try:
                        # TODO: check module_activator.py
                        importlib.reload(module_to_reload.python_module)
                        self.log.info(f"Loaded {module_to_reload.display_name}")
                    except:
                        self.log.error(f"Could not load {module_to_reload.display_name}")
        except CancelledError:
            pass
        except:
            self.log.exception("Error in HMR worker.")

    @classmethod
    def _get_module_dependencies(cls, modules: List[Module]) -> Dict[Module, Set[str]]:
        module_files: Dict[Module, Set[str]] = {}

        for module in modules:
            # TODO: refactor
            python_module_name = module.__module__
            contents = package_contents(python_module_name)
            module_files[module] = contents

        return module_files


MODULE_EXTENSIONS = [".py"]


def package_contents(package_name) -> Set[str]:
    """
    TODO: This is cool, but broken for __init__.py imports :/
    """
    try:
        spec = importlib.util.find_spec(package_name)
        if not spec or not spec.origin:
            return set()
    except:
        return set()

    pathname = Path(spec.origin).parent

    if not pathname:
        return set()

    ret = set()
    with os.scandir(pathname) as entries:
        for entry in entries:
            if entry.name.startswith("__") and not entry.name.startswith("__init__"):
                continue
            current = ".".join((package_name, entry.name.partition(".")[0]))
            if entry.is_file():
                if any((True for x in MODULE_EXTENSIONS if entry.name.endswith(x))):
                    ret.add(current)
            elif entry.is_dir():
                ret.add(current)
                ret |= package_contents(current)

    return ret
