"""




    Retrieves the relevant procedures as a string, based on the context provided by an interpreter's recent messages.

    This function fetches the procedures or updates the local procedure database if necessary, and then it generates a query
    string from the last two messages of the interpreter. It then queries the updated database for relevant procedures.

    Args:
        interpreter (Interpreter): An instance of the interpreter that contains context such as recent messages,
            downloaded procedures, and possibly a local copy of procedures database.

    Returns:
        str: A formatted string of recommended procedures to be included in the plan. It emphasizes the inclusion of
            verbatim code snippets from procedures if they are relevant to the task at hand.

    Raises:
        requests.RequestException: If there is a failure to fetch the procedures database from the remote source.

Note: Documentation automatically generated by https://undoc.ai
"""
#### ARCHIVED ####
# The following code has been archived. It uses a locally running vector db.
# I think in time we'll find the right way to do this conditionally,
# but it's just too much to download for the average user.

import requests

from ..utils.vector_search import search


def get_relevant_procedures_string(interpreter):
    """
    Fetches and provides a formatted string of relevant procedures based on recent interpreter activity.
    This function retrieves the necessary procedures from an online database or local storage, updates the interpreter's
    procedures database, and constructs a query string from the last two messages received by the interpreter. It then
    utilizes a vector search to identify the most relevant procedures. The result is a formatted string containing
    recommendations for procedures, including explicit code snippets if applicable, for the user to include in their plan.
    Args:
        interpreter (Interpreter): An instance of the Interpreter class which holds properties such as procedures,
                                     messages, and configuration for downloading and processing procedures.
    Returns:
        str: A formatted string that includes a list of recommended procedures which should be considered
             for inclusion in the user's plan, incorporating any exact code snippets present in the procedure steps.
    """
    # Open Procedures is an open-source database of tiny, up-to-date coding tutorials.
    # We can query it semantically and append relevant tutorials/procedures to our system message

    # If download_open_procedures is True and interpreter.procedures is None,
    # We download the bank of procedures:

    if (
        interpreter.procedures is None
        and interpreter.download_open_procedures
        and not interpreter.local
    ):
        # Let's get Open Procedures from Github
        url = "https://raw.githubusercontent.com/KillianLucas/open-procedures/main/procedures_db.json"
        response = requests.get(url)
        interpreter._procedures_db = response.json()
        interpreter.procedures = interpreter._procedures_db.keys()

    # Update the procedures database to reflect any changes in interpreter.procedures
    if interpreter._procedures_db.keys() != interpreter.procedures:
        updated_procedures_db = {}
        if interpreter.procedures is not None:
            for key in interpreter.procedures:
                if key in interpreter._procedures_db:
                    updated_procedures_db[key] = interpreter._procedures_db[key]
                else:
                    updated_procedures_db[key] = interpreter.embed_function(key)
        interpreter._procedures_db = updated_procedures_db

    # Assemble the procedures query string. Last two messages
    query_string = ""
    for message in interpreter.messages[-2:]:
        if "content" in message:
            query_string += "\n" + message["content"]
        if "code" in message:
            query_string += "\n" + message["code"]
        if "output" in message:
            query_string += "\n" + message["output"]
    query_string = query_string[-3000:].strip()

    num_results = interpreter.num_procedures

    relevant_procedures = search(
        query_string,
        interpreter._procedures_db,
        interpreter.embed_function,
        num_results=num_results,
    )

    # This can be done better. Some procedures should just be "sticky"...
    relevant_procedures_string = (
        "[Recommended Procedures]\n"
        + "\n---\n".join(relevant_procedures)
        + "\nIn your plan, include steps and, if present, **EXACT CODE SNIPPETS** (especially for deprecation notices, **WRITE THEM INTO YOUR PLAN -- underneath each numbered step** as they will VANISH once you execute your first line of code, so WRITE THEM DOWN NOW if you need them) from the above procedures if they are relevant to the task. Again, include **VERBATIM CODE SNIPPETS** from the procedures above if they are relevent to the task **directly in your plan.**"
    )

    if interpreter.debug_mode:
        print("Generated relevant_procedures_string:", relevant_procedures_string)

    return relevant_procedures_string
