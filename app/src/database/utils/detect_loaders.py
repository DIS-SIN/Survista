import importlib
import pkgutil
import os
import types


def detect(pkg: types.ModuleType) -> list:
    """
    returns the names of the load_ modules in the loaders packages
    """
    # try importing the module from the package_name

    if not isinstance(pkg, types.ModuleType):
        raise TypeError('Argument must be of type module ' +
                        f'not {type(pkg)}')

    file_path = os.path.split(pkg.__file__)[0]
    loaders = [name for _, name, _ in pkgutil.iter_modules([file_path])
               if name.split('_')[0] == "load"]
    return loaders
