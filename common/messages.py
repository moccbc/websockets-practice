import json
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any, ClassVar, Dict, Type

class BaseMessage:
    pass

MESSAGES = {}

def message(tag):
    def wrap(clazz):
        clazz.type = tag
        MESSAGES[tag] = clazz
        return clazz
    return wrap

def encode(msg: BaseMessage): 
    return json.dumps({"type": msg.type, **asdict(msg)})

def decode(raw):
    data = json.loads(raw)
    clazz = MESSAGES[data.pop("type")]
    return clazz(**data)
    
# Goes from client -> server
@message("join")
@dataclass
class Join(BaseMessage):
    pass

@message("move")
@dataclass
class Move(BaseMessage):
    player_id: str
    dx: float
    dy: float

@message("GameReady")
@dataclass
class GameReady(BaseMessage):
    pass
