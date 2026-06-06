from dataclasses import dataclass
from enum import StrEnum

class ClientMessageType(StrEnum):
    PLAYER_MOVE = "playerMove"

class ServerMessageType(StrEnum):
    OPPONENT_MOVE = "opponentMove"

@dataclass
class PlayerMove:
    y_position: int
    type: ClientMessageType = ClientMessageType.PLAYER_MOVE
    
@dataclass
class OpponentMove:
    y_position: int
    type: ServerMessageType = ServerMessageType.OPPONENT_MOVE