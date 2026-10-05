from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.room_connections: dict[str, dict[str, WebSocket]] = {}
        self.game_connections: dict[str, dict[str, WebSocket]] = {}
        self.room_games: dict[str, str] = {}

    async def connect(
        self,
        room_code: str,
        player_id: str,
        websocket: WebSocket,
    ) -> str | None:
        await websocket.accept()

        game_id = self.room_games.get(room_code)

        if game_id:
            self._add_game_connection(
                game_id=game_id,
                player_id=player_id,
                websocket=websocket,
            )
            return game_id

        if room_code not in self.room_connections:
            self.room_connections[room_code] = {}

        self.room_connections[room_code][player_id] = websocket

        return None

    def _add_game_connection(
        self,
        game_id: str,
        player_id: str,
        websocket: WebSocket,
    ) -> None:
        if game_id not in self.game_connections:
            self.game_connections[game_id] = {}

        self.game_connections[game_id][player_id] = websocket

    def bind_room_to_game(
        self,
        room_code: str,
        game_id: str,
    ) -> None:
        self.room_games[room_code] = game_id

        room_connections = self.room_connections.pop(
            room_code,
            {},
        )

        for player_id, websocket in room_connections.items():
            self._add_game_connection(
                game_id=game_id,
                player_id=player_id,
                websocket=websocket,
            )

    def get_game_id(
        self,
        room_code: str,
    ) -> str | None:
        return self.room_games.get(room_code)

    def disconnect(
        self,
        room_code: str,
        player_id: str,
    ) -> None:
        game_id = self.room_games.get(room_code)

        if game_id:
            self.disconnect_game_player(
                game_id=game_id,
                player_id=player_id,
            )
            return

        connections = self.room_connections.get(room_code)

        if not connections:
            return

        connections.pop(player_id, None)

        if not connections:
            self.room_connections.pop(room_code, None)

    async def send_to_player(
        self,
        game_id: str,
        player_id: str,
        message: dict,
    ) -> None:
        websocket = self.game_connections.get(
            game_id,
            {},
        ).get(player_id)

        if not websocket:
            return

        try:
            await websocket.send_json(message)

        except Exception:
            self.disconnect_game_player(
                game_id=game_id,
                player_id=player_id,
            )

    async def broadcast(
        self,
        game_id: str,
        message: dict,
    ) -> None:
        connections = self.game_connections.get(
            game_id,
            {},
        )

        disconnected_players = []

        for player_id, websocket in connections.items():
            try:
                await websocket.send_json(message)

            except Exception:
                disconnected_players.append(player_id)

        for player_id in disconnected_players:
            self.disconnect_game_player(
                game_id=game_id,
                player_id=player_id,
            )

    def disconnect_game_player(
        self,
        game_id: str,
        player_id: str,
    ) -> None:
        connections = self.game_connections.get(game_id)

        if not connections:
            return

        connections.pop(player_id, None)

        if not connections:
            self.game_connections.pop(game_id, None)

    def cleanup_game(
        self,
        room_code: str,
        game_id: str,
    ) -> None:
        self.room_games.pop(
            room_code,
            None,
        )

        self.game_connections.pop(
            game_id,
            None,
        )

        self.room_connections.pop(
            room_code,
            None,
        )
