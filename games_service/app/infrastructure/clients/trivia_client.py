
import httpx

from app.domain.entities.game_question import GameQuestion


class TriviaClient:

    def __init__(
        self,
        base_url: str,
    ):
        self.base_url = base_url

    async def get_questions(
        self,
        package_id: int,
    ) -> list[GameQuestion]:

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/{package_id}/game-questions"
            )

            response.raise_for_status()

            data = response.json()

        questions: list[GameQuestion] = []

        for index, question in enumerate(data):
            alternatives = question.get(
                "alternatives",
                [],
            )

            options = [
                alternative["text"]
                for alternative in alternatives
            ]

            questions.append(
                GameQuestion(
                    id=str(question["question_id"]),
                    order=index,
                    statement=question["statement"],
                    options=options,
                    correct_answer=str(
                        question["correct_answer"]
                    ),
                    explanation=(
                        question.get("explanation")
                        or ""
                    ),
                )
            )

        return questions
