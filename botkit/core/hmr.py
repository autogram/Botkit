import asyncio
import importlib
import importlib.util
import inspect
import os
import re
import sys
from asyncio import Future
from asyncio.exceptions import CancelledError
from pathlib import Path
from types import ModuleType
from typing import Dict, Iterable, List, Optional, Set

from boltons.iterutils import flatten
from watchgod import RegExpWatcher, awatch

from botkit.core.modules._module import Module
from botkit.utils.botkit_logging.setup import create_logger


class HotModuleReloadWorker:
    def __init__(self):
        self._worker_future: Optional[Future] = None
        self.log = create_logger("hmr")

    def start(self, modules: Iterable[Module]) -> Future:
        if self._worker_future:
            self._worker_future.cancel()
        self._worker_future = asyncio.ensure_future(self.__run(modules))
        return self._worker_future

    def reload_module(self, module: Module) -> None:
        pass

    async def __run(self, modules: Iterable[Module]) -> None:
        modules: List[Module] = list(modules)
        try:
            # module_files = self._get_module_dependencies(modules)
            module_files: Dict[Module, Path] = {
                m: Path(m.__class__.__module__) for m in modules
            }

            user_module_names: List[str] = list(
                (
                    x
                    for x in flatten(module_files.values())
                    if not str(x).startswith("botkit.")
                )
            )

            invalid: List[str] = []
            modules_to_watch: List[ModuleType] = []
            for m in user_module_names:
                py_module = sys.modules.get(m)

                if py_module is not None:
                    modules_to_watch.append(py_module)
                else:
                    invalid.append(m)
                    # self.log.error(f"Could not find module '{m}' in sys.modules")

            print("Invalid:")
            print(invalid)

            files_to_watch: List[str] = [inspect.getfile(m) for m in modules_to_watch]
            common_base_dir = os.path.commonprefix(files_to_watch)
            joined_paths = "|".join(map(re.escape, files_to_watch))
            joined_paths_reg = re.compile(f"({joined_paths})")

            async for change in awatch(
                common_base_dir,
                watcher_cls=RegExpWatcher,
                watcher_kwargs=dict(re_files=joined_paths_reg, re_dirs=None),
            ):
                print(change)

                # importlib.reload()
        except CancelledError:
            return
        except:
            self.log.exception("Error in hot module reload worker.")

    @classmethod
    def _get_module_dependencies(
        cls, modules: Iterable[Module]
    ) -> Dict[Module, Set[str]]:
        module_files: Dict[Module, Set[str]] = {}

        for module in modules:
            # TODO: refactor
            python_module_name = module.__module__
            contents = package_contents(python_module_name)
            module_files[module] = contents

        return module_files

    # @classmethod
    # def _get_module_parent_folder(cls, module: Module) -> Path:
    #     module_file_path = Path(module.__class__.__module__)
    #     return module_file_path.parent


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
