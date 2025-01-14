"""



Module for running and handling PowerShell scripts using a subprocess interpreter pattern inheriting from SubprocessCodeInterpreter.

This module defines a set of classes and functions to execute PowerShell (PS1) scripts, pre-process the code with additional scripting for line annotation and error capturing, and manage output and error streams from the underlying PowerShell process. The PowerShell class defined in this module is responsible for configuring the initial settings for the subprocess, handling stream outputs, and processing PowerShell code.

Classes:
    PowerShell(SubprocessCodeInterpreter): A SubprocessCodeInterpreter implementation that runs PowerShell code. It overrides several methods for PowerShell specific processing.

Functions:
    preprocess_powershell(code: str) -> str: Preprocesses PowerShell script code adding line print annotations and wrapping it in a try-catch block.
    add_active_line_prints(code: str) -> str: Injects print statements before each line of code to mark active lines being executed.
    wrap_in_try_catch(code: str) -> str: Wraps the PowerShell script code inside a try-catch block for error handling.

Note: Documentation automatically generated by https://undoc.ai
"""
import os
import platform
import shutil

from ..subprocess_code_interpreter import SubprocessCodeInterpreter


class PowerShell(SubprocessCodeInterpreter):
    """
    A class representing a PowerShell interpreter for running PowerShell scripts.
    This class inherits from `SubprocessCodeInterpreter` and is configured to run PowerShell scripts with '.ps1' extension.
    It determines the appropriate start command to execute PowerShell depending on the operating system.
    Attributes:
        file_extension (str): The file extension for PowerShell scripts, set to `'ps1'`.
        proper_name (str): The proper name of the interpreter, set to `'PowerShell'`.
        config (dict): A configuration dictionary provided upon initialization.
        start_cmd (str): The command used to start the PowerShell interpreter, which is platform-dependent.
    Methods:
        __init__(self, config):
            Initializes the PowerShell object with the given configuration. Sets the start command based on the
            operating system.
        preprocess_code(self, code):
            Preprocesses the provided PowerShell code before execution.
        line_postprocessor(self, line):
            A method to process each line of output from the interpreter, currently returns the line unchanged.
        detect_active_line(self, line):
            Detects if a line in the output contains an active line marker and returns the line number if found.
        detect_end_of_execution(self, line):
            Determines if the given line indicates the end of script execution.
        Raises:
            Various exceptions related to subprocess and environment if any issues arise during initialization
            or execution of PowerShell commands.
    """
    file_extension = "ps1"
    proper_name = "PowerShell"

    def __init__(self, config):
        """
        Initializes the object with configuration provided and determines the start command based on the platform.
            This method sets up the initial state by storing the provided configuration and determining
            the appropriate command to start the shell. It uses 'powershell.exe' for Windows platforms
            and opts for 'pwsh' (PowerShell Core) if available on non-Windows platforms; otherwise, it
            falls back to 'bash'.
            Args:
                config (dict): A dictionary containing configuration parameters for initialization.
            Attributes:
                config (dict): Stores the provided configuration dictionary.
                start_cmd (str): The command to start the shell, determined based on the operating system.
        """
        super().__init__()
        self.config = config

        # Determine the start command based on the platform (use "powershell" for Windows)
        if platform.system() == "Windows":
            self.start_cmd = "powershell.exe"
            # self.start_cmd = os.environ.get('SHELL', 'powershell.exe')
        else:
            # On non-Windows platforms, prefer pwsh (PowerShell Core) if available, or fall back to bash
            self.start_cmd = "pwsh" if shutil.which("pwsh") else "bash"

    def preprocess_code(self, code):
        """
        Preprocesses the provided PowerShell code to enhance its error handling and output tracking capabilities.
            This function takes a string of PowerShell code, then it incorporates additional PowerShell code that adds print statements to track the execution of individual lines and wraps the modified code in a try-catch block. This is primarily done to facilitate debugging and execution flow monitoring. It also appends a unique end-of-execution marker to the code, allowing the caller to detect when the PowerShell execution has completed.
            Args:
                code (str): The PowerShell code to be preprocessed.
            Returns:
                str: The transformed PowerShell code with additional print statements for active line tracking, wrapped in a try-catch block, and appended with an end-of-execution marker.
        """
        return preprocess_powershell(code)

    def line_postprocessor(self, line):
        return line

    def detect_active_line(self, line):
        """
        Detects if a given line of text indicates an active line in an application's output stream.
            This function checks if the provided line contains a specific marker that denotes
            an active line of execution ('##active_line'). If the marker is found, the function
            extracts and returns the line number that follows the marker. If the marker is not
            present, the function returns None, indicating that the line does not represent
            an active line of execution.
            Args:
                line (str): The line of text to be analyzed for an active line indicator.
            Returns:
                Optional[int]: The number of the active line if the marker is present; otherwise, None.
        """
        if "##active_line" in line:
            return int(line.split("##active_line")[1].split("##")[0])
        return None

    def detect_end_of_execution(self, line):
        """
            Detects the presence of a specific end of execution marker within a provided line of text.
            This method checks if the string '##end_of_execution##' is part of the line passed to it. It's used to
            determine if a particular execution block or script has completed its run. This can be useful in
            environments where the end of a script's output needs to be detected programmatically.
            Args:
                line (str): A string representing a line of text that may contain the end of execution marker.
            Returns:
                bool: A boolean value indicating whether the '##end_of_execution##' marker is found within the input line.
        """
        return "##end_of_execution##" in line


