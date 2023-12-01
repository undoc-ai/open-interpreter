"""

A module providing functionality to display messages in a rich text format using blocks within a terminal interface.

This module contains the `MessageBlock` class, which extends the `BaseBlock` class, to enable rich text rendering of messages with markdown-like syntax. It transforms markdown code blocks to text-only representation and wraps the content into a rich panel for display.

Functions:
    textify_markdown_code_blocks(text: str) -> str
        Converts markdown code blocks in a given string to 'text'-only format for consistent rendering.

        Args:
            text (str): The original string that may contain markdown code blocks.

        Returns:
            str: The transformed string with 'text' as the specified language for code blocks, usable for display in rich panels.

Classes:
    MessageBlock(BaseBlock):
        A block for rendering and managing messages as rich text in a live-updating terminal interface.

        Extends the functionality of BaseBlock with methods specific for handling message content and its presentation.

        Attributes:
            type (str): The block type, set to 'message'.
            message (str): The message content to be displayed in the block.
            has_run (bool): Flag indicating whether the block content has been processed and displayed at least once.

        Methods:
            __init__(self):
                Initializes a new instance of MessageBlock, setting up the live display infrastructure.

            refresh(self, cursor: Optional[bool] = True):
                Refreshes the live display with the current message content. Adds a cursor symbol if cursor is True.

                Args:
                    cursor (bool, optional): Indicates whether to include a cursor symbol in the live display. Defaults to True.

Note: Documentation automatically generated by https://undoc.ai
"""
import re

from rich.box import MINIMAL
from rich.markdown import Markdown
from rich.panel import Panel

from .base_block import BaseBlock


class MessageBlock(BaseBlock):
    """
    A component block for displaying messages in a UI framework.
    This class represents a block that is responsible for displaying messages. It instances a base block with a predefined type of 'message' and provides functionality to refresh its content with an option to display a cursor. The message content is processed through a markdown conversion before display.
    Attributes:
        type (str): A string indicating the type of the block, set to 'message' for instances of this class.
        message (str): The message text that will be displayed in this block.
        has_run (bool): A flag indicating whether the block has been run or not.
        live (Live): An object that allows for live updating of the UI, inherited from the base class.
    Methods:
        __init__(self):
            Initializes a new instance of the MessageBlock class.
            The constructor initializes the base block, sets the 'type' attribute to 'message',
            initializes 'message' as an empty string, and 'has_run' as False.
        refresh(self, cursor=True):
            Updates the content of the block and refreshes the display.
            The content of 'message' is processed to convert markdown code blocks to text, and a cursor is
            optionally appended to the content. A new Markdown panel is then created with the processed
            content using a minimal box style, and the display is refreshed using the 'live' attribute.
            Args:
                cursor (bool, optional): A flag to determine whether to append a cursor symbol to the
                content. Defaults to True.
    """
    def __init__(self):
        """
            Initialize the message object.
            This constructor method is used to initialize the properties of the message object. It sets the
            type of the message object to 'message', initializes the message content as an empty string, and
            sets the 'has_run' flag to False to indicate that the message action has not been executed yet.
            Attributes:
                type (str): The type of the message, set to 'message' by default.
                message (str): The content of the message, initialized to an empty string.
                has_run (bool): A flag indicating whether the message action has been executed, initialized to
                False.
        """
        super().__init__()

        self.type = "message"
        self.message = ""
        self.has_run = False

    def refresh(self, cursor=True):
        """
        Converts the current instance's message from markdown to text where code blocks are indicated, appending a cursor at the end if specified, and then updates and refreshes the associated 'live' display panel with the new content.
            This function transforms all markdown code block delimiters in the message to a '```text' format, ensuring they are recognized as text blocks. It then creates a 'Panel' to contain the formatted message, optionally with a cursor at the end. Finally, the function updates the 'live' object with the new panel and refreshes the display to show the latest content.
            Args:
                cursor (bool): A flag indicating whether to append a cursor symbol ('●') to the end of the converted text. The cursor is appended if the flag is set to true. Defaults to True.
            Returns:
                None: The function does not return any value.
        """
        # De-stylize any code blocks in markdown,
        # to differentiate from our Code Blocks
        content = textify_markdown_code_blocks(self.message)

        if cursor:
            content += "●"

        markdown = Markdown(content.strip())
        panel = Panel(markdown, box=MINIMAL)
        self.live.update(panel)
        self.live.refresh()


def textify_markdown_code_blocks(text):
    """
    def textify_markdown_code_blocks(text):
        Converts markdown code block annotations to a uniform 'text' annotation.
        This function searches through the given markdown text for code
        blocks, denoted by triple backticks (```). When a code block
        is found, its language annotation (if any) is replaced with
        'text'. This function is particularly useful if the language
        annotation is irrelevant and a uniform format is needed.
        Args:
            text (str): A string containing markdown content.
        Returns:
            str: The modified markdown text with 'text' annotations
                replacing any specific language annotations in code blocks.
    """
    replacement = "```text"
    lines = text.split("\n")
    inside_code_block = False

    for i in range(len(lines)):
        # If the line matches ``` followed by optional language specifier
        if re.match(r"^```(\w*)$", lines[i].strip()):
            inside_code_block = not inside_code_block

            # If we just entered a code block, replace the marker
            if inside_code_block:
                lines[i] = replacement

    return "\n".join(lines)
