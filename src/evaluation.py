import json

from src.indexing import LocalFileIndexingPipelineWrapper
from src.pipeline import CommonPipelineWrapper
from haystack_integrations.components.evaluators.ragas import RagasEvaluator

from src.rag import RagPipelineWrapper


class RagasEvaluationPipelineWrapper(CommonPipelineWrapper):

    def __init__(self, settings, eval_params):
        super().__init__(settings)

        # we assume settings["eval_ragas_metrics"] to contain a dict with two entries:
        # 1) "params" - contains a dict of static parameters for the metric;
        # 2) "required_data" - contains a list of parameters out of 'questions', 'contexts', 'responses' and 'ground truths'
        # specifying the data required for the given metric.
        self._metric_params = {}
        self._metric_data = {}
        for metric_name, metric_settings in self._settings["eval_ragas_metrics"].items():
            self._metric_params[metric_name] = metric_settings["params"]
            self._metric_data[metric_name] = {key: eval_params[key] for key in metric_settings["required_data"]}

    def _add_evaluators(self):
        for metric_name in self._metric_params.keys():
            evaluator = RagasEvaluator(metric=metric_name, metric_params=self._metric_params[metric_name])
            self._add_component(f"evaluator_{metric_name}", evaluator, component_args=self._metric_data[metric_name], should_connect=False)

    def build_pipeline(self):
        self._add_evaluators()


class Evaluator(object):

    def __init__(self, settings):
        self._settings = settings
        self._questions, self._ground_truth_answers = self._load_questions_and_answers()

        self._indexing_pipeline = LocalFileIndexingPipelineWrapper(settings, settings["eval_documents_path"])
        self._rag_pipeline = RagPipelineWrapper(settings, evaluation_mode=True)

        for pipeline in [self._indexing_pipeline, self._rag_pipeline]:
            pipeline.build_pipeline()

    def _load_questions_and_answers(self):
        # for now, we assume the questions & answers file to have this specific format
        with open(self._settings["eval_questions_answers_path"], "r") as f:
            data = json.load(f)
            questions = data["questions"]
            answers = data["ground_truths"]
        return questions, answers

    def _run_rag_pipeline_on_eval_questions(self):
        contexts = []
        responses = []
        for question in self._questions:
            response = self._rag_pipeline.run(query=question)
            contexts.append([d.content for d in response.documents])
            responses.append(response.data)
        return contexts, responses

    def evaluate_rag_pipeline(self):
        self._indexing_pipeline.run()

        contexts, responses = self._run_rag_pipeline_on_eval_questions()

        eval_params = {
            "questions": self._questions,
            "contexts": contexts,
            "responses": responses,
            "ground_truths": self._ground_truth_answers,
        }
        eval_pipeline = RagasEvaluationPipelineWrapper(self._settings, eval_params)
        eval_pipeline.build_pipeline()

        return eval_pipeline.run()
