"""


Module setup_text_llm

This module handles the setup of a text-based language model (LLM) session. The primary
function `setup_text_llm` is used to configure and initialize the model using the provided
interpreter settings. It trims the context and message history to fit the model's context window
and token limits, applies optional interpreter configurations, and returns a text-based model
generator for generating model completions. The module integrates wtih LiteLLM or OpenAI's
GPT offerings based on the interpreter settings. It also handles edge cases and errors when
attempting to prune the context for maintaining meaningful dialogues within the constraints
of the specified model.

The `setup_text_llm` function requires an interpreter object that contains the model configuration
and session parameters. It takes care of setting up and returning a generator that interfaces
with either LiteLLM or OpenAI's API based on the configuration determined through the
provided settings, such as `model`, `context_window`, `max_tokens`, `api_key`, etc.

Functions:
    setup_text_llm(interpreter):
        Configures the message context based on the interpreter's provided settings,
        prepares the LiteLLM or OpenAI API calls accordingly, and returns a message generator
        that can be used for obtaining LLM responses.

Note: Documentation automatically generated by https://undoc.ai
"""
import os
import traceback

import litellm
import openai
import tokentrim as tt

from ...terminal_interface.utils.display_markdown_message import (
    display_markdown_message,
)


def setup_text_llm(interpreter):
    """
        Configures and returns a closure that encapsulates interactions with
        a text-based large language model (LLM), catering to specific interpreter settings.
        This function sets up a closure named 'base_llm' that manages message preprocessing,
        context and token limitations, and the creation of an LLM or LiteLLM generator,
        depending on the provided interpreter configurations. It utilizes the given interpreter object to
        trim messages based on the context window and tokenize them according to the model constraints.
        Args:
            interpreter: An object that contains configuration settings for the LLM, such
                         as context_window, max_tokens, model, api_base, api_key, api_version,
                         max_budget, debug_mode, temperature, etc.
        Returns:
            A function 'base_llm' that, when called with a list of messages, processes the messages
            to adhere to the set configurations, and returns a generator for the LLM interactions.
        Raises:
            TypeError: If a non-string buffer is encountered while anticipating a string during image
                        message handling, and this error type is not due to vision parameters or when
                        any other type-related errors occur not handled by the internal logic.
    """

    # Pass remaining parameters to LiteLLM
    def base_llm(messages):
        """
        Processes messages and generates responses using a large language model (LLM).
        This function processes an initial system message followed by a list of messages to generate a response from a large language model (LLM). It trims the context if necessary, 
        handles context and max token settings, and optionally adjusts parameters for image messages if the interpreter supports vision. 
        The function initializes and configures the LiteLLM generator or OpenAI's API with the provided parameters to produce a completion or a marked message.
        Args:
            messages (list): A list where the first element is the initial system message and the subsequent elements are user and system messages that form the conversation history.
        Returns:
            The generated completion from the LLM or an appropriate error message if any part of the process fails.
        Raises:
            TypeError: If an unexpected type is encountered during message processing.
        """

        system_message = messages[0]["content"]

        messages = messages[1:]

        try:
            if interpreter.context_window and interpreter.max_tokens:
                trim_to_be_this_many_tokens = (
                    interpreter.context_window - interpreter.max_tokens - 25
                )  # arbitrary buffer
                messages = tt.trim(
                    messages,
                    system_message=system_message,
                    max_tokens=trim_to_be_this_many_tokens,
                )
            elif interpreter.context_window and not interpreter.max_tokens:
                # Just trim to the context window if max_tokens not set
                messages = tt.trim(
                    messages,
                    system_message=system_message,
                    max_tokens=interpreter.context_window,
                )
            else:
                try:
                    messages = tt.trim(
                        messages, system_message=system_message, model=interpreter.model
                    )
                except:
                    if len(messages) == 1:
                        display_markdown_message(
                            """
                        **We were unable to determine the context window of this model.** Defaulting to 3000.
                        If your model can handle more, run `interpreter --context_window {token limit}` or `interpreter.context_window = {token limit}`.
                        Also, please set max_tokens: `interpreter --max_tokens {max tokens per response}` or `interpreter.max_tokens = {max tokens per response}`
                        """
                        )
                    messages = tt.trim(
                        messages, system_message=system_message, max_tokens=3000
                    )

        except TypeError as e:
            if interpreter.vision and str(e) == "expected string or buffer":
                # There's just no way to use tokentrim on vision-enabled models yet.
                if interpreter.debug_mode:
                    print("Couldn't token trim image messages. Error:", e)

                ### DISABLED image trimming
                # To maintain the order of messages while simulating trimming, we will iterate through the messages
                # and keep only the first 2 and last 2 images, while keeping all non-image messages.
                # trimmed_messages = []
                # image_counter = 0
                # for message in messages:
                #     if (
                #         "content" in message
                #         and isinstance(message["content"], list)
                #         and len(message["content"]) > 1
                #     ):
                #         if message["content"][1]["type"] == "image":
                #             image_counter += 1
                #             if (
                #                 image_counter <= 2
                #                 or image_counter
                #                 > len(
                #                     [
                #                         m
                #                         for m in messages
                #                         if m["content"][1]["type"] == "image"
                #                     ]
                #                 )
                #                 - 2
                #             ):
                #                 # keep message normal
                #                 pass
                #             else:
                #                 message["content"].pop(1)

                #         trimmed_messages.append(message)
                # messages = trimmed_messages

                # Reunite messages with system_message
                messages = [{"role": "system", "content": system_message}] + messages
            else:
                raise

        if interpreter.debug_mode:
            print("Passing messages into LLM:", messages)

        # Create LiteLLM generator
        params = {
            "model": interpreter.model,
            "messages": messages,
            "stream": True,
        }

        # Optional inputs
        if interpreter.api_base:
            params["api_base"] = interpreter.api_base
        if interpreter.api_key:
            params["api_key"] = interpreter.api_key
        if interpreter.api_version:
            params["api_version"] = interpreter.api_version
        if interpreter.max_tokens:
            params["max_tokens"] = interpreter.max_tokens
        if interpreter.temperature is not None:
            params["temperature"] = interpreter.temperature
        else:
            params["temperature"] = 0.0

        if interpreter.model == "gpt-4-vision-preview":
            # We need to go straight to OpenAI for this, LiteLLM doesn't work
            if interpreter.api_base:
                openai.api_base = interpreter.api_base
            if interpreter.api_key:
                openai.api_key = interpreter.api_key
            if interpreter.api_version:
                openai.api_version = interpreter.api_version
            return openai.ChatCompletion.create(**params)

        # LiteLLM

        # These are set directly on LiteLLM
        if interpreter.max_budget:
            litellm.max_budget = interpreter.max_budget
        if interpreter.debug_mode:
            litellm.set_verbose = True

        # Report what we're sending to LiteLLM
        if interpreter.debug_mode:
            print("Sending this to LiteLLM:", params)

        return litellm.completion(**params)

    return base_llm
