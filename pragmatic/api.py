from pragmatic.pipelines.utils import produce_custom_settings


def index_path_for_rag(path, **kwargs):
    from pragmatic.pipelines.indexing import LocalFileIndexingPipelineWrapper

    settings = produce_custom_settings(kwargs)
    pipeline = LocalFileIndexingPipelineWrapper(settings, path)
    pipeline.build_pipeline()
    return pipeline.run()

def execute_rag_query(query, **kwargs):
    from pragmatic.pipelines.rag import RagPipelineWrapper

    settings = produce_custom_settings(kwargs)
    pipeline = RagPipelineWrapper(settings, query)
    pipeline.build_pipeline()
    return pipeline.run()

def evaluate_rag_pipeline(**kwargs):
    from pragmatic.pipelines.evaluation import Evaluator

    settings = produce_custom_settings(kwargs)
    evaluator = Evaluator(settings)
    return evaluator.evaluate_rag_pipeline()


__all__ = ["index_path_for_rag",
           "execute_rag_query",
           # "evaluate_rag_pipeline"
           ]
