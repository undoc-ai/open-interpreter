"""

Module that provides a vector search function to find the most similar items to a query in an embedding database.

This module contains a function `search` that takes a query string and systematically
searches a database of vectors to find the most similar items using the cosine distance metric.
The search function is typically employed in information retrieval tasks where
each item in the database has been transformed into a vector embedding.

Functions:
    search(query, db, embed_function, num_results=2)
        Performs a search for the top `num_results` similar items to the `query` in the database `db`
        by comparing the cosine distance of each item's embedding, obtained using `embed_function`.

    Parameters:
        query (str): The query string to search for in the `db`.
        db (dict): A dictionary where keys are item identifiers and values are their corresponding
                   embedding vectors.
        embed_function (callable): A function that converts the query string into its embedding vector.
        num_results (int, optional): Number of top similar results to return. Defaults to 2.

    Returns:
        list: A list of the most similar item identifiers in the `db` to the `query`,
              based on the cosine similarity of their embeddings.

Note: Documentation automatically generated by https://undoc.ai
"""

import numpy as np
from chromadb.utils.distance_functions import cosine


def search(query, db, embed_function, num_results=2):
    """
    Converts a given query into an embedding and retrieves the most similar elements from a provided database.
        The function applies the given embed_function to the query to generate an embedding. It then calculates the cosine
        distances between this query embedding and each embedding in the provided database. The database entries are sorted
        by their proximity to the query embedding, and the specified number of most similar entries is returned.
        Args:
            query (str): The query text to be converted into an embedding.
            db (dict): A dictionary where keys represent database entries and values are the associated embeddings.
            embed_function (callable): A function that converts text into embeddings.
            num_results (int, optional): The number of most similar database entries to retrieve. Defaults to 2.
        Returns:
            list: A list of the most similar database entries to the query.
    """

    # Convert the query to an embedding
    query_embedding = embed_function(query)

    # Calculate the cosine distance between the query embedding and each embedding in the database
    distances = {
        value: cosine(query_embedding, embedding) for value, embedding in db.items()
    }

    # Sort the values by their distance to the query, and select the top num_results
    most_similar_values = sorted(distances, key=distances.get)[:num_results]

    # Return the most similar values
    return most_similar_values
