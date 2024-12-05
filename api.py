from evaluation import Evaluator
from indexing import LocalJSONIndexingPipelineWrapper
from rag import RagPipelineWrapper
from utils import produce_custom_settings


def index_path_for_rag(path, **kwargs):
    settings = produce_custom_settings(kwargs)
    pipeline = LocalJSONIndexingPipelineWrapper(settings, path)
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
