import asyncio
import time
import websockets

from common import messages
from common.messages import Move, Join, GameReady, JoinResponse, PaddlePosition, BallPosition

PLAYER_PADDLE_SPEED = 0.5
BALL_SPEED = 75

"""
Player data structure: {ws: websocket, 'id': int, 'y': int}
Ball data structure: {'x': int, 'y': int }
"""

# TODO: Should this be a @dataclass?
class Player:
    def __init__(self, ws, id, x, y):
        self.ws = ws
        self.id = id
        self.x = x
        self.y = y
        
players: dict[int, Player] = {}

async def game_loop():
    while True:
        for player_id, player in players.items():
            for player_id2, player2 in players.items():
                paddle_position_message = messages.encode(
                        PaddlePosition(player_id, player.x, player.y))
                await player2.ws.send(paddle_position_message)

                ball_position_message = messages.encode(
                        BallPosition(player_id, player.x, player.y))
                await player2.ws.send(ball_position_message)

        # This is needed so that the game_loop and the async for loop in handle_client can share
        # the resources so that handle_client can actually send and receive stuff to and from 
        # the client
        await asyncio.sleep(1/30)

async def handle_client(websocket: websockets.ServerConnection):
    global players

    player_id = len(players)
    players[player_id] = Player(websocket, player_id, 500, 500)

    # Main game loop
    try:
        # this line is equivalent to while True: message = await websocket.recv()
        async for raw_message in websocket:
            message = messages.decode(raw_message)
            print(f"Received client message: {message}")

            match message:
                case Join():
                    await websocket.send(messages.encode(JoinResponse(player_id)))

                    if len(players) == 2:
                        for player in players.items():
                            ready_message = messages.encode(GameReady())
                            await player.ws.send(ready_message)
                            asyncio.create_task(game_loop())

                case Move(player_id, dy):
                    players[player_id].y += dy * PLAYER_PADDLE_SPEED

    finally:
        players.pop(player_id)


async def start_game():
    players = {}

async def main():
    async with websockets.serve(handle_client, "localhost", 32231):
        print("Server started")
        await asyncio.Future() # runs server

asyncio.run(main())
