"""

Module that provides a function `validate_llm_settings` responsible for ensuring the correct settings for using the LiteLLM language model interpreter. Additionally, includes the `display_welcome_message_once` function, which displays the welcome message the first time it is called.

Functions:
    validate_llm_settings(interpreter):
        Validates settings for the LiteLLM language model interpreter. If the interpreter is set to a local model or if the proper environment variables for the API key are set, it returns without any message. In the case of non-local interpreters, it ensures that the necessary API keys are provided before continuing. It checks specifically for OpenAI API keys if the chosen model is from the set of OpenAI chat completion models. If settings are validated successfully, a message indicating the model set is displayed unless the interpreter is in auto_run mode or set to local.

    display_welcome_message_once():
        Displays a welcome message for the Open Interpreter application unless the message has been displayed previously. This function leverages a function attribute to track whether it has already been invoked.

Constants:
    None

Variables:
    None

Exceptions:
    None

Note: Documentation automatically generated by https://undoc.ai
"""
import getpass
import os
import time

import litellm

from .utils.display_markdown_message import display_markdown_message


def validate_llm_settings(interpreter):
    """
    Validates the Local Language Model (LLM) settings for the given interpreter.
    This function checks whether a Local Language Model (LLM) is designated as 'local' or requires an API
    key for a remote service, such as OpenAI. If the interpreter is set to use a local model, the function
    breaks the loop and exits. For remote services, the function checks if the necessary API keys are provided
    either through environment variables or directly as interpreter attributes. If these credentials are missing
    for a model supported by OpenAI, it prompts the user to enter the API key. The function also handles
    displaying welcome messages based on whether 'auto_run' is set or not and the interpreter's 'local' flag.
    If all conditions are met, the function exits, indicating that the LLM settings are valid for the interpreter.
    Args:
        interpreter (Interpreter): The Interpreter object whose Local Language Model settings are to be validated.
    Returns:
        None: This function does not return anything but raises potential errors if settings validation fails.
    """

    # This runs in a while loop so `continue` lets us start from the top
    # after changing settings (like switching to/from local)
    while True:
        if interpreter.local:
            # We have already displayed a message.
            # (This strange behavior makes me think validate_llm_settings needs to be rethought / refactored)
            break

        else:
            # Ensure API keys are set as environment variables

            # OpenAI
            if interpreter.model in litellm.open_ai_chat_completion_models:
                if not os.environ.get("OPENAI_API_KEY") and not interpreter.api_key:
                    display_welcome_message_once()

                    display_markdown_message(
                        """---
                    > OpenAI API key not found

                    To use `GPT-4` (highly recommended) please provide an OpenAI API key.

                    To use another language model, consult the documentation at [docs.openinterpreter.com](https://docs.openinterpreter.com/language-model-setup/).
                    
                    ---
                    """
                    )

                    response = getpass.getpass("OpenAI API key: ")
                    print(f"OpenAI API key: {response[:4]}...{response[-4:]}")

                    display_markdown_message(
                        """

                    **Tip:** To save this key for later, run `export OPENAI_API_KEY=your_api_key` on Mac/Linux or `setx OPENAI_API_KEY your_api_key` on Windows.
                    
                    ---"""
                    )

                    interpreter.api_key = response
                    time.sleep(2)
                    break

            # This is a model we don't have checks for yet.
            break

    # If we're here, we passed all the checks.

    # Auto-run is for fast, light useage -- no messages.
    # If local, we've already displayed a message.
    if not interpreter.auto_run and not interpreter.local:
        display_markdown_message(f"> Model set to `{interpreter.model}`")
    return


def display_welcome_message_once():
    """
    Displays a welcome message only once during the runtime.
    This function is intended to show a welcome message to the user when they first interact
    with a specific functionality in a system. If the function has already been called and
    the welcome message has been displayed, further calls to the function will not result
    in the message being shown again. This is achieved by setting a flag on the function
    to indicate that the message has already been displayed.
    The function uses a nested call to another function, `display_markdown_message`,
    to handle the actual display of the welcome message in a specified markup style.
    This function includes a sleep delay of 1.5 seconds to allow the user to read
    the welcome message before it potentially disappears or new content is shown.
    Attributes:
        _displayed (bool): A flag to determine whether the welcome message was
        already shown to prevent it from being displayed more than once.
    """
    if not hasattr(display_welcome_message_once, "_displayed"):
        display_markdown_message(
            """
        ●

        Welcome to **Open Interpreter**.
        """
        )
        time.sleep(1.5)

        display_welcome_message_once._displayed = True
