from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack.components.joiners import DocumentJoiner
from haystack.components.rankers import TransformersSimilarityRanker
from haystack.utils import Secret
from haystack_integrations.document_stores.elasticsearch import ElasticsearchDocumentStore
from haystack import Pipeline
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack_integrations.components.retrievers.elasticsearch import ElasticsearchEmbeddingRetriever, \
    ElasticsearchBM25Retriever

from settings import DEFAULT_SETTINGS

BASE_RAG_PROMPT = """You are an assistant for question-answering tasks. 

    Here is the context to use to answer the question:

    {% for document in documents %}
        {{document.content}}
    {% endfor %}

    Think carefully about the above context. 

    Now, review the user question:

    {{query}}

    Provide an answer to this questions using only the above context. 

    Answer:
    """

def run_rag_pipeline(query, settings=DEFAULT_SETTINGS):
    # text_embedder = SentenceTransformersTextEmbedder(model=settings["embedding_model"])

    document_store = ElasticsearchDocumentStore(hosts=settings["elasticsearch_host_url"],
                                                basic_auth=(settings["elasticsearch_user"], settings["elasticsearch_password"]),
                                                index=settings["elasticsearch_index_name"])
    bm25_retriever = ElasticsearchBM25Retriever(document_store=document_store, top_k=settings["elasticsearch_top_k"])
    # embedding_retriever = ElasticsearchEmbeddingRetriever(document_store=document_store, top_k=settings["elasticsearch_top_k"])

    # document_joiner = DocumentJoiner()

    # ranker = TransformersSimilarityRanker(model=settings["ranking_model"])

    prompt_builder = PromptBuilder(template=BASE_RAG_PROMPT)
    llm = OpenAIGenerator(
        api_key=Secret.from_token("VLLM-PLACEHOLDER-API-KEY"),  # for compatibility with the OpenAI API
        model=settings["llm"],
        api_base_url=settings["vllm_base_url"],
        generation_kwargs={"max_tokens": 512}
    )

    pipeline = Pipeline()
    # pipeline.add_component("text_embedder", text_embedder)
    # pipeline.add_component("embedding_retriever", embedding_retriever)
    pipeline.add_component("bm25_retriever", bm25_retriever)
    # pipeline.add_component("document_joiner", document_joiner)
    # pipeline.add_component("ranker", ranker)
    pipeline.add_component("prompt_builder", prompt_builder)
    pipeline.add_component("llm", llm)

    # pipeline.connect("text_embedder", "embedding_retriever")
    # pipeline.connect("bm25_retriever", "document_joiner")
    # pipeline.connect("embedding_retriever", "document_joiner")
    # pipeline.connect("document_joiner", "ranker")
    # pipeline.connect("ranker", "prompt_builder.documents")
    pipeline.connect("bm25_retriever", "prompt_builder.documents")
    pipeline.connect("prompt_builder", "llm")

    result = pipeline.run({  # "text_embedder": {"text": query},
                           "bm25_retriever": {"query": query},
                           # "ranker": {"query": query},
                           "prompt_builder": {"query": query}})
    return result["llm"]["replies"][0]
