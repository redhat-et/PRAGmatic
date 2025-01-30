from haystack.components.builders import PromptBuilder, AnswerBuilder
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack.components.generators import OpenAIGenerator
from haystack.components.joiners import DocumentJoiner
from haystack.components.rankers import TransformersSimilarityRanker
from haystack.utils import Secret
# from haystack_integrations.components.retrievers.elasticsearch import ElasticsearchEmbeddingRetriever, \
#    ElasticsearchBM25Retriever
from milvus_haystack import MilvusEmbeddingRetriever
from openai import OpenAI

from pragmatic.pipelines.pipeline import CommonPipelineWrapper
from pragmatic.pipelines.streaming import RagStreamHandler

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
    def __init__(self, settings, query=None, evaluation_mode=False):
        super().__init__(settings)
        self._query = query
        self._evaluation_mode = evaluation_mode

        self._streaming_handler = RagStreamHandler(settings)

    def _add_embedder(self, query):
        embedder = SentenceTransformersTextEmbedder(model=self._settings["embedding_model_path"])
        self._add_component("embedder", embedder, component_args={"text": query})

    def __init_sparse_retriever(self):
        vector_db_type = self._settings["vector_db_type"]
        document_store = self._init_document_store(retrieval_mode=True)
        # if vector_db_type.lower() == "elasticsearch":
        #    return ElasticsearchBM25Retriever(document_store=document_store, top_k=self._settings["elasticsearch_top_k"])

        raise ValueError(f"Unsupported vector DB type for sparse retrieval: {vector_db_type}")

    def __init_dense_retriever(self):
        vector_db_type = self._settings["vector_db_type"]
        document_store = self._init_document_store(retrieval_mode=True)
        if vector_db_type.lower() == "milvus":
            return MilvusEmbeddingRetriever(document_store=document_store, top_k=self._settings["top_k"])
        # if vector_db_type.lower() == "elasticsearch":
        #    return ElasticsearchEmbeddingRetriever(document_store=document_store, top_k=self._settings["top_k"])

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
            self._add_component("retriever", dense_retriever,
                                component_from_connect_point="embedder.embedding",
                                component_to_connect_point="retriever.query_embedding")
        else:  # retriever_type == "hybrid"
            self._add_component("sparse_retriever", sparse_retriever, component_args={"query": self._query},
                                should_connect=False)
            self._add_embedder(self._query)
            self._add_component("dense_retriever", dense_retriever, should_connect=False)
            self._add_component("document_joiner", DocumentJoiner(), should_connect=False)

            # manually connect the components to create a hybrid retrieval topology
            self._pipeline.connect("embedder.embedding", "dense_retriever.query_embedding")
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
        if "generator_object" in self._settings and self._settings["generator_object"] is not None:
            # an object to use for communicating with the model was explicitly specified and we should use it
            self._add_component("llm", self._settings["generator_object"])
            return
        
        custom_callback = (
            self._streaming_handler._streaming_callback
            if self._settings.get("enable_response_streaming") else None
        )

        llm = OpenAIGenerator(
            api_key=self._settings["llm_api_key"],
            model=self._settings["llm"],
            api_base_url=self._settings["llm_base_url"],
            timeout=self._settings["llm_connection_timeout"],
            max_retries=self._settings["llm_connection_max_retries"],
            system_prompt=self._settings["llm_system_prompt"],
            organization=self._settings["llm_organization"],
            streaming_callback=custom_callback,
            generation_kwargs={
                "max_tokens": self._settings["llm_response_max_tokens"],
                "temperature": self._settings["llm_temperature"],
                "top_p": self._settings["llm_top_p"],
                "n": self._settings["llm_num_completions"],
                "stop": self._settings["llm_stop_sequences"],
                "frequency_penalty": self._settings["llm_frequency_penalty"],
                "presence_penalty": self._settings["llm_presence_penalty"],
                "logit_bias": self._settings["llm_logit_bias"],
            }
        )
        if "llm_http_client" in self._settings and self._settings["llm_http_client"] is not None:
            # Haystack does not support setting the HTTP client directly, so we need to redefine the OpenAI object
            llm.client = OpenAI(api_key=self._settings["llm_api_key"],
                                organization=self._settings["llm_organization"],
                                base_url=self._settings["llm_base_url"],
                                timeout=self._settings["llm_connection_timeout"],
                                max_retries=self._settings["llm_connection_max_retries"],
                                http_client=self._settings["llm_http_client"])
        self._add_component("llm", llm)

    def _add_answer_builder(self):
        if not self._evaluation_mode:
            return
        self._add_component("answer_builder", AnswerBuilder(), component_args={"query": self._query},
                            should_connect=False)
        self._pipeline.connect("llm.replies", "answer_builder.replies")
        self._pipeline.connect("retriever", "answer_builder.documents")

    def build_pipeline(self):
        self._add_retrievers()
        self._add_ranker()
        self._add_prompt_builder()
        self._add_llm()
        self._add_answer_builder()

    def get_evaluation_mode(self):
        return self._evaluation_mode

    def set_evaluation_mode(self, new_evaluation_mode):
        should_rebuild_pipeline = not self._evaluation_mode and new_evaluation_mode
        self._evaluation_mode = new_evaluation_mode
        if should_rebuild_pipeline:
            self._rebuild_pipeline()

    def run(self, query=None):
        """
            Executes a query against the pipeline.

            If response enable_response_streaming is enabled, returns a generator that yields chunks of the response.
            Otherwise, returns a string with the final response.

            If evaluation mode is enabled, the response is retrieved from the answer builder instead of the standard pipeline output.

            Parameters:
                query (str, optional): The input query string to be processed.

            Returns:
                str | generator: A string when enable_response_streaming is False or a generator when enable_response_streaming is True.
        """
        # If a query is provided, update the relevant keys in the pipeline arguments
        if query:
            for config_dict in self._args.values():
                for key in ["text", "query"]:
                    if key in config_dict:
                        config_dict[key] = query

        # Handle incompatible settings 
        if self._settings.get("enable_response_streaming", False) and self._evaluation_mode:
            raise ValueError("Evaluation mode does not support streaming replies.")

        # Handle streaming mode if enabled
        if self._settings.get("enable_response_streaming", False):
            self._streaming_handler.start_stream(lambda: super(RagPipelineWrapper, self).run())
            return self._streaming_handler.stream_chunks()

        # Otherwise, execute a normal pipeline run 
        result = super().run()

        #  # In evaluation mode, return the answer from the answer builder in string format
        if self._evaluation_mode:
            return result.get("answer_builder", {}).get("answers", [""])[0]
        
        # Return the final LLM reply in string format
        return result.get("llm", {}).get("replies", [""])[0]

