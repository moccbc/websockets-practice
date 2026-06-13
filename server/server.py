import asyncio
import time
import websockets

from common import messages
from common.messages import Move, Join, GameReady

PLAYER_PADDLE_SPEED = 50
BALL_SPEED = 75

"""
Player data structure: {ws: websocket, 'id': int, 'y': int}
Ball data structure: {'x': int, 'y': int }
"""

players = set() #[] -> index by player Id?

async def handle_client(websocket: websockets.ServerConnection):
    global players

    # Main game loop
    try:
        # this line is equivalent to while True: message = await websocket.recv()
        async for raw_message in websocket:
            message = messages.decode(raw_message)
            print(f"Received client message: {message}")

            match message:
                case Join():
                    player_id = 1 if len(players) == 0 else 2
                    players.add(websocket)

                    if len(players) == 2:
                        opp: websockets.ServerConnection = next(p for p in players if p != websocket)
                        outgoing_message = messages.encode(GameReady())
                        await opp.send(outgoing_message)
                    elif len(players) == 1:
                        # TODO Waiting for players
                        pass

                case Move(player_id, dx, dy):
                    pass
    finally:
        players.remove(websocket)



async def start_game():
    players = {}

async def main():
    async with websockets.serve(handle_client, "localhost", 32231):
        print("Server started")
        await asyncio.Future() # runs server


'''
1. client -> server: Sends message
2. server handles message: handle_client(client_ws)
3. handle_client runs to handle the message in client_ws
    - No loop that goes on here

1. client connects to server
2. server does "async with websockets.serve(handle_client, "localhost", 32231):"
    While(True):
        ws = queue.pop
        handle_client(ws)
3. server persists the connection
'''

asyncio.run(main())
