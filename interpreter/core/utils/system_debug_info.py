"""

Module that provides functions to gather and display debug information about the Python environment, host operating system, and an interpreter object.

    This module consists of various utility functions that retrieve information about the current runtime environment, the versions of Python and associated tools, and system resources such as CPU and RAM usage. Additionally, the module offers a function to extract details from a provided interpreter object, which includes information regarding its configuration and status.

    Functions:
        get_python_version(): Gets the version of Python that is currently running.

        get_pip_version(): Retrieves the version of pip installed in the environment.

        get_oi_version(): Fetches the Open Interpreter's version both from the command line and the installed package.

        get_os_version(): Retrieves information about the operating system including the version and architecture.

        get_cpu_info(): Returns details about the CPU of the system running the script.

        get_ram_info(): Provides information on the total, used, and free RAM in the system.

        interpreter_info(interpreter): Extracts and returns comprehensive information about the specified interpreter object.

        system_info(interpreter): Gathers and prints out a summary of the overall system and interpreter information.

    Each function is designed to be standalone and can be used independently to obtain specific system or interpreter information. The `system_info` function aggregates information from the other functions and gives a consolidated view ideal for debug purposes.

Note: Documentation automatically generated by https://undoc.ai
"""
import platform
import subprocess

import pkg_resources
import psutil


def get_python_version():
    """
    Gets the current Python version running on the system.
    Returns:
        str: The Python version as a string in the format of 'major.minor.micro'.
    """
    return platform.python_version()


def get_pip_version():
    """
        Gets the current version of pip installed in the system.
        This function will invoke the pip command-line tool to retrieve the current pip version installed.
        It returns the version number as a string, or an error message if pip cannot be accessed or
        any unexpected error occurs during execution of the subprocess.
        Returns:
            str: The current version of pip as a string, or an error message if an exception is raised.
    """
    try:
        pip_version = subprocess.check_output(["pip", "--version"]).decode().split()[1]
    except Exception as e:
        pip_version = str(e)
    return pip_version


def get_oi_version():
    """
        Retrieves the version of the currently installed 'open-interpreter' package and the version reported by the interpreter command.
        This function executes the 'interpreter --version' command to get the version string from the command line,
        then it retrieves the version installed in the Python environment using the 'pkg_resources' method.
        Returns:
            tuple: A tuple where the first element is the version string obtained from the command line and
            the second element is the version string obtained from the package distribution.
        Raises:
            Exception: It captures any exception raised while attempting to fetch the command line version
            and returns the exception message as part of the returned tuple.
    """
    try:
        oi_version_cmd = (
            subprocess.check_output(["interpreter", "--version"]).decode().split()[1]
        )
    except Exception as e:
        oi_version_cmd = str(e)
    oi_version_pkg = pkg_resources.get_distribution("open-interpreter").version
    oi_version = oi_version_cmd, oi_version_pkg
    return oi_version


def get_os_version():
    """
    Get the operating system version.
    This function retrieves the operating system's version information.
    Returns:
        str: A string representing the operating system's version, as provided
            by `platform.platform()`. This often includes system's distribution
            and version, the machine type, and additional versioning information
            specific to the operating system.
    """
    return platform.platform()


def get_cpu_info():
    """
    Gets the name of the processor used by the machine.
        This function uses the `platform` standard library to retrieve information
        about the processor on which the Python interpreter is currently executing.
        Returns:
            str: The processor name or the empty string if the information is not
            available.
    """
    return platform.processor()


def get_ram_info():
    """
        Retrieves information about the system's RAM, including total, used, and free memory.
        This function obtains memory usage statistics from the system using the `psutil` library.
        It calculates the RAM in gigabytes for total, used, and free memory and returns a formatted string.
        Returns:
            str: A string reporting total, used, and free RAM, each to two decimal places.
    """
    vm = psutil.virtual_memory()
    used_ram_gb = vm.used / (1024**3)
    free_ram_gb = vm.free / (1024**3)
    total_ram_gb = vm.total / (1024**3)
    return f"{total_ram_gb:.2f} GB, used: {used_ram_gb:.2f}, free: {free_ram_gb:.2f}"


def interpreter_info(interpreter):
    """
    Provides information about an interpreter object.
    This function takes an interpreter object which contains various attributes about
    the state and configuration of the interpreter. It formats and returns a string
    that presents this information in a human-readable form. If the interpreter is
    local, it executes a curl command to retrieve details from the API base endpoint,
    otherwise, it reports that the interpreter is not local. Any issues during the
    retrieval or formatting process result in an error message.
    Args:
        interpreter (obj): The interpreter object with attributes describing its
            state and configuration.
    Returns:
        str: A string containing formatted information about the interpreter, including
            vision, model, API base, and more, or an error message if information
            could not be retrieved.
    """
    try:
        if interpreter.local:
            try:
                curl = subprocess.check_output(f"curl {interpreter.api_base}")
            except Exception as e:
                curl = str(e)
        else:
            curl = "Not local"

        # System message:{interpreter.system_message}
        return f"""

        Interpreter Info
        Vision: {interpreter.vision}
        Model: {interpreter.model}
        Function calling: {interpreter.function_calling_llm}
        Context window: {interpreter.context_window}
        Max tokens: {interpreter.max_tokens}

        Auto run: {interpreter.auto_run}
        API base: {interpreter.api_base}
        Local: {interpreter.local}

        Curl output: {curl}
    """
    except:
        return "Error, couldn't get interpreter info"


def system_info(interpreter):
    """
    Gets comprehensive system and interpreter information.
    Gathers information about the Python interpreter version, Pip version, Open-interpreter version, operating system,
    CPU, RAM, and additional details specific to the provided interpreter argument.
    Intended to be used for diagnostic or informational purposes, where understanding
    the environment in which the interpreter is running can be crucial.
    Args:
        interpreter (str): The interpreter for which the information is being requested.
    Returns:
        None: This function does not return anything. It prints the gathered information directly to the console.    
    """
    oi_version = get_oi_version()
    print(
        f"""
        Python Version: {get_python_version()}
        Pip Version: {get_pip_version()}
        Open-interpreter Version: cmd:{oi_version[0]}, pkg: {oi_version[1]}
        OS Version and Architecture: {get_os_version()}
        CPU Info: {get_cpu_info()}
        RAM Info: {get_ram_info()}
        {interpreter_info(interpreter)}
    """
    )
