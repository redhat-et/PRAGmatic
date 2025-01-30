# addressing the issue where the project structure causes pragmatic to not be on the path
import sys
import os
sys.path.insert(0, os.path.abspath(os.getcwd()))

import argparse

from api import index_path_for_rag, execute_rag_query, evaluate_rag_pipeline
from settings import DEFAULT_SETTINGS


def main():
    """
    The tool can be executed in one of the following modes:
    1) Indexing mode (-i flag) - index a collection of documents from the given path.
    2) RAG query mode (-r flag) - answer a given query with RAG using the previously indexed documents.
    3) Evaluation mode (-e flag) - evaluate the RAG pipeline as specified in the settings - NOT YET OFFICIALLY SUPPORTED.
    """
    parser = argparse.ArgumentParser(description='RAG Pipeline PoC')

    parser.add_argument('-i', '--indexing', help='Index a set of documents in the document storage', action='store_true')
    parser.add_argument('--path', help='The path to a directory with the documents to be indexed.')

    parser.add_argument('-r', '--rag', help='Answer a given query based on the indexed documents', action='store_true')
    parser.add_argument('--query', help='The query for the language model to answer.')

    parser.add_argument('-e', '--evaluation', help='Evaluate the RAG pipeline', action='store_true')

    # Positional arguments to capture overrides of default settings
    parser.add_argument('overrides', nargs='*', help="Optionally override default settings as key=value")

    args = parser.parse_args()

    if sum([args.indexing, args.rag, args.evaluation]) != 1:
        print("Wrong usage: exactly one of the supported operation modes (indexing, query) must be specified.")
        return

    custom_settings = {}
    for override in args.overrides:
        if '=' in override:
            key, value = override.split('=', 1)
            if key in DEFAULT_SETTINGS:
                prev_value = DEFAULT_SETTINGS[key]
                if type(prev_value) == int:
                    custom_settings[key] = int(value)
                elif type(prev_value) == float:
                    custom_settings[key] = float(value)
                else:
                    custom_settings[key] = value
            else:
                print(f"Warning: '{key}' is not a valid setting key. Ignoring it.")
        else:
            print(f"Invalid format for argument: '{override}'. Expected format: key=value")

    if args.indexing:
        if args.path is None:
            print("Please specify the path containing the documents to index.")
            return
        index_path_for_rag(args.path, **custom_settings)

    if args.rag:
        if args.query is None:
            print("Please specify the query.")
            return

        # Execute query and get response
        result = execute_rag_query(args.query, **custom_settings)
        
        if isinstance(result, str):  # If a string, print directly
            print(result)
        else:  # If a generator, process each chunk
            for chunk in result:
                print(chunk, end="", flush=True)

    if args.evaluation:
        print(evaluate_rag_pipeline(**custom_settings))


if __name__ == "__main__":
    main()
