from pragmatic.pipelines.indexing import LocalFileIndexingPipelineWrapper
from pragmatic.pipelines.rag import RagPipelineWrapper
from pragmatic.pipelines.utils import produce_custom_settings

def create_index_pipeline(path, **kwargs):
    settings = produce_custom_settings(kwargs)
    index_pipeline = LocalFileIndexingPipelineWrapper(settings, path)
    index_pipeline.build_pipeline()
    return index_pipeline

def create_rag_pipeline(**kwargs):
    settings = produce_custom_settings(kwargs)
    rag_pipeline = RagPipelineWrapper(settings)
    rag_pipeline.build_pipeline()
    return rag_pipeline

def indexing_for_rag(index_pipeline, **kwargs):
    return index_pipeline.run()

def execute_rag_query(rag_pipeline, query, **kwargs):
    return rag_pipeline.run(query)

def evaluate_rag_pipeline(**kwargs):
    from pragmatic.pipelines.evaluation import Evaluator

    settings = produce_custom_settings(kwargs)
    evaluator = Evaluator(settings)
    return evaluator.evaluate_rag_pipeline()


__all__ = ["create_index_pipeline",
           "create_rag_pipeline",
           "indexing_for_rag",
           "execute_rag_query",
           # "evaluate_rag_pipeline"
        ]
