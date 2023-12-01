"""

Checks if a package is available in the current Python environment.

This function first checks if the package is already loaded into `sys.modules`. If
not, it attempts to find the package specification using `importlib.util.find_spec`,
and if found, it tries to load and execute the module. If any step fails or the
package cannot be found, the function returns `False`. If the package is already
loaded or is successfully loaded during this process, it returns `True`.

Args:
    package (str): The name of the package to check for.

Returns:
    bool: `True` if the package is found and available, `False` otherwise.

Note: Documentation automatically generated by https://undoc.ai
"""
import importlib.util
import sys


# borrowed from: https://stackoverflow.com/a/1051266/656011
def check_for_package(package):
    """
        Checks if a Python package is already imported or can be imported.
        This function examines if a given package name is present in the system modules or can be imported without any ImportError. If the package is already in sys.modules, it returns True indicating the package is available. If not, it attempts to find the package's specification and import it. If the package can be successfully imported, it returns True; otherwise, it returns False to indicate the package is not available.
        Args:
            package (str): The name of the package to be checked.
        Returns:
            bool: True if the package is already imported or was successfully imported, otherwise False.
    """
    if package in sys.modules:
        return True
    elif (spec := importlib.util.find_spec(package)) is not None:
        try:
            module = importlib.util.module_from_spec(spec)

            sys.modules[package] = module
            spec.loader.exec_module(module)

            return True
        except ImportError:
            return False
    else:
        return False
