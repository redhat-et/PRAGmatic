from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack.components.joiners import DocumentJoiner
from haystack.components.rankers import TransformersSimilarityRanker
from haystack.utils import Secret
from haystack_integrations.components.retrievers.elasticsearch import ElasticsearchEmbeddingRetriever, \
    ElasticsearchBM25Retriever
from milvus_haystack import MilvusEmbeddingRetriever

from pipeline import CommonPipelineWrapper

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

class RagPipelineWrapper(CommonPipelineWrapper):
    def __init__(self, settings, query=None):
        super().__init__(settings)
        self._query = query

    def __init_sparse_retriever(self):
        vector_db_type = self._settings["vector_db_type"]
        document_store = self._init_document_store()
        if vector_db_type.lower() == "elasticsearch":
            ElasticsearchBM25Retriever(document_store=document_store, top_k=self._settings["elasticsearch_top_k"])

        raise ValueError(f"Unsupported vector DB type for sparse retrieval: {vector_db_type}")

    def __init_dense_retriever(self):
        vector_db_type = self._settings["vector_db_type"]
        document_store = self._init_document_store()
        if vector_db_type.lower() == "milvus":
            return MilvusEmbeddingRetriever(document_store=document_store, top_k=self._settings["top_k"])
        if vector_db_type.lower() == "elasticsearch":
            return ElasticsearchEmbeddingRetriever(document_store=document_store, top_k=self._settings["top_k"])

        raise ValueError(f"Unsupported vector DB type: {vector_db_type}")

    def _add_retrievers(self):
        sparse_retriever = None
        dense_retriever = None

        retriever_type = self._settings["retriever_type"]
        if retriever_type not in ["sparse", "dense", "hybrid"]:
            raise ValueError(f"Unsupported retrieval mode: {retriever_type}")

        if retriever_type in ["sparse", "hybrid"]:
            sparse_retriever = self.__init_sparse_retriever()
        if retriever_type in ["dense", "hybrid"]:
            dense_retriever = self.__init_dense_retriever()

        if retriever_type == "sparse":
            self._add_component("retriever", sparse_retriever, component_args={"query": self._query})
        elif retriever_type == "dense":
            self._add_embedder(self._query)
            self._add_component("retriever", dense_retriever)
        else:  # retriever_type == "hybrid"
            self._add_component("sparse_retriever", sparse_retriever, component_args={"query": self._query}, should_connect=False)
            self._add_embedder(self._query)
            self._add_component("dense_retriever", dense_retriever, should_connect=False)
            self._add_component("document_joiner", DocumentJoiner(), should_connect=False)

            # manually connect the components to create a hybrid retrieval topology
            self._pipeline.connect("embedder", "dense_retriever")
            self._pipeline.connect("sparse_retriever", "document_joiner")
            self._pipeline.connect("dense_retriever", "document_joiner")
            self._set_last_connect_point("document_joiner")

    def _add_ranker(self):
        if not self._settings["ranker_enabled"]:
            return
        ranker = TransformersSimilarityRanker(model=self._settings["ranking_model"])
        self._add_component("ranker", ranker, component_args={"query": self._query})

    def _add_prompt_builder(self):
        prompt_builder = PromptBuilder(template=BASE_RAG_PROMPT)
        self._add_component("prompt_builder", prompt_builder, component_args={"query": self._query},
                            component_to_connect_point="prompt_builder.documents")

    def _add_llm(self):
        llm = OpenAIGenerator(
            api_key=Secret.from_token("VLLM-PLACEHOLDER-API-KEY"),  # for compatibility with the OpenAI API
            model=self._settings["llm"],
            api_base_url=self._settings["vllm_base_url"],
            generation_kwargs={"max_tokens": 512}
        )
        self._add_component("llm", llm)

    def build_pipeline(self):
        self._add_retrievers()
        self._add_ranker()
        self._add_prompt_builder()
        self._add_llm()

    def run(self, query=None):
        if query is not None:
            # replace the query in the pipeline args
            for config_dict in self._args.values():
                for key in ["text", "query"]:
                    if key in config_dict:
                        config_dict[key] = query

        result = super().run()
        return result["llm"]["replies"][0]
