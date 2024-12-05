import argparse

import uvicorn
from fastapi import FastAPI

from evaluation import Evaluator
from indexing import LocalJSONIndexingPipelineWrapper
from rag import RagPipelineWrapper
from settings import DEFAULT_SETTINGS


def main():
    """
    The tool can be executed in one of the following three modes:
    1) Indexing mode (-i flag) - index a collection of documents from the given path.
    2) Query mode (-q flag) - answer a given query with RAG using the previously indexed documents.
    3) Server mode (-s flag) - run a FastAPI server accepting indexing and query requests.
    """
    parser = argparse.ArgumentParser(description='RAG Pipeline PoC')

    parser.add_argument('-i', '--indexing', help='Index a set of documents in the document storage', action='store_true')
    parser.add_argument('--path', help='The path to a directory with the documents to be indexed.')

    parser.add_argument('-q', '--query_mode', help='Answer a given query based on the indexed documents', action='store_true')
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

    settings = dict(DEFAULT_SETTINGS)
    for override in args.overrides:
        if '=' in override:
            key, value = override.split('=', 1)
            if key in settings:
                settings[key] = value
            else:
                print(f"Warning: '{key}' is not a valid setting key. Ignoring it.")
        else:
            print(f"Invalid format for argument: '{override}'. Expected format: key=value")

    if args.indexing:
        if args.path is None:
            print("Please specify the path containing the documents to index.")
            return
        pipeline = LocalJSONIndexingPipelineWrapper(settings, args.path)
        pipeline.build_pipeline()
        pipeline.run()

    if args.rag:
        if args.query is None:
            print("Please specify the query.")
            return
        pipeline = RagPipelineWrapper(settings, args.query)
        pipeline.build_pipeline()
        print(pipeline.run())

    if args.evaluation:
        evaluator = Evaluator(settings)
        print(evaluator.evaluate_rag_pipeline())

    if args.server:
        rag_pipeline = RagPipelineWrapper(settings)
        rag_pipeline.build_pipeline()
        app = FastAPI(title="RAG Pipeline PoC", description="An API server for querying the RAG pipeline.")

        @app.get("/query")
        def query_rag_pipeline(query: str):
            return rag_pipeline.run(query)

        @app.get("/indexing")
        def run_indexing_pipeline(document_path: str):
            indexing_pipeline = LocalJSONIndexingPipelineWrapper(settings, document_path)
            indexing_pipeline.build_pipeline()
            return indexing_pipeline.run()

        print(f"Starting FastAPI server on port {args.port}...")
        uvicorn.run(app, host="0.0.0.0", port=args.port)


if __name__ == "__main__":
    main()
