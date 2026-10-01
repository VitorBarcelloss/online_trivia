from uuid import UUID

from app.dtos.alternative import AlternativeDTO
from app.core.exceptions import TriviaErrorMessages, TriviaException
from app.models.alternative import Alternative


class AlternativeService:
	def __init__(self, alternative_repository):
		self.alternative_repository = alternative_repository

	def get_alternatives(
		self,
		question_id: int,
		player_id: UUID | None = None,
	) -> list[AlternativeDTO]:
		alternatives = self.alternative_repository.get_alternatives(question_id, player_id)

		if not alternatives:
			raise TriviaException(TriviaErrorMessages.ALTERNATIVE_NOT_FOUND)

		return [self._from_entity_to_dto(alternative) for alternative in alternatives]

	def get_alternative(
		self,
		alternative_id: int,
		player_id: UUID | None = None,
	) -> AlternativeDTO:
		alternative = self.alternative_repository.get_alternative_by_id(alternative_id, player_id)

		if not alternative:
			raise TriviaException(TriviaErrorMessages.ALTERNATIVE_NOT_FOUND)

		return self._from_entity_to_dto(alternative)

	def create_alternative(self, alternative: AlternativeDTO, player_id: UUID) -> AlternativeDTO:
		if not alternative.question_id:
			raise TriviaException(TriviaErrorMessages.QUESTION_ID_MISSING)
		question = self.alternative_repository.get_question_by_id(alternative.question_id, player_id)
		if not question:
			raise TriviaException(TriviaErrorMessages.QUESTION_NOT_FOUND)
		if question.package.author_id != player_id:
			raise TriviaException(TriviaErrorMessages.UNAUTHORIZED_ALTERNATIVE_UPDATE)

		alternative_entity = self._from_dto_to_entity(alternative)
		alternative_entity = self.alternative_repository.create_alternative(alternative_entity)

		if not alternative_entity.id:
			raise TriviaException(TriviaErrorMessages.ALTERNATIVE_CREATION_FAILED)

		return self._from_entity_to_dto(alternative_entity)

	def update_alternative(
		self,
		alternative_id: int,
		alternative: AlternativeDTO,
		player_id: UUID,
	) -> AlternativeDTO:
		existing_alternative = self.alternative_repository.get_alternative_by_id(alternative_id, player_id)

		if not existing_alternative:
			raise TriviaException(TriviaErrorMessages.ALTERNATIVE_NOT_FOUND)

		if existing_alternative.question.package.author_id != player_id:
			raise TriviaException(TriviaErrorMessages.UNAUTHORIZED_ALTERNATIVE_UPDATE)

		alternative_data = alternative.model_dump(exclude_unset=True)
		for key, value in alternative_data.items():
			setattr(existing_alternative, key, value)

		updated_alternative = self.alternative_repository.update_alternative(existing_alternative)

		if not updated_alternative:
			raise TriviaException(TriviaErrorMessages.ALTERNATIVE_UPDATE_FAILED)

		return self._from_entity_to_dto(updated_alternative)

	def delete_alternative(self, alternative_id: int, player_id: UUID) -> None:
		existing_alternative = self.alternative_repository.get_alternative_by_id(alternative_id, player_id)

		if not existing_alternative:
			raise TriviaException(TriviaErrorMessages.ALTERNATIVE_NOT_FOUND)

		if existing_alternative.question.package.author_id != player_id:
			raise TriviaException(TriviaErrorMessages.UNAUTHORIZED_ALTERNATIVE_UPDATE)

		self.alternative_repository.delete_alternative(existing_alternative)

	@staticmethod
	def _from_entity_to_dto(alternative: Alternative) -> AlternativeDTO:
		return AlternativeDTO(
			id=alternative.id,
			question_id=alternative.question_id,
			text=alternative.text,
			is_correct=alternative.is_correct,
		)

	@staticmethod
	def _from_dto_to_entity(alternative_dto: AlternativeDTO) -> Alternative:
		return Alternative(
			question_id=alternative_dto.question_id,
			text=alternative_dto.text,
			is_correct=alternative_dto.is_correct,
		)
