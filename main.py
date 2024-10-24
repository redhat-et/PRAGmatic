import argparse

from indexing import run_indexing_pipeline
from rag import run_rag_pipeline
from settings import DEFAULT_SETTINGS


def main():
    parser = argparse.ArgumentParser(description='RAG Pipeline PoC')

    parser.add_argument('-i', '--indexing', help='Index a set of documents in the document storage', action='store_true')

    parser.add_argument('-r', '--rag', help='Answer a given query based on the indexed documents', action='store_true')
    parser.add_argument('--query', help='The query for the language model to answer.')

    # Positional arguments to capture overrides of default settings
    parser.add_argument('overrides', nargs='*', help="Optionally override default settings as key=value")

    args = parser.parse_args()
    if args.indexing and args.rag:
        print("Wrong usage: cannot run in indexing mode and RAG mode at the same time.")
        return

    if not args.indexing and not args.rag:
        print("Wrong usage: either indexing mode or RAG mode must be specified.")
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
        run_indexing_pipeline(settings)
    else:
        print(run_rag_pipeline(args.query, settings))


if __name__ == "__main__":
    main()
