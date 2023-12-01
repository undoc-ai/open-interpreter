"""

Module that provides a Python execution environment using a subprocess or Jupyter kernel manager.

This module contains classes and functions to interpret and run Python code in isolated
subprocess environments or through a Jupyter kernel interface. It can preprocess the code,
handle streaming output and capture execution errors. Eclipse-like active line prints can
be added to the code for enhancing debugging and tracing execution flow.

Classes:
    SubprocessCodeInterpreter(BaseCodeInterpreter): An interpreter that runs code in a
        subprocess.
    PythonVision: An interpreter that uses the Jupyter kernel manager to run Python code.
    Python(SubprocessCodeInterpreter): A subclass of SubprocessCodeInterpreter specialized
        for Python code execution with additional preprocessing requirements.
    AddLinePrints(ast.NodeTransformer): AST NodeTransformer that adds print statements to
        indicate active lines in the execution.

Functions:
    preprocess_python(code: str) -> str: Preprocess the input Python code before
        execution to add active line indicators and wrap the code in a try-except block.
    add_active_line_prints(code: str) -> str: Parses the input code into an AST and
        inserts print statements before each line to trace active lines.
    wrap_in_try_except(code: str) -> str: Wraps the entire input Python code in a try-except
        block to capture any exceptions raised during the code execution.

Note: Documentation automatically generated by https://undoc.ai
"""
# Subprocess based

import ast
import os
import re
import shlex
import sys

from ..subprocess_code_interpreter import SubprocessCodeInterpreter
from .python_vision import PythonVision


class Python(SubprocessCodeInterpreter):
    """
    A class that manages the execution of Python code in a subprocess, and specially adapts to Python vision-based scripts if needed.
        This class is a subclass of SubprocessCodeInterpreter and is designed to work with Python scripting. It modifies the behavior
        of the base class by defining the specific file extension and proper name for Python, and by initializing with any given
        configuration parameters. Additionally, the class can morph into a PythonVision class if the configuration specifies
        vision-related features.
        The preprocessing of code and the postprocessing of lines executed are tailored specifically for Python code, including
        detecting special markers in output lines to find the active line or the end of script execution signal.
        Attributes:
            file_extension (str): The default file extension for Python scripts.
            proper_name (str): The proper name to associate with the Python language.
            config (dict): A configuration dictionary that may contain various options for the interpreter, potentially
                           including vision-specific configurations.
            start_cmd (str): The command used to start the Python subprocess, adjusted for Windows and non-Windows environments.
        Methods:
            __init__(self, config): Initializes the class with the supplied configuration.
            preprocess_code(code): Preprocesses Python code before execution.
            line_postprocessor(line): Processes lines of output from the Python subprocess, filtering out prompts.
            detect_active_line(line): Identifies if the line contains a marker indicating the current active line in the script.
            detect_end_of_execution(line): Determines if the line indicates the script execution has ended.
        Note:
            The class may be instantiated with a vision-specific configuration, in which case it transforms into a PythonVision
            class by reassigning its own `__class__` attribute and re-initializing with the same configuration.
    """
    file_extension = "py"
    proper_name = "Python"

    def __init__(self, config):
        """
            Initialize the instance with the given configuration.
            If the 'vision' key in the config is True, the instance's class is changed to PythonVision, and
            it's re-initialized. If the 'vision' key is not True, the instance is initialized as a normal
            Python environment for executing code. In the latter case, it prepares the command to start
            a Python interactive interpreter with unbuffered output on non-Windows systems.
            Args:
                config (dict): Configuration options for the instance. It must contain the 'vision' key
                    to determine which type of interpreter the instance should emulate.
            Raises:
                KeyError: If the 'vision' key is missing from the config dictionary.
        """
        super().__init__()
        self.config = config

        if config["vision"]:
            self.__class__ = PythonVision
            self.__init__(config)
        else:
            executable = sys.executable
            if os.name != "nt":  # not Windows
                executable = shlex.quote(executable)
            self.start_cmd = executable + " -i -q -u"

    def preprocess_code(self, code):
        """
        Preprocesses a given Python code to inject specific modifications before execution.
            This function acts as a wrapper around the 'preprocess_python' function.
            It is designed to apply a set of predefined preprocessing steps to the
            input Python code. The current implementation of preprocessing involves
            injecting print statements to trace active lines of execution. The sole
            purpose of this function is to receive a string containing Python code,
            pass it to the 'preprocess_python' function, and return the processed
            code.
            Args:
                code (str): The Python code to preprocess.
            Returns:
                str: The preprocessed Python code with additional modifications
                    for execution tracing.
            Note:
                The 'preprocess_python' function which this function calls modifies
                the input code by injecting print statements at the beginning of
                each executable line, to assist in debugging and tracking the flow
                of execution.
        """
        return preprocess_python(code)

    def line_postprocessor(self, line):
        """
            Processes a given line of output to determine if it should be modified or discarded.
            This method examines the input line and processes it based on specific criteria. If the line begins with the python
            interactive shell prompt (either '>>>' or '...'), the line is considered as not relevant for the output and thus
            returned as None. Otherwise, the original line is returned without any modification. This behavior is useful for
            filtering out unnecessary interactive shell prompts or continuation lines when processing output from a Python
            interactive session.
            Parameters:
                line (str): The line of text to be post-processed.
            Returns:
                Optional[str]: The post-processed line which is either the unchanged input line or None if the line
                               meets the criteria to be discarded.
        """
        if re.match(r"^(\s*>>>\s*|\s*\.\.\.\s*)", line):
            return None
        return line

    def detect_active_line(self, line):
        """
        Detects if the provided line contains an indication of an active line number.
        This method examines a string to identify if it has an embedded marker
        that specifies a line number which should be considered 'active'. It assumes
        the marker follows the format '##active_line[number]##', where [number]
        is an integer value representing the line number. If such a marker is found,
        the method extracts and returns the line number as an integer. If the marker
        is not present, the method returns None, indicating no active line was detected.
        Args:
            line (str): The line of text to be checked for an 'active line' indicator.
        Returns:
            int or None: The extracted active line number as an integer, or None if no
                          active line indicator is present in the given text line.
        """
        if "##active_line" in line:
            return int(line.split("##active_line")[1].split("##")[0])
        return None

    def detect_end_of_execution(self, line):
        """
            Detects the presence of a specific end-of-execution marker in the provided line.
            This method checks if the provided line of text contains the marker `##end_of_execution##`,
            which is used to indicate the end of a script's execution or output. If the marker is found,
            the method returns True; otherwise, it returns False.
            Args:
                line (str): The line of text to check for the end-of-execution marker.
            Returns:
                bool: True if the `##end_of_execution##` marker is present in the provided line,
                      False otherwise.
        """
        return "##end_of_execution##" in line


