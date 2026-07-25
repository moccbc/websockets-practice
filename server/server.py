import asyncio
import random
import time
import websockets

from common import messages
from common.messages import Move, Join, GameReady, JoinResponse, ScoreUpdate, BallObject, PaddleObject

PLAYER_PADDLE_SPEED = 2
BALL_SPEED = 75
GAME_SPEED = 1/30
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

PADDLE_WIDTH = 10
PADDLE_HEIGHT = 100

PLAYER_ONE_PADDLE_INIT_X = 25
PLAYER_ONE_PADDLE_INIT_Y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
PLAYER_TWO_PADDLE_INIT_X = SCREEN_WIDTH - PLAYER_ONE_PADDLE_INIT_X - PADDLE_WIDTH
PLAYER_TWO_PADDLE_INIT_Y = PLAYER_ONE_PADDLE_INIT_Y 

BALL_RADIUS = 8

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

def reset_ball():
    ball_x = SCREEN_WIDTH / 2
    ball_y = SCREEN_HEIGHT / 2

    while True:
        dx = random.uniform(-1, 1)
        dy = random.uniform(-1, 1)
        magnitude = (dx * dx + dy * dy) ** 0.5
        if magnitude > 0:
            return ball_x, ball_y, (dx / magnitude, dy / magnitude)

def check_collision_with_paddle(ball_x, ball_y, player):
    # Check collision with Player1 (left) paddle
    if player.id == 0 and (ball_x - BALL_RADIUS <= player.x + PADDLE_WIDTH) and \
        (player.y <= ball_y <= player.y + PADDLE_HEIGHT):
        return True 

    # Check collision with Player2 (right) paddle
    if player.id == 1 and (ball_x + BALL_RADIUS >= player.x) and \
        (player.y <= ball_y <= player.y + PADDLE_HEIGHT):
        return True

    return False 

def advance_ball(ball_x, ball_y, ball_direction, score_left, score_right, player):
    ball_x += ball_direction[0] * BALL_SPEED * GAME_SPEED
    ball_y += ball_direction[1] * BALL_SPEED * GAME_SPEED

    # Checking if it collided with a player's paddle
    if check_collision_with_paddle(ball_x, ball_y, player):
        ball_direction = (-ball_direction[0], ball_direction[1])
        return ball_x, ball_y, ball_direction, score_left, score_right

    # When the ball is out of bounds (OOB) of the top of the screen
    if ball_y - BALL_RADIUS <= 0:
        ball_y = BALL_RADIUS
        ball_direction = (ball_direction[0], -ball_direction[1])
    # When the ball is OOB of the bottom of the screen
    elif ball_y + BALL_RADIUS >= SCREEN_HEIGHT:
        ball_y = SCREEN_HEIGHT - BALL_RADIUS
        ball_direction = (ball_direction[0], -ball_direction[1])

    # When the ball is OOB of the left of the screen
    if ball_x - BALL_RADIUS <= 0:
        score_right += 1
        return (*reset_ball(), score_left, score_right)
    # When the ball is OOB of the right of the screen
    elif ball_x + BALL_RADIUS >= SCREEN_WIDTH:
        score_left += 1
        return (*reset_ball(), score_left, score_right)

    return ball_x, ball_y, ball_direction, score_left, score_right


async def game_loop():
    ball_x, ball_y, ball_direction = reset_ball()
    score_left = 0
    score_right = 0

    while True:
        for player_id, player in players.items():
            ball_x, ball_y, ball_direction, score_left, score_right = advance_ball(
                ball_x,
                ball_y,
                ball_direction,
                score_left,
                score_right,
                player
            )

            # First, update score if applicable
            score_message = messages.encode(ScoreUpdate(score_left, score_right))
            await player.ws.send(score_message)

            await player.ws.send(messages.encode(
                BallObject(ball_x, ball_y, BALL_RADIUS)))

            for player_id2, player2 in players.items():
                await player2.ws.send(messages.encode(
                    PaddleObject(player_id, player.x, player.y, PADDLE_WIDTH, PADDLE_HEIGHT)))

        # This is needed so that the game_loop and the async for loop in handle_client can share
        # the resources so that handle_client can actually send and receive stuff to and from 
        # the client
        await asyncio.sleep(GAME_SPEED)

async def handle_client(websocket: websockets.ServerConnection):
    global players

    player_id = len(players)
    init_x, init_y = (PLAYER_ONE_PADDLE_INIT_X, PLAYER_ONE_PADDLE_INIT_Y) if player_id == 0 else \
                     (PLAYER_TWO_PADDLE_INIT_X, PLAYER_TWO_PADDLE_INIT_Y)
    players[player_id] = Player(websocket, player_id, init_x, init_y)

    # Main game loop
    try:
        # this line is equivalent to "while True: message = await websocket.recv()"
        async for raw_message in websocket:
            message = messages.decode(raw_message)

            match message:
                case Join():
                    await websocket.send(messages.encode(JoinResponse(player_id)))

                    if len(players) == 2:
                        print(players)
                        for player_id, player in players.items():
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
