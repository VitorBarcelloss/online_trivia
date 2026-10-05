import httpx


class GameClient:

    def __init__(
        self,
        base_url: str,
    ):
        self.base_url = base_url

    async def start_game(
        self,
        room_code: str,
        player_id: str,
    ) -> str:

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/start",
                params={
                    "room_code": room_code,
                    "player_id": player_id,
                },
            )

            response.raise_for_status()

            data = response.json()

        return str(data["id"])