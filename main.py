import argparse

from fastapi import FastAPI
from langchain_core.runnables import chain
from langserve import add_routes
import uvicorn

from pydantic import BaseModel, Field

from contexters.BasicContexter import BasicContexter
from generators.BasicLLMGenerator import BasicLLMGenerator
from graph import GraphBuilder
from retrievers.ElasticsearchRetriever import ElasticsearchRetriever
from settings import DEFAULT_SETTINGS


class GraphExecutionParams(BaseModel):
    query: str
    llm_path: str = Field(default=DEFAULT_SETTINGS["llm_path"])

    elasticsearch_host_url: str = Field(default=DEFAULT_SETTINGS["elasticsearch_host_url"])
    elasticsearch_index_name: str = Field(default=DEFAULT_SETTINGS["elasticsearch_index_name"])
    elasticsearch_top_k: int = Field(default=DEFAULT_SETTINGS["elasticsearch_top_k"])


def execute_graph(params):
    try:
        retriever = ElasticsearchRetriever(params["elasticsearch_host_url"],
                                           params["elasticsearch_index_name"],
                                           params["elasticsearch_top_k"])
        contexter = BasicContexter()
        generator = BasicLLMGenerator(params["llm_path"], {"trust_remote_code": True})
        graph = GraphBuilder(retriever, contexter, generator).create_graph()

        return graph.invoke(params["query"])

    except Exception as e:
        return f"Graph execution failed: {str(e)}"

@chain
def langchain_execute_graph(params: GraphExecutionParams):
    return execute_graph(params)

def ui_main():
    app = FastAPI(title="RAG LangChain Server", version="1.0", description="A simple RAG API server")
    add_routes(app, langchain_execute_graph, path="/chain")
    uvicorn.run(app, host="localhost", port=8000)

def cl_main(**kwargs):
    print(execute_graph(kwargs))

def main():
    parser = argparse.ArgumentParser(description='RAG Pipeline PoC')

    parser.add_argument('-i', '--interactive', help='Get runtime parameters via the web UI', action='store_true')
    parser.add_argument('--query', help='The query for the language model to answer.')

    parser.add_argument('--llm-path', help='The LLM to be used.', default=DEFAULT_SETTINGS["llm_path"])

    # Elasticsearch params
    parser.add_argument('--elasticsearch-host-url', help='The URL of the running Elasticsearch instance.',
                        default=DEFAULT_SETTINGS["elasticsearch_host_url"])
    parser.add_argument('--elasticsearch-index-name', help='The name of the Elasticsearch index to use.',
                        default=DEFAULT_SETTINGS["elasticsearch_index_name"])
    parser.add_argument('--elasticsearch-top-k', help='Number of documents to fetch from Elasticsearch.',
                        type=int, default=DEFAULT_SETTINGS["elasticsearch_top_k"])

    args = parser.parse_args()
    if args.interactive:
        ui_main()
    else:
        cl_main(query=args.query, llm_path=args.llm_path,
                elasticsearch_host_url=args.elasticsearch_host_url,
                elasticsearch_index_name=args.elasticsearch_index_name,
                elasticsearch_top_k=args.elasticsearch_top_k)


if __name__ == "__main__":
    main()