def preprocess_python(code):
    """
    Transforms the given Python code to aid in runtime execution analysis.
    This function preprocesses a given string of Python code to insert special print statements
    indicating the active line of execution. It also wraps the entire code block in a try-except
    catch-all structure to capture and print out any exceptions that may occur during runtime.
    Additionally, it cleans up white space lines which may interfere with the intended code structure.
    An end-of-execution print statement is also appended to signify the end of the code execution
    which can be useful for external monitoring and control mechanisms.
    Args:
        code (str): A string containing the Python code to preprocess.
    Returns:
        str: The transformed Python code as a string, ready for execution with additional
            instrumentation for execution flow monitoring and exception handling.
    """

    # Add print commands that tell us what the active line is
    code = add_active_line_prints(code)

    # Wrap in a try except
    code = wrap_in_try_except(code)

    # Remove any whitespace lines, as this will break indented blocks
    # (are we sure about this? test this)
    code_lines = code.split("\n")
    code_lines = [c for c in code_lines if c.strip() != ""]
    code = "\n".join(code_lines)

    # Add end command (we'll be listening for this so we know when it ends)
    code += '\n\nprint("##end_of_execution##")'

    return code


def add_active_line_prints(code):
    """
    Transforms the given python code to insert print statements indicating active line numbers.
        This function takes a string of python code, parses it into an abstract syntax tree (AST),
        traverses the AST, and inserts print statements before each significant line. The inserted print
        statements output line markers, allowing external tools to detect and process the execution flow
        in real-time. The modified AST is then unparsed back into a string of python code with the added
        print statements.
        Args:
            code (str): The python code to transform.
        Returns:
            str: The transformed python code with added print statements before each significant line.
        Note:
            The function does not execute the code it transforms, and it assumes that the input code is
            syntactically correct Python code. Also, the transformed code may look visually different due to
            formatting changes resulting from AST manipulation, but it will be functionally equivalent.
    """
    tree = ast.parse(code)
    transformer = AddLinePrints()
    new_tree = transformer.visit(tree)
    return ast.unparse(new_tree)


