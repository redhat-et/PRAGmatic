from paragon.pipelines.evaluation import Evaluator
from paragon.pipelines.indexing import LocalFileIndexingPipelineWrapper
from paragon.pipelines.rag import RagPipelineWrapper
from paragon.pipelines.utils import produce_custom_settings


def index_path_for_rag(path, **kwargs):
    settings = produce_custom_settings(kwargs)
    pipeline = LocalFileIndexingPipelineWrapper(settings, path)
    pipeline.build_pipeline()
    return pipeline.run()

def execute_rag_query(query, **kwargs):
    settings = produce_custom_settings(kwargs)
    pipeline = RagPipelineWrapper(settings, query)
    pipeline.build_pipeline()
    return pipeline.run()

def evaluate_rag_pipeline(**kwargs):
    settings = produce_custom_settings(kwargs)
    evaluator = Evaluator(settings)
    return evaluator.evaluate_rag_pipeline()


__all__ = ["index_path_for_rag",
           "execute_rag_query",
           # "evaluate_rag_pipeline"
           ]
