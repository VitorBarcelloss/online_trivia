import httpx
from app.domain.entities.game_question import GameQuestion

class TriviaClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        
    async def get_questions(self, package_id: str) -> list[GameQuestion]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/{package_id}/game-questions"
                )
            response.raise_for_status()
            
            data = response.json()
            questions = [
                GameQuestion(
                    id=question["question_id"],
                    order=index,
                    statement=question["statement"],
                    options=question["alternatives"],
                    correct_answer=question["correct_answer"],
                    explanation=question.get("explanation")
                )
                for index, question in enumerate(data)
            ]
            
            return questions