class AddLinePrints(ast.NodeTransformer):
    """
    A NodeTransformer subclass that modifies an Abstract Syntax Tree (AST) to insert print
      statements after each line of code.
      This transformation facilitates the tracking of code execution by printing a marker
      with the line number each time a new line of code is executed. The inserted print
      statements include a customizable prefix (by default '##active_line') followed by the
      line number of the subsequent code.
      Attributes:
        None.
      Methods:
        insert_print_statement(line_number): Creates a new AST node representing a print statement.
          Args:
            line_number (int): The line number to be included in the print statement.
          Returns:
            ast.Expr: The AST expression node representing a print statement.
        process_body(body): Processes a list of AST nodes, inserting print statements before each.
          Args:
            body (list or AST node): A list of AST nodes or a single AST node to process.
          Returns:
            list: A new list of AST nodes with print statements inserted.
        visit(node): Visits each node in the AST and processes nodes with 'body' or 'orelse'.
          Overwrites the default visit() method to process the bodies of compound statements
          such as 'if', 'for', 'while', as well as the bodies and exception handlers of 'try' blocks.
          Args:
            node (AST node): The node to visit and potentially transform.
          Returns:
            AST node: A potentially transformed version of the input node with print statements inserted.
      This class is a utility for debugging and code analysis, to be used in conjunction with Python's
      'ast' module, particularly useful when investigating code execution paths or for instructional purposes.
    """

    def insert_print_statement(self, line_number):
        """
            Inserts an AST node that represents a print statement at a given line number.
            This method generates an AST (Abstract Syntax Tree) expression node suitable for injection into a
            Python code AST to print a specific marker line, which can be used to signal that a certain
            line of code has been executed.
            Args:
                line_number (int): The line number where the print statement should be added. The line number
                is used to create a unique marker in the format of a string `##active_line<line_number>##`.
            Returns:
                ast.Expr: An expression AST node representing a print statement that prints out the
                unique marker for the specified line number.
        """
        return ast.Expr(
            value=ast.Call(
                func=ast.Name(id="print", ctx=ast.Load()),
                args=[ast.Constant(value=f"##active_line{line_number}##")],
                keywords=[],
            )
        )

    def process_body(self, body):
        """
        Processes a given 'body' which is a list or a single element, by potentially augmenting it with print statements.
            This function is designed to iteratively process elements in 'body'. If 'body' is not a list, it is
            first converted to a list with just one element. Each element in this list is checked whether it has
            the 'lineno' attribute. If this attribute exists, a print statement is inserted at the corresponding line
            number by calling 'insert_print_statement'. Whether or not the attribute exists, the element is then
            appended to 'new_body'. The augmented 'new_body' is finally returned.
            Args:
                body: A list or a single element that represents parts of a code block to be processed.
            Returns:
                A list that includes the original elements of 'body', potentially augmented with additional
                print statements inserted before elements that have the 'lineno' attribute.
        """
        new_body = []

        # In case it's not iterable:
        if not isinstance(body, list):
            body = [body]

        for sub_node in body:
            if hasattr(sub_node, "lineno"):
                new_body.append(self.insert_print_statement(sub_node.lineno))
            new_body.append(sub_node)

        return new_body

    def visit(self, node):
        """
            Visit a node and update its contents based on custom processing rules.
            The method recursively visits the nodes of the tree, starting with the given node, allowing
            for custom node processing. Upon visiting a node, it processes the node's body if it exists,
            the 'orelse' block for certain control structures, as well as all the blocks within 'Try' nodes.
            This allows for context-aware transformations of the AST.
            Args:
                node (ast.AST): The node to visit and potentially modify.
            Returns:
                ast.AST: The modified or original node after processing.
            Note:
                This function overrides the visit method from the parent class to include additional
                processing steps. The actual processing of the node's body or blocks is handled by a
                separate method, `process_body`, which needs to be defined elsewhere.
        """
        new_node = super().visit(node)

        # If node has a body, process it
        if hasattr(new_node, "body"):
            new_node.body = self.process_body(new_node.body)

        # If node has an orelse block (like in for, while, if), process it
        if hasattr(new_node, "orelse") and new_node.orelse:
            new_node.orelse = self.process_body(new_node.orelse)

        # Special case for Try nodes as they have multiple blocks
        if isinstance(new_node, ast.Try):
            for handler in new_node.handlers:
                handler.body = self.process_body(handler.body)
            if new_node.finalbody:
                new_node.finalbody = self.process_body(new_node.finalbody)

        return new_node


def wrap_in_try_except(code):
    """
    Transforms the provided Python code so that it is wrapped within a try-except block that catches all exceptions and prints their stack traces. This can be used to ensure that any exceptions raised within the provided code block do not cause the program to crash and output useful debugging information instead.
        Parameters:
            code (str): A string of the Python code to be wrapped in the try-except block.
        Returns:
            str: The transformed code as a string where the entire original code block is enclosed within a try-except that catches any Exception and prints its traceback.
    """
    # Add import traceback
    code = "import traceback\n" + code

    # Parse the input code into an AST
    parsed_code = ast.parse(code)

    # Wrap the entire code's AST in a single try-except block
    try_except = ast.Try(
        body=parsed_code.body,
        handlers=[
            ast.ExceptHandler(
                type=ast.Name(id="Exception", ctx=ast.Load()),
                name=None,
                body=[
                    ast.Expr(
                        value=ast.Call(
                            func=ast.Attribute(
                                value=ast.Name(id="traceback", ctx=ast.Load()),
                                attr="print_exc",
                                ctx=ast.Load(),
                            ),
                            args=[],
                            keywords=[],
                        )
                    ),
                ],
            )
        ],
        orelse=[],
        finalbody=[],
    )

    # Assign the try-except block as the new body
    parsed_code.body = [try_except]

    # Convert the modified AST back to source code
    return ast.unparse(parsed_code)
