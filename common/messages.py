import json
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any, ClassVar, Dict, Type

MESSAGES = {}

def message(tag):
    def wrap(clazz):
        clazz.type = tag
        MESSAGES[tag] = clazz
        return clazz
    return wrap

# Goes from client -> server
@message("join")
@dataclass
class Join:
    pass

@message("move")
@dataclass
class Move:
    player_id: int
    y: int

@message("player_move")
@dataclass
class PlayerMove:
    player_id: int
    dy: float

# Goes from server -> client
@message("join_response")
@dataclass
class JoinResponse:
    player_id: int

@message("game_ready")
@dataclass
class GameReady:
    pass

@message("paddle_position")
@dataclass(frozen=True)
class PaddlePosition:
    player_id: int
    x: float
    y: float

@message("ball_position")
@dataclass(frozen=True)
class BallPosition:
    x: float
    y: float

Message = Join | JoinResponse | Move | GameReady | PlayerMove | PaddlePosition | BallPosition

def encode(msg: Message): 
    return json.dumps({"type": msg.type, **asdict(msg)})

def decode(raw):
    data = json.loads(raw)
    clazz = MESSAGES[data.pop("type")]
    return clazz(**data)
    
