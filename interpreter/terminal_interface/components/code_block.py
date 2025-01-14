"""

The `code_block` module provides a `CodeBlock` class that inherits from `BaseBlock`. This class is responsible for rendering a block of syntax-highlighted code with support for indicating an active line and displaying associated output. The `CodeBlock` renders the code within a Rich console, using tables and panels for structured and styled output. The module utilizes the Rich library for terminal rendering features such as panels, syntax highlighting, and tables. The `CodeBlock` class is customizable in terms of language, output display, active line indication, and other rendering behaviors, appropriate for terminal user interfaces that require dynamic, real-time code display functionalities.

Note: Documentation automatically generated by https://undoc.ai
"""
from rich.box import MINIMAL
from rich.console import Group
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from .base_block import BaseBlock


class CodeBlock(BaseBlock):
    """
    A CodeBlock represents a block of code with optional syntax highlighting, output display, and cursor addition features.
        This class extends `BaseBlock` and holds properties related to the code content, such as the code itself,
        the programming language, and the active line for display purposes. 'CodeBlock' also manages the visual
        representation and refreshing of the code in a console application using rich library components like
        `Table`, `Panel`, `Syntax`, and `Group` for organization.
        Attributes:
            type (str): The type identifier for the block, set to 'code'.
            language (str): The programming language of the code block, used for syntax highlighting.
            output (str): The output resulting from running the code, displayed below the code.
            code (str): The actual code contained within the block.
            active_line (int, optional): The line number that is currently active or selected. Default to `None`.
            margin_top (bool): A flag to determine whether to include a top margin above the code block within
                the display. Default is `True`.
        Methods:
            __init__(): Initializes the `CodeBlock` instance, setting the `type` attribute and initializing
                other necessary attributes for auto-completion in IDEs.
            refresh(cursor=bool): Refreshes the visual display of the code block, optionally including a cursor.
                This method constructs the visual components and updates the displayed content using the 'rich'
                library's components to create an attractive and readable code display with optional interactive
                elements like a movable cursor or highlighted active line.
    """

    def __init__(self):
        """
            Initializes a new instance of the class with default properties.
            This method sets up the initial state of the object, defining default
            values for various properties like 'type', 'language', 'output', 'code',
            'active_line', and 'margin_top'. It also invokes the initialization of
            the parent class.
            Attributes:
                type (str): A string indicating the type of entity, which is set to 'code' by default.
                language (str): A placeholder for the language used, initialized to an empty string.
                output (str): A placeholder for output generated by the entity, initialized to an empty string.
                code (str): A placeholder for the code associated with the entity, initialized to an empty string.
                active_line (NoneType): Initially set to None, this can later hold the reference to an active line within the code.
                margin_top (bool): A flag indicating if there is a top margin, set to True by default.
        """
        super().__init__()

        self.type = "code"

        # Define these for IDE auto-completion
        self.language = ""
        self.output = ""
        self.code = ""
        self.active_line = None
        self.margin_top = True

    def refresh(self, cursor=True):
        """
            Refresh the current displayed code and output in the terminal.
            This function handles the updating of both the code presentation and the output display in the terminal.
            It generates a visual table for displaying lines of code with an optional cursor, 
            and a panel for output display according to the content of 'self.output'.
            If there is no code, the function returns early. The function adds styling to the active line, 
            and formats the rest of the code with default styling.
            If 'cursor' is True, it adds a cursor character at the end of the code. 
            It uses a Markdown panel to create an attractive display for the code and the output.
            Args:
                cursor (bool): A flag to indicate whether to show the cursor after the last character of code.
            Side Effects:
                Triggers a refresh of the terminal display to update the visual representation of the code and output.
        """
        # Get code, return if there is none
        code = self.code
        if not code:
            return

        # Create a table for the code
        code_table = Table(
            show_header=False, show_footer=False, box=None, padding=0, expand=True
        )
        code_table.add_column()

        # Add cursor
        if cursor:
            code += "●"

        # Add each line of code to the table
        code_lines = code.strip().split("\n")
        for i, line in enumerate(code_lines, start=1):
            if i == self.active_line:
                # This is the active line, print it with a white background
                syntax = Syntax(
                    line, self.language, theme="bw", line_numbers=False, word_wrap=True
                )
                code_table.add_row(syntax, style="black on white")
            else:
                # This is not the active line, print it normally
                syntax = Syntax(
                    line,
                    self.language,
                    theme="monokai",
                    line_numbers=False,
                    word_wrap=True,
                )
                code_table.add_row(syntax)

        # Create a panel for the code
        code_panel = Panel(code_table, box=MINIMAL, style="on #272722")

        # Create a panel for the output (if there is any)
        if self.output == "" or self.output == "None":
            output_panel = ""
        else:
            output_panel = Panel(self.output, box=MINIMAL, style="#FFFFFF on #3b3b37")

        # Create a group with the code table and output panel
        group_items = [code_panel, output_panel]
        if self.margin_top:
            # This adds some space at the top. Just looks good!
            group_items = [""] + group_items
        group = Group(*group_items)

        # Update the live display
        self.live.update(group)
        self.live.refresh()
