import unittest

from server import server


class ServerScoringTests(unittest.TestCase):
    def test_left_edge_scoring_increments_right_score(self):
        ball_x, ball_y, ball_direction, score_left, score_right = server.advance_ball(
            4,
            300,
            (-1, 0.2),
            0,
            0,
        )

        self.assertEqual(score_left, 0)
        self.assertEqual(score_right, 1)
        self.assertEqual(ball_x, server.SCREEN_WIDTH / 2)
        self.assertEqual(ball_y, server.SCREEN_HEIGHT / 2)

    def test_right_edge_scoring_increments_left_score(self):
        ball_x, ball_y, ball_direction, score_left, score_right = server.advance_ball(
            server.SCREEN_WIDTH - 4,
            300,
            (1, 0.2),
            0,
            0,
        )

        self.assertEqual(score_left, 1)
        self.assertEqual(score_right, 0)
        self.assertEqual(ball_x, server.SCREEN_WIDTH / 2)
        self.assertEqual(ball_y, server.SCREEN_HEIGHT / 2)


if __name__ == "__main__":
    unittest.main()
