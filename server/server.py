import asyncio
from dataclasses import asdict
import json
import websockets
import time

from common.Enums import ClientMessageType, OpponentMove

PLAYER_PADDLE_SPEED = 50
BALL_SPEED = 75

"""
Player data structure: {'id': int, 'y': int}
Ball data structure: {'x': int, 'y': int }
"""


players = set()


async def handle_client(websocket: websockets.ServerConnection):
    global players

    if len(players) == 2:
        return

    player_id = 1 if len(players) == 0 else 2

    players.add(websocket)

    # Main game loop
    try:
        async for message in websocket:
            print("Received client message: " + json.dumps(json.loads(message)))
            if len(players) == 2:
                data = json.loads(message)
                opp: websockets.ServerConnection = next(p for p in players if p != websocket)
                if data["type"] == ClientMessageType.PLAYER_MOVE:
                    # Send opponent this players position
                    print("Received client message: " + json.dumps(data))
                    outgoing_message = OpponentMove(y_position=data["y_position"])
                    await opp.send(json.dumps(asdict(outgoing_message)))
            elif len(players) == 1:
                # TODO Waiting for players
                pass
    finally:
        players.remove(websocket)



async def start_game():
    players = {}

async def main():
    async with websockets.serve(handle_client, "localhost", 32231):
        print("Server started")
        await asyncio.Future() # runs server

asyncio.run(main())