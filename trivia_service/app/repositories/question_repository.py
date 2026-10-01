from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.question import Question
from app.models.question_package import QuestionPackage


class QuestionRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_questions(self, package_id: int, player_id: UUID | None = None) -> list[Question]:
        query = self.session.query(Question).join(Question.package).filter(
            Question.package_id == package_id
        )
        if player_id is None:
            query = query.filter(QuestionPackage.is_public.is_(True))
        else:
            query = query.filter(
                or_(
                    QuestionPackage.is_public.is_(True),
                    QuestionPackage.author_id == player_id,
                )
            )
        return query.all()

    def get_question_by_id(
        self,
        question_id: int,
        player_id: UUID | None = None,
    ) -> Question | None:
        query = self.session.query(Question).join(Question.package).filter(
            Question.id == question_id
        )
        if player_id is None:
            query = query.filter(QuestionPackage.is_public.is_(True))
        else:
            query = query.filter(
                or_(
                    QuestionPackage.is_public.is_(True),
                    QuestionPackage.author_id == player_id,
                )
            )
        return query.first()

    def get_package_by_id(self, package_id: int) -> QuestionPackage | None:
        return self.session.query(QuestionPackage).filter_by(id=package_id).first()

    def get_duplicate(self, package_id: int, statement: str) -> Question | None:
        return self.session.query(Question).filter_by(
            package_id=package_id,
            statement=statement,
        ).first()

    def create_question(self, question: Question) -> Question:
        self.session.add(question)
        self.session.flush()
        self.session.refresh(question)
        return question

    def update_question(self, question: Question) -> Question:
        self.session.add(question)
        self.session.flush()
        self.session.refresh(question)
        return question

    def delete_question(self, question: Question) -> None:
        self.session.delete(question)
        self.session.flush()