def preprocess_powershell(code):
    """
        Preprocesses PowerShell code by injecting print statements for active line tracking and
        wrapping the code in a try-catch block for error handling.
        The function enhances the input PowerShell code by first calling `add_active_line_prints` which
        parses the code and adds print statements after each line of code to help in identifying the currently executed line.
        It then wraps the modified code in a PowerShell try-catch block by calling `wrap_in_try_catch`
        to manage error propagation. Lastly, it appends an output statement at the end of the
        code to signal the end of execution.
        Args:
            code (str): A string containing the PowerShell code to be preprocessed.
        Returns:
            str: The modified PowerShell code containing additional print statements for
                active line tracking, wrapped in a try-catch block, and ending with a
                specific marker indicating the end of the script execution.
    """
    # Add commands that tell us what the active line is
    code = add_active_line_prints(code)

    # Wrap in try-catch block for error handling
    code = wrap_in_try_catch(code)

    # Add end marker (we'll be listening for this to know when it ends)
    code += '\nWrite-Output "##end_of_execution##"'

    return code


def add_active_line_prints(code):
    """
    Adds markers before each line of the given code for use in detecting active lines during code execution.
    Args:
        code (str): A string containing the code lines separated by new line characters.
    Returns:
        str: The modified code with added 'Write-Output "##active_line{line_number}##"' before each line.
    """
    lines = code.split("\n")
    for index, line in enumerate(lines):
        # Insert the Write-Output command before the actual line
        lines[index] = f'Write-Output "##active_line{index + 1}##"\n{line}'
    return "\n".join(lines)


def wrap_in_try_catch(code):
    """
    Wraps the provided PowerShell code within a try-catch block.
    This function takes a string containing PowerShell code and encapsulates
    it within a try-catch block. This block sets the error action preference to 'Stop',
    ensuring that any error encountered within the try block will halt the script execution
    and will be caught by the catch block, where it triggers a 'Write-Error' cmdlet to output the error.
    Args:
        code (str): A string containing the PowerShell code to be encapsulated.
    Returns:
        str: The input code wrapped inside a try-catch block with error handling.
    """
    try_catch_code = """
try {
    $ErrorActionPreference = "Stop"
"""
    return try_catch_code + code + "\n} catch {\n    Write-Error $_\n}\n"
