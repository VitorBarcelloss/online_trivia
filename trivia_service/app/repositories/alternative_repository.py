from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.alternative import Alternative
from app.models.question import Question
from app.models.question_package import QuestionPackage


class AlternativeRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_alternatives(self, question_id: int, player_id: UUID | None = None) -> list[Alternative]:
        query = self.session.query(Alternative).filter(Alternative.question_id == question_id)

        query = query.join(Question).join(Question.package)
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

    def get_alternative_by_id(self, alternative_id: int, player_id: UUID | None = None) -> Alternative | None:
        query = self.session.query(Alternative).filter(Alternative.id == alternative_id)

        query = query.join(Question).join(Question.package)
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

    def get_duplicate(self, question_id: int, text: str) -> Alternative | None:
        return self.session.query(Alternative).filter_by(
            question_id=question_id,
            text=text,
        ).first()

    def create_alternative(self, alternative: Alternative) -> Alternative:
        self.session.add(alternative)
        self.session.flush()
        self.session.refresh(alternative)
        return alternative

    def update_alternative(self, alternative: Alternative) -> Alternative:
        self.session.flush()
        self.session.refresh(alternative)
        return alternative

    def delete_alternative(self, alternative: Alternative) -> None:
        self.session.delete(alternative)
        self.session.flush()