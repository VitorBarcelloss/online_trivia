from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.question_package import QuestionPackage


class QuestionPackageRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_packages(self, player_id: UUID | None = None) -> list[QuestionPackage]:
        query = self.session.query(QuestionPackage)

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

    def get_package_by_id(self, package_id: int) -> QuestionPackage | None:
        return self.session.query(QuestionPackage).filter_by(id=package_id).first()

    def get_by_author_and_name(self, author_id: UUID, name_key: str) -> QuestionPackage | None:
        return self.session.query(QuestionPackage).filter_by(
            author_id=author_id,
            name_key=name_key,
        ).first()

    def create_question_package(self, package: QuestionPackage) -> QuestionPackage:
        self.session.add(package)
        self.session.flush()
        self.session.refresh(package)
        return package

    def update_question_package(self, package: QuestionPackage) -> QuestionPackage:
        self.session.flush()
        self.session.refresh(package)
        return package

    def delete_question_package(self, package: QuestionPackage) -> None:
        self.session.delete(package)
        self.session.flush()