import httpx

from app.application.dtos.room import RoomResponseDTO


class RoomClient:

    def __init__(
        self,
        base_url: str,
    ):
        self.base_url = base_url

    async def get_room(
        self,
        room_code: str,
    ) -> RoomResponseDTO:

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/{room_code}"
            )

            response.raise_for_status()

        return RoomResponseDTO(
            **response.json()
        )