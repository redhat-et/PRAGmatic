from abc import ABC

from haystack import Pipeline
# from haystack_integrations.document_stores.elasticsearch import ElasticsearchDocumentStore
from milvus_haystack import MilvusDocumentStore

import logging

logger = logging.getLogger(__name__)


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
        logger.debug(f"Adding component {component_name} with the following args: {component_args}")
        self._pipeline.add_component(component_name, component_obj)
        if component_args is not None:
            self._args[component_name] = component_args

        if not should_connect:
            return

        actual_from_connect_point = component_from_connect_point if component_from_connect_point is not None else self.__last_connect_point
        actual_to_connect_point = component_to_connect_point if component_to_connect_point is not None else component_name

        if self.__last_connect_point is not None:
            # this is not the first pipeline component - a link has to be created
            logger.debug(f"Adding pipeline connection: {actual_from_connect_point} -> {actual_to_connect_point}")
            self._pipeline.connect(actual_from_connect_point, actual_to_connect_point)
        self.__last_connect_point = component_name

    def _set_last_connect_point(self, connect_point):
        self.__last_connect_point = connect_point

    def run(self, pipeline_args_dict=None):
        if pipeline_args_dict:
            logger.debug(f"Executing the pipeline with the following arguments:\n{pipeline_args_dict}")
            return self._pipeline.run(pipeline_args_dict)
        else:
            return self._pipeline.run(self._args)

    def build_pipeline(self):
        raise NotImplementedError()


class CommonPipelineWrapper(PipelineWrapper, ABC):
    DEFAULT_LOCAL_MILVUS_INDEX_SETTINGS = {
        "metric_type": "L2",
        "index_type": "IVF_FLAT",
        "params": {"M": 8, "efConstruction": 64},
    }

    def __init__(self, settings):
        super().__init__()
        self._settings = settings

    def _init_document_store(self, retrieval_mode=True):
        vector_db_type = self._settings["vector_db_type"]

        if vector_db_type.lower() == "milvus":
            milvus_deployment_type = self._settings["milvus_deployment_type"]
            if milvus_deployment_type.lower() == "lite":
                milvus_connection_args = {"uri": self._settings["milvus_file_path"]}
            elif milvus_deployment_type.lower() == "standalone":
                milvus_connection_args = {"uri": self._settings["milvus_server_url"]}
            else:
                raise ValueError(f"Unsupported Milvus deployment type: {milvus_deployment_type}")

            if "milvus_auth_token" in self._settings and self._settings["milvus_auth_token"] is not None:
                milvus_connection_args["token"] = self._settings["milvus_auth_token"]

            drop_old = False if retrieval_mode else self._settings["milvus_drop_old_collection"]

            # This is a workaround over an issue with the milvus-haystack integration component. When no index parameters are
            # provided, MilvusDocumentStore tries to create a HNSW index, which is not supported in Lite mode. Thus, when
            # Lite mode is desired, we have to provide our own index parameters.
            index_params = CommonPipelineWrapper.DEFAULT_LOCAL_MILVUS_INDEX_SETTINGS \
                if self._settings["milvus_deployment_type"] == 'lite' else None

            return MilvusDocumentStore(connection_args=milvus_connection_args,
                                       collection_name=self._settings["milvus_collection_name"],
                                       timeout=self._settings["milvus_connection_timeout"],
                                       drop_old=drop_old,
                                       index_params=index_params)

        # if vector_db_type.lower() == "elasticsearch":
        #    return ElasticsearchDocumentStore(hosts=self._settings["elasticsearch_host_url"],
        #                                      basic_auth=(self._settings["elasticsearch_user"], self._settings["elasticsearch_password"]),
        #                                      index=self._settings["elasticsearch_index_name"])

        raise ValueError(f"Unsupported vector DB type: {vector_db_type}")
