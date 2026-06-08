import json
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any, ClassVar, Dict, Type

MessagePayload = Dict[str, Any]


class MessageParseError(ValueError):
    pass


class ClientMessageType(StrEnum):
    PLAYER_MOVE = "playerMove"


class ServerMessageType(StrEnum):
    OPPONENT_MOVE = "opponentMove"


@dataclass
class BaseMessage:
    type: str = field(init=False)
    TYPE: ClassVar[str]

    def __post_init__(self):
        self.type = self.TYPE

    def to_dict(self) -> MessagePayload:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: MessagePayload) -> "BaseMessage":
        if "type" not in data:
            raise MessageParseError("Message payload must include a type field")

        try:
            return cls(**{k: v for k, v in data.items() if k != "type"})
        except TypeError as exc:
            raise MessageParseError("Invalid or missing message fields") from exc


@dataclass
class PlayerMove(BaseMessage):
    TYPE: ClassVar[str] = ClientMessageType.PLAYER_MOVE
    y_position: int


@dataclass
class OpponentMove(BaseMessage):
    TYPE: ClassVar[str] = ServerMessageType.OPPONENT_MOVE
    y_position: int


_MESSAGE_CLASSES: Dict[str, Type[BaseMessage]] = {
    ClientMessageType.PLAYER_MOVE: PlayerMove,
    ServerMessageType.OPPONENT_MOVE: OpponentMove,
}


def serialize_message(message: BaseMessage) -> str:
    return message.to_json()


def deserialize_message(payload: str) -> BaseMessage:
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise MessageParseError("Malformed JSON payload") from exc

    if not isinstance(data, dict):
        raise MessageParseError("Message payload must be a JSON object")

    message_type = data.get("type")
    if message_type not in _MESSAGE_CLASSES:
        raise MessageParseError(f"Unknown message type: {message_type}")

    message_cls = _MESSAGE_CLASSES[message_type]
    return message_cls.from_dict(data)
