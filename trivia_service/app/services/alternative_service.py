from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.dtos.alternative import AlternativeCreateDTO, AlternativeResponseDTO, AlternativeUpdateDTO
from app.core.exceptions import TriviaErrorMessages, TriviaException
from app.models.alternative import Alternative


class AlternativeService:
	def __init__(self, alternative_repository):
		self.alternative_repository = alternative_repository

	def get_alternatives(
		self,
		question_id: int,
		player_id: UUID | None = None,
	) -> list[AlternativeResponseDTO]:
		alternatives = self.alternative_repository.get_alternatives(question_id, player_id)
		return [self._from_entity_to_dto(alternative) for alternative in alternatives]

	def get_alternative(
		self,
		alternative_id: int,
		player_id: UUID | None = None,
	) -> AlternativeResponseDTO:
		alternative = self.alternative_repository.get_alternative_by_id(alternative_id, player_id)

		if not alternative:
			raise TriviaException(TriviaErrorMessages.ALTERNATIVE_NOT_FOUND)

		return self._from_entity_to_dto(alternative)

	def create_alternative(self, alternative: AlternativeCreateDTO, player_id: UUID) -> AlternativeResponseDTO:
		text = alternative.text.strip()
		if not text:
			raise TriviaException(TriviaErrorMessages.INVALID_REQUEST)
		question = self.alternative_repository.get_question_by_id(alternative.question_id, player_id)
		if not question:
			raise TriviaException(TriviaErrorMessages.QUESTION_NOT_FOUND)
		if question.package.author_id != player_id:
			raise TriviaException(TriviaErrorMessages.UNAUTHORIZED_ALTERNATIVE_UPDATE)

		duplicate = self.alternative_repository.get_duplicate(alternative.question_id, text)
		if duplicate:
			if duplicate.is_correct == alternative.is_correct:
				return self._from_entity_to_dto(duplicate)
			raise TriviaException(TriviaErrorMessages.DUPLICATE_RESOURCE_CONFLICT)

		alternative_entity = self._from_dto_to_entity(alternative)
		alternative_entity.text = text
		try:
			alternative_entity = self.alternative_repository.create_alternative(alternative_entity)
			self.alternative_repository.session.commit()
		except IntegrityError:
			self.alternative_repository.session.rollback()
			duplicate = self.alternative_repository.get_duplicate(alternative.question_id, text)
			if duplicate and duplicate.is_correct == alternative.is_correct:
				return self._from_entity_to_dto(duplicate)
			if duplicate:
				raise TriviaException(TriviaErrorMessages.DUPLICATE_RESOURCE_CONFLICT)
			raise

		return self._from_entity_to_dto(alternative_entity)

	def update_alternative(
		self,
		alternative_id: int,
		alternative: AlternativeUpdateDTO,
		player_id: UUID,
	) -> AlternativeResponseDTO:
		existing_alternative = self.alternative_repository.get_alternative_by_id(alternative_id, player_id)

		if not existing_alternative:
			raise TriviaException(TriviaErrorMessages.ALTERNATIVE_NOT_FOUND)

		if existing_alternative.question.package.author_id != player_id:
			raise TriviaException(TriviaErrorMessages.UNAUTHORIZED_ALTERNATIVE_UPDATE)

		alternative_data = alternative.model_dump(exclude_unset=True)
  
		if "text" in alternative_data:
			alternative_data["text"] = alternative_data["text"].strip()

		if any(getattr(existing_alternative, key) == value for key, value in alternative_data.items()):
			return self._from_entity_to_dto(existing_alternative)

		if "text" in alternative_data:
			duplicate = self.alternative_repository.get_duplicate(
				existing_alternative.question_id,
				alternative_data["text"],
			)
   
			if duplicate and duplicate.id != existing_alternative.id:
				raise TriviaException(TriviaErrorMessages.DUPLICATE_RESOURCE_CONFLICT)

		for key, value in alternative_data.items():
			setattr(existing_alternative, key, value)

		try:
			updated_alternative = self.alternative_repository.update_alternative(existing_alternative)
			self.alternative_repository.session.commit()
		except IntegrityError as exc:
			self.alternative_repository.session.rollback()
			raise TriviaException(TriviaErrorMessages.DUPLICATE_RESOURCE_CONFLICT) from exc

		if not updated_alternative:
			raise TriviaException(TriviaErrorMessages.ALTERNATIVE_UPDATE_FAILED)

		return self._from_entity_to_dto(updated_alternative)


	def delete_alternative(self, alternative_id: int, player_id: UUID) -> None:
		existing_alternative = self.alternative_repository.get_alternative_by_id(alternative_id, player_id)

		if not existing_alternative:
			return

		if existing_alternative.question.package.author_id != player_id:
			raise TriviaException(TriviaErrorMessages.UNAUTHORIZED_ALTERNATIVE_UPDATE)

		self.alternative_repository.delete_alternative(existing_alternative)
		self.alternative_repository.session.commit()

	@staticmethod
	def _from_entity_to_dto(alternative: Alternative) -> AlternativeResponseDTO:
		return AlternativeResponseDTO(
			id=alternative.id,
			question_id=alternative.question_id,
			text=alternative.text,
			is_correct=alternative.is_correct,
		)

	@staticmethod
	def _from_dto_to_entity(alternative_dto: AlternativeCreateDTO) -> Alternative:
		return Alternative(
			question_id=alternative_dto.question_id,
			text=alternative_dto.text,
			is_correct=alternative_dto.is_correct,
		)
