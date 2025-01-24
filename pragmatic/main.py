import argparse

from api import create_index_pipeline, create_rag_pipeline, indexing_for_rag, execute_rag_query, evaluate_rag_pipeline
from settings import DEFAULT_SETTINGS


def main():
    """
    The tool can be executed in one of the following modes:
    1) Index pipeline creation mode (-ip flag) - create an indexing pipeline from the given path.
    2) RAG pipeline creatioon mode (-rp flag) - create a RAG pipeline
    3) Indexing mode (-i flag) - index a collection of documents from the given path.
    4) RAG query mode (-r flag) - answer a given query with RAG using the previously indexed documents.
    5) Evaluation mode (-e flag) - evaluate the RAG pipeline as specified in the settings - NOT YET OFFICIALLY SUPPORTED.
    """
    parser = argparse.ArgumentParser(description='RAG Pipeline PoC')

    parser.add_argument('-ip', '--indexpipeline', help='Initialize an indexing pipeline', action='store_true')
    parser.add_argument('--path', help='The path to a directory with the documents to be indexed.')

    parser.add_argument('-i', '--indexing', help='Index a set of documents in the document storage', action='store_true')
    parser.add_argument('--pipeline', help='Provide the relevant pipeline for running the task, if pipeline not created initialize either index/rag pipeline depending on your task')

    parser.add_argument('-rp', '--ragpipeline', help='Initialize a RAG pipeline', action='store_true')

    parser.add_argument('-r', '--rag', help='Answer a given query based on the indexed documents', action='store_true')
    parser.add_argument('--query', help='The query for the language model to answer.')

    parser.add_argument('-e', '--evaluation', help='Evaluate the RAG pipeline', action='store_true')

    # Positional arguments to capture overrides of default settings
    parser.add_argument('overrides', nargs='*', help="Optionally override default settings as key=value")

    args = parser.parse_args()

    if sum([args.indexpipeline, args.ragpipeline, args.indexing, args.rag, args.evaluation, args.server]) != 1:
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

    if args.indexpipeline:
        if args.path is None:
            print("Please specify the path containing the documents to index.")
            return
        create_index_pipeline(args.path, **custom_settings)
    
    if args.indexing:
        if args.pipeline is None:
            print("Please specify a relevant pipeline for running the task")
            return
        indexing_for_rag(args.pipeline, **custom_settings)

    if args.ragpipeline:
        create_rag_pipeline(**custom_settings)

    if args.rag:
        if args.query is None:
            print("Please specify the query.")
            return
        if args.pipeline is None:
            print("Please specify a relevant pipeline for running the task")
            return
        print(execute_rag_query(args.pipeline, args.query, **custom_settings))

    if args.evaluation:
        print(evaluate_rag_pipeline(**custom_settings))


if __name__ == "__main__":
    main()
