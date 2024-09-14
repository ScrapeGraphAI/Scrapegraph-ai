"""
high-level module for dynamic importing of python modules at runtime

source code inspired by https://gist.github.com/DiTo97/46f4b733396b8d7a8f1d4d22db902cfc
"""
import sys
import typing
import importlib.util
if typing.TYPE_CHECKING:
    import types

def srcfile_import(modpath: str, modname: str) -> "types.ModuleType":
    """imports a python module from its srcfile

    Args:
        modpath: The srcfile absolute path
        modname: The module name in the scope

    Returns:
        The imported module

    Raises:
        ImportError: If the module cannot be imported from the srcfile
    """
    spec = importlib.util.spec_from_file_location(modname, modpath)

    if spec is None:
        message = f"missing spec for module at {modpath}"
        raise ImportError(message)

    if spec.loader is None:
        message = f"missing spec loader for module at {modpath}"
        raise ImportError(message)

    module = importlib.util.module_from_spec(spec)

    sys.modules[modname] = module

    spec.loader.exec_module(module)

    return module


def dynamic_import(modname: str, message: str = "") -> None:
    """imports a python module at runtime

    Args:
        modname: The module name in the scope
        message: The display message in case of error

    Raises:
        ImportError: If the module cannot be imported at runtime
    """
    if modname not in sys.modules:
        try:
            import importlib

            module = importlib.import_module(modname)
            sys.modules[modname] = module
        except ImportError as x:
            raise ImportError(message) from x
