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
    dx: float
    dy: float

# Goes from server -> client
@message("game_ready")
@dataclass
class GameReady:
    pass

Message = Join | Move | GameReady

def encode(msg: Message): 
    return json.dumps({"type": msg.type, **asdict(msg)})

def decode(raw):
    data = json.loads(raw)
    clazz = MESSAGES[data.pop("type")]
    return clazz(**data)
    
