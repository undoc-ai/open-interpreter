"""


    Display a markdown formatted message using the rich library.

    This function takes a string that contains markdown formatted text and prints it out
    to the console in a styled manner. It checks for horizontal rules (---) to
    print them as separators and for blockquotes to ensure they are followed by a
    newline for better readability. Each line of the input message is processed and
    printed individually with appropriate styling applied.

    Args:
        message (str): A string containing markdown formatted text.

    Returns:
        None.
    

Note: Documentation automatically generated by https://undoc.ai
"""
from rich import print as rich_print
from rich.markdown import Markdown
from rich.rule import Rule


def display_markdown_message(message):
    """
        Processes a markdown message and displays it with formatting.
        The function takes a markdown formatted string, splits it into lines, and then processes each line
        to be printed with the appropriate formatting. It uses rich library functions `rich.print`
        (aliased as `rich_print` in this context) to print markdown and `rich.Rule` to create
        horizontal rules based on '---' lines in the message. Newlines in the original message
        result in blank lines being printed, and blockquotes indicated by '>' at the beginning
        of the line are followed by an extra newline for better readability.
        Args:
            message (str): The markdown formatted string to be displayed.
        Returns:
            None: The function prints the formatted message to the console and does not return anything.
    """

    for line in message.split("\n"):
        line = line.strip()
        if line == "":
            print("")
        elif line == "---":
            rich_print(Rule(style="white"))
        else:
            rich_print(Markdown(line))

    if "\n" not in message and message.startswith(">"):
        # Aesthetic choice. For these tags, they need a space below them
        print("")
