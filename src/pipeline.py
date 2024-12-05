from abc import ABC

from haystack import Pipeline
from haystack.components.embedders import SentenceTransformersTextEmbedder
# from haystack_integrations.document_stores.elasticsearch import ElasticsearchDocumentStore
from milvus_haystack import MilvusDocumentStore


class PipelineWrapper(object):
    def __init__(self):
        self._reset_pipeline()

    def get_pipeline(self):
        return self._pipeline

    def get_pipeline_args(self):
        return self._args

    def _reset_pipeline(self):
        self._pipeline = Pipeline()
        self._args = {}
        self.__last_connect_point = None

    def _rebuild_pipeline(self):
        self._reset_pipeline()
        self.build_pipeline()

    def _add_component(self, component_name, component_obj, component_args=None, should_connect=True,
                       component_from_connect_point=None, component_to_connect_point=None):
        self._pipeline.add_component(component_name, component_obj)
        if component_args is not None:
            self._args[component_name] = component_args

        if not should_connect:
            return

        actual_from_connect_point = component_from_connect_point if component_from_connect_point is not None else component_name
        actual_to_connect_point = component_to_connect_point if component_to_connect_point is not None else component_name

        if self.__last_connect_point is not None:
            # this is not the first pipeline component - a link has to be created
            self._pipeline.connect(self.__last_connect_point, actual_to_connect_point)
        self.__last_connect_point = actual_from_connect_point

    def _set_last_connect_point(self, connect_point):
        self.__last_connect_point = connect_point

    def run(self):
        return self._pipeline.run(self._args)

    def build_pipeline(self):
        raise NotImplementedError()


class CommonPipelineWrapper(PipelineWrapper, ABC):
    def __init__(self, settings):
        super().__init__()
        self._settings = settings

    def _add_embedder(self, query=None):
        embedder = SentenceTransformersTextEmbedder(model=self._settings["embedding_model"])
        args = None if query is None else {"text": query}
        self._add_component("embedder", embedder, component_args=args)

    def _init_document_store(self):
        vector_db_type = self._settings["vector_db_type"]

        if vector_db_type.lower() == "milvus":
            milvus_deployment_type = self._settings["milvus_deployment_type"]
            if milvus_deployment_type.lower() == "lite":
                milvus_connection_args = self._settings["milvus_file_path"]
            elif milvus_deployment_type.lower() == "standalone":
                milvus_connection_args = self._settings["milvus_server_url"]
            else:
                raise ValueError(f"Unsupported Milvus deployment type: {milvus_deployment_type}")
            return MilvusDocumentStore(connection_args=milvus_connection_args, drop_old=self._settings["drop_old_collection"])

        #if vector_db_type.lower() == "elasticsearch":
        #    return ElasticsearchDocumentStore(hosts=self._settings["elasticsearch_host_url"],
        #                                      basic_auth=(self._settings["elasticsearch_user"], self._settings["elasticsearch_password"]),
        #                                      index=self._settings["elasticsearch_index_name"])

        raise ValueError(f"Unsupported vector DB type: {vector_db_type}")
