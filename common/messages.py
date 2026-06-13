import json
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any, ClassVar, Dict, Type

MESSAGES = {}

def message(tag):
    def wrap(clazz):
        print(clazz)
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

# Goes from server -> client
@message("game_ready")
@dataclass
class GameReady:
    pass

@message("player_move")
@dataclass
class PlayerMove:
    player_id: int
    dy: float

@message("ball_move")
@dataclass
class BallMove:
    player_id: int
    dy: float

Message = Join | Move | GameReady | PlayerMove | BallMove

def encode(msg: Message): 
    return json.dumps({"type": msg.type, **asdict(msg)})

def decode(raw):
    data = json.loads(raw)
    clazz = MESSAGES[data.pop("type")]
    return clazz(**data)
    
