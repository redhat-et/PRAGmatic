import argparse

import uvicorn
from fastapi import FastAPI

from api import index_path_for_rag, execute_rag_query, evaluate_rag_pipeline
from settings import DEFAULT_SETTINGS


def main():
    """
    The tool can be executed in one of the following four modes:
    1) Indexing mode (-i flag) - index a collection of documents from the given path.
    2) RAG query mode (-r flag) - answer a given query with RAG using the previously indexed documents.
    3) Evaluation mode (-e flag) - evaluate the RAG pipeline as specified in the settings.
    4) Server mode (-s flag) - run a FastAPI server accepting indexing and query requests.
    """
    parser = argparse.ArgumentParser(description='RAG Pipeline PoC')

    parser.add_argument('-i', '--indexing', help='Index a set of documents in the document storage', action='store_true')
    parser.add_argument('--path', help='The path to a directory with the documents to be indexed.')

    parser.add_argument('-r', '--rag', help='Answer a given query based on the indexed documents', action='store_true')
    parser.add_argument('--query', help='The query for the language model to answer.')

    parser.add_argument('-e', '--evaluation', help='Evaluate the RAG pipeline', action='store_true')

    parser.add_argument('-s', '--server', help='Run a FastAPI server to serve the RAG pipeline', action='store_true')
    parser.add_argument('--port', help='The port for the server to listen on.', type=int, default=8000)

    # Positional arguments to capture overrides of default settings
    parser.add_argument('overrides', nargs='*', help="Optionally override default settings as key=value")

    args = parser.parse_args()

    if sum([args.indexing, args.rag, args.evaluation, args.server]) != 1:
        print("Wrong usage: exactly one of the supported operation modes (indexing, query, evaluation or server) must be specified.")
        return

    custom_settings = {}
    for override in args.overrides:
        if '=' in override:
            key, value = override.split('=', 1)
            if key in DEFAULT_SETTINGS:
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
        print(execute_rag_query(args.query, **custom_settings))

    if args.evaluation:
        print(evaluate_rag_pipeline(**custom_settings))

    if args.server:
        app = FastAPI(title="RAG Pipeline PoC", description="An API server for indexing RAG documents and querying/evaluating the RAG pipeline.")

        @app.get("/indexing")
        def run_indexing_pipeline(document_path: str):
            return index_path_for_rag(document_path, **custom_settings)

        @app.get("/query")
        def query_rag_pipeline(query: str):
            return execute_rag_query(query, **custom_settings)

        @app.get("/eval")
        def run_eval_pipeline():
            return evaluate_rag_pipeline(**custom_settings)

        print(f"Starting FastAPI server on port {args.port}...")
        uvicorn.run(app, host="0.0.0.0", port=args.port)


if __name__ == "__main__":
    main()
