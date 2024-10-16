import os

from .evaluator import Evaluator

from langchain.evaluation import load_evaluator
from langchain_google_vertexai import ChatVertexAI

class GoogleEvaluator(Evaluator):
    DEFAULT_MODEL_KWARGS: dict = dict(temperature=0)
    CRITERIA = {"accuracy": """
                Score 1: The answer is completely unrelated to the reference.
                Score 3: The answer has minor relevance but does not align with the reference.
                Score 5: The answer has moderate relevance but contains inaccuracies.
                Score 7: The answer aligns with the reference but has minor omissions.
                Score 10: The answer is completely accurate and aligns perfectly with the reference.
                Only respond with a numberical score"""}

    def __init__(self,
                 project_id: str,
                 model_name: str = "gemini-1.5-pro",
                 model_kwargs: dict = DEFAULT_MODEL_KWARGS):
        """
        :param project_id: ID of the google cloud platform project to use
        :param model_name: The name of the model.
        :param model_kwargs: Model configuration. Default is {temperature: 0}
        """
        self.model_name = model_name
        self.model_kwargs = model_kwargs
        self.evaluator = ChatVertexAI(model=self.model_name, **self.model_kwargs)

    def evaluate_response(self, response: str, question_asked: str, true_answer: str) -> int:
        evaluator = load_evaluator(
            "labeled_score_string",
            criteria=self.CRITERIA,
            llm=self.evaluator,
        )

        eval_result = evaluator.evaluate_strings(
            # The models response
            prediction=response,

            # The actual answer
            reference=true_answer,

            # The question asked
            input=question_asked,
        )

        return int(eval_result['score'])
