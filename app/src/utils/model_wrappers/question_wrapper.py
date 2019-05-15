from typing import Optional, Union, cast
import src.models.question_model as qm


class QuestionWrapper:

    def __init__(self, question: Optional["qm.Question"]) -> None:
        self.question = question
    
    @property
    def question(self) -> "qm.Question":
        return self._question
    
    @question.setter
    def question(self, question: Union[str, "qm.Question"]) -> None:

        if isinstance(question, str):
            question = qm.Question.nodes.get(question)

        question = cast(qm.Question, question)
        self._question = question