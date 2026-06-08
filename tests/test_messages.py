import json
import unittest

from common.messages import (
    MessageParseError,
    OpponentMove,
    PlayerMove,
    deserialize_message,
    serialize_message,
)


class TestMessageSerialization(unittest.TestCase):
    def test_player_move_serializes_to_json(self):
        message = PlayerMove(y_position=42)
        payload = serialize_message(message)

        data = json.loads(payload)
        self.assertEqual(data["type"], "playerMove")
        self.assertEqual(data["y_position"], 42)

    def test_opponent_move_serializes_to_json(self):
        message = OpponentMove(y_position=17)
        payload = serialize_message(message)

        data = json.loads(payload)
        self.assertEqual(data["type"], "opponentMove")
        self.assertEqual(data["y_position"], 17)

    def test_deserialize_player_move_returns_player_move(self):
        payload = json.dumps({"type": "playerMove", "y_position": 99})
        message = deserialize_message(payload)

        self.assertIsInstance(message, PlayerMove)
        self.assertEqual(message.y_position, 99)

    def test_deserialize_opponent_move_returns_opponent_move(self):
        payload = json.dumps({"type": "opponentMove", "y_position": 7})
        message = deserialize_message(payload)

        self.assertIsInstance(message, OpponentMove)
        self.assertEqual(message.y_position, 7)

    def test_deserialize_unknown_type_raises(self):
        payload = json.dumps({"type": "unknownType", "y_position": 5})
        with self.assertRaises(MessageParseError):
            deserialize_message(payload)

    def test_deserialize_malformed_json_raises(self):
        with self.assertRaises(MessageParseError):
            deserialize_message("{not valid json}")

    def test_deserialize_missing_field_raises(self):
        payload = json.dumps({"type": "playerMove"})
        with self.assertRaises(MessageParseError):
            deserialize_message(payload)


if __name__ == "__main__":
    unittest.main()
