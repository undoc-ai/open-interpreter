"""

Module for handling creation and cleanup of temporary files.

This module provides functions to easily create a temporary file with specified
contents and extension, as well as to clean up (delete) a specified temporary file.

Functions:
    cleanup_temporary_file(temp_file_name, verbose=False):
        Removes the specified temporary file from the file system.

        Args:
            temp_file_name (str): The name/path of the file to be removed.
            verbose (bool): If True, prints verbose information during the operation. Defaults to False.

        Raises:
            Exception: If unable to remove the file, it catches a general exception and prints
                an error message with the caught exception details.

    create_temporary_file(contents, extension=None, verbose=False):
        Creates a temporary file with the given contents and an optional extension.

        Args:
            contents (str): The content to be written to the temporary file.
            extension (str, optional): The extension to be appended to the file name.
                If not specified, no extension will be added. Defaults to None.
            verbose (bool): If True, prints verbose information during file creation. Defaults to False.

        Returns:
            str: The name/path of the created temporary file.

        Raises:
            Exception: If unable to create the file, it catches a general exception and prints
                an error message with the caught exception details.

Note: Documentation automatically generated by https://undoc.ai
"""
import os
import tempfile


def cleanup_temporary_file(temp_file_name, verbose=False):
    """
        Removes a temporary file from the file system.
        This function attempts to remove the specified temporary file. If the 'verbose' flag is set to True, it
        also prints messages about the cleanup process. In case of failure during file removal, it catches the
        exception and prints an error message, along with the exception details.
        Args:
            temp_file_name (str): The name or path of the temporary file to be removed.
            verbose (bool, optional): A flag that indicates whether to print additional information about the
                cleanup process. Defaults to False.
        Raises:
            Exception: Catches any exception that occurs while attempting to remove the temporary file and
                prints the exception message.
    """

    try:
        # clean up temporary file
        os.remove(temp_file_name)

        if verbose:
            print(f"Cleaning up temporary file {temp_file_name}")
            print("---")

    except Exception as e:
        print(f"Could not clean up temporary file.")
        print(e)
        print("")


def create_temporary_file(contents, extension=None, verbose=False):
    """
    Creates a temporary file with specified contents and extension.
        This function generates a temporary file using the `tempfile` module, writes the given
        contents into the file, and then closes it. If a file extension is specified, it appends
        the extension to the file name. The function returns the name of the temporary file for
        later use. In case of an error during the file creation process, the function prints an
        error message along with the exception message.
        Args:
            contents (str): The content to be written into the temporary file.
            extension (str, optional): The file extension to be appended to the file name. If not provided,
                no extension is appended.
            verbose (bool): If True, prints messages about the file creation process; otherwise, remains silent.
        Returns:
            str: The file name of the created temporary file.
        Raises:
            Exception: If an error occurs during the file creation, an error is printed along with the
                exception message, but the error is not propagated upwards.
    """

    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=f".{extension}" if extension else ""
        ) as f:
            f.write(contents)
            temp_file_name = f.name
            f.close()

        if verbose:
            print(f"Created temporary file {temp_file_name}")
            print("---")

        return temp_file_name

    except Exception as e:
        print(f"Could not create temporary file.")
        print(e)
        print("")
