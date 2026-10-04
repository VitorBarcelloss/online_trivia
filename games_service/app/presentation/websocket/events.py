from typing import Literal

from pydantic import BaseModel


# Client → Server


class SubmitAnswerEvent(BaseModel):
    type: Literal["submit_answer"]
    answer: str


class FinishGameEvent(BaseModel):
    type: Literal["finish_game"]


# Server → Client


class GameStartedEvent(BaseModel):
    type: Literal["game_started"]
    game_id: str


class QuestionStartedEvent(BaseModel):
    type: Literal["question_started"]
    question: dict


class AnswerSubmittedEvent(BaseModel):
    type: Literal["answer_submitted"]


class QuestionResolvedEvent(BaseModel):
    type: Literal["question_resolved"]
    question_id: str
    correct_answer: str
    explanation: str


class RankingUpdatedEvent(BaseModel):
    type: Literal["ranking_updated"]
    ranking: list[dict]


class NextQuestionEvent(BaseModel):
    type: Literal["next_question"]
    question: dict


class GameFinishedEvent(BaseModel):
    type: Literal["game_finished"]
    ranking: list[dict]


class PlayerJoinedEvent(BaseModel):
    type: Literal["player_joined"]
    player: dict


class PlayerLeftEvent(BaseModel):
    type: Literal["player_left"]
    player_id: str


class ErrorEvent(BaseModel):
    type: Literal["error"]
    message: str