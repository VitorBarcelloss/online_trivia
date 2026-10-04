from abc import ABC, abstractmethod

from app.domain.entities.game import Game


class GameRepository(ABC):

    @abstractmethod
    async def save(self, game: Game) -> Game:
        pass

    @abstractmethod
    async def get(self, game_id: str) -> Game | None:
        pass

    @abstractmethod
    async def get_by_room_id(self, room_id: str) -> Game | None:
        pass

    @abstractmethod
    async def update(self, game: Game) -> bool:
        pass

    @abstractmethod
    async def delete(self, game_id: str) -> bool:
        pass