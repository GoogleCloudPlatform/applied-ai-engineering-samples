
from abc import ABC, abstractmethod

class Evaluator(ABC):
    CRITERIA: dict[str, str]

    @abstractmethod
    def evaluate_response(self, response: str, question_asked: str, true_answer: str) -> int: ...