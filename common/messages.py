import json
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any, ClassVar, Dict, Type
from typing_extensions import deprecated

MESSAGES = {}

class MessageError(Exception):
    """Base class for message encode/decode failures."""
    pass

class EncodeError(MessageError):
    """Raised when a message fails to encode."""
    pass

class DecodeError(MessageError):
    """Raised when raw data fails to decode into a message."""
    pass

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

# Goes from server -> client
@message("join_response")
@dataclass
class JoinResponse:
    player_id: int

@message("game_ready")
@dataclass
class GameReady:
    pass

@message("paddle")
@dataclass(frozen=True)
class PaddleObject:
    player_id: int
    x: float
    y: float
    width: int 
    height: int 

@message("ball")
@dataclass(frozen=True)
class BallObject:
    x: float
    y: float
    radius: float

@message("score_update")
@dataclass(frozen=True)
class ScoreUpdate:
    score_left: int
    score_right: int

Message = Join | JoinResponse | Move | GameReady | ScoreUpdate | PaddleObject | BallObject

def encode(msg: Message):
    try:
        return json.dumps({"type": msg.type, **asdict(msg)})
    except (AttributeError, TypeError) as exc:
        raise EncodeError(f"Failed to encode {msg!r}") from exc

def decode(raw):
    try:
        data = json.loads(raw)
        clazz = MESSAGES[data.pop("type")]
        return clazz(**data)
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        raise DecodeError(f"Failed to decode {raw!r}") from exc
    
