# Question Result:
# question_id uuid
# correct_answers int
# explanation str
# answers list[PlayerAnswer]

from pydantic import BaseModel


class QuestionResult(BaseModel):
    question_id: str
    correct_answers: int
    explanation: str
    answers: list[dict]