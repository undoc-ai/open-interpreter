"""

Module for scanning code for potential issues using semgrep.

This module provides functionality related to scanning code using the
semgrep tool. It is capable of determining the proper file extension
and language name for the provided code, creating a temporary file to
house the code, invoking semgrep to perform the scan, and cleaning up
after the scan by removing the temporary file.

Functions:
    get_language_file_extension(language_name): Returns the
        file extension corresponding to the language name provided.
    get_language_proper_name(language_name): Returns the proper name
        of the programming language stated.
    scan_code(code, language, interpreter): Scans the provided piece
        of code for issues using semgrep, performing cleanup
        afterwards. Debug mode and verbosity is supported.

This module also imports necessary functionality for file handling and
subprocess management.

Note: Documentation automatically generated by https://undoc.ai
"""
import os
import subprocess

from yaspin import yaspin
from yaspin.spinners import Spinners

from ..code_interpreters.language_map import language_map
from .temporary_file import cleanup_temporary_file, create_temporary_file


def get_language_file_extension(language_name):
    """
        Retrieves the file extension for a given programming language name.
        This function looks up a programming language in a predefined language map, using the language name provided by the user. It returns the file extension associated with that language. If the language name is not associated with any file extension in the map, the function returns the language object itself.
        Args:
            language_name (str): The name of the programming language for which to retrieve the file extension.
        Returns:
            str: The file extension corresponding to the given programming language name if found, otherwise returns the language object.
        Raises:
            KeyError: If the `language_name` is not found in the language map.
    """
    language = language_map[language_name.lower()]

    if language.file_extension:
        return language.file_extension
    else:
        return language


def get_language_proper_name(language_name):
    """
        Retrieves the proper name of a programming language based on a given language name.
        This function looks up the proper name of a programming language by accessing a predefined mapping.
        `language_map` is expected to be a dictionary where the keys are language names in lowercase, and the
        values are objects that contain a `proper_name` attribute. If the `proper_name` attribute exists and is
        non-empty for the given `language_name`, the function returns it. Otherwise, it returns the object itself
        that represents the programming language.
        Args:
            language_name (str): The name of the programming language to lookup, case-insensitive.
        Returns:
            str or object: The proper name of the language if it exists, or the original language object
            from the mapping if there's no proper name attribute.
        Raises:
            KeyError: If the `language_name` is not found in the `language_map`.
    """
    language = language_map[language_name.lower()]

    if language.proper_name:
        return language.proper_name
    else:
        return language


def scan_code(code, language, interpreter):
    """
        Scans the provided code using the `semgrep` tool to detect potential issues.
        This function creates a temporary file with the given code content, determines the file extension based
        on the provided language, and uses semgrep to scan the code for any issues. It prints out
        messages indicating the status of scanning and results. If any issues are found, they will be reported.
        The temporary file is cleaned up at the end of the scan, regardless of the scan's success or failure.
        Additionally, the function can output verbose messages if the interpreter's debug mode is active.
        Args:
            code (str): The code content to be scanned.
            language (str): The programming language of the code.
            interpreter (object): An object representing the interpreter with properties such as debug_mode
                and safe_mode that influence the behavior of the function.
        Returns:
            None. The function is used for its side effects, including output to the console and triggering
            scans with semgrep.
        Raises:
            Exception: Generic exception captured during the scan process or while cleaning up the
                temporary file; details of the exception are printed to the console.
    """

    temp_file = create_temporary_file(
        code, get_language_file_extension(language), verbose=interpreter.debug_mode
    )

    temp_path = os.path.dirname(temp_file)
    file_name = os.path.basename(temp_file)

    if interpreter.debug_mode:
        print(f"Scanning {language} code in {file_name}")
        print("---")

    # Run semgrep
    try:
        # HACK: we need to give the subprocess shell access so that the semgrep from our pyproject.toml is available
        # the global namespace might have semgrep from guarddog installed, but guarddog is currenlty
        # pinned to an old semgrep version that has issues with reading the semgrep registry
        # while scanning a single file like the temporary one we generate
        # if guarddog solves [#249](https://github.com/DataDog/guarddog/issues/249) we can change this approach a bit
        with yaspin(text="  Scanning code...").green.right.binary as loading:
            scan = subprocess.run(
                f"cd {temp_path} && semgrep scan --config auto --quiet --error {file_name}",
                shell=True,
            )

        if scan.returncode == 0:
            language_name = get_language_proper_name(language)
            print(
                f"  {'Code Scaner: ' if interpreter.safe_mode == 'auto' else ''}No issues were found in this {language_name} code."
            )
            print("")

        # TODO: it would be great if we could capture any vulnerabilities identified by semgrep
        # and add them to the conversation history

    except Exception as e:
        print(f"Could not scan {language} code.")
        print(e)
        print("")  # <- Aesthetic choice

    cleanup_temporary_file(temp_file, verbose=interpreter.debug_mode)
