import pygame
import queue
from client.ui.button import Button
from common import messages
from common.messages import Move, ScoreUpdate, BallObject, PaddleObject
from common.messages import GameReady
from client.states.state import State

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PADDLE_WIDTH = 10
PADDLE_HEIGHT = 100
PADDLE_SPEED = 300
BALL_RADIUS = 8

# TODO: Move this to the UI directory
class PaddleUI():
    def __init__(self, x=100, y=100, height=100, width=100):
        self.x = x
        self.y = y
        self.width = width 
        self.height = height

    def update(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), (self.x, self.y, self.width, self.height))

# TODO: Move this to the UI directory
class BallUI():
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius

    def update(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), self.radius)

class PlayState(State):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont(None, 36)
        self.large_font = pygame.font.SysFont(None, 48)
        self.local_up = False
        self.local_down = False

        self.player_id = self.game.player_id

        self.player_paddle = PaddleUI()
        self.opponent_paddle = PaddleUI()
        self.ball = BallUI(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, BALL_RADIUS)

        self.score_left = 0
        self.score_right = 0
        # whether the match is ready (both players connected)
        self.ready = bool(getattr(self.game, 'local_test', False))
        # back/disconnect button
        self.backButton = Button((SCREEN_WIDTH - 170, 20, 150, 40), "Back to Menu", self.disconnect)

    def handle_event(self, event):
        # pass events to UI buttons
        self.backButton.handle_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                self.local_up = True
            elif event.key == pygame.K_s:
                self.local_down = True
            elif event.key == pygame.K_UP:
                self.local_up = True
            elif event.key == pygame.K_DOWN:
                self.local_down = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                self.local_up = False
            elif event.key == pygame.K_s:
                self.local_down = False
            elif event.key == pygame.K_UP:
                self.local_up = False
            elif event.key == pygame.K_DOWN:
                self.local_down = False

    def handle_message(self, message):
        match message:
            case GameReady():
                self.ready = True

            case PaddleObject(player_id, x, y, width, height):
                if player_id == self.player_id:
                    self.player_paddle.update(x, y, width, height)
                else:
                    self.opponent_paddle.update(x, y, width, height)

            case BallObject(x, y, radius):
                self.ball.update(x, y, radius)

            case ScoreUpdate(score_left, score_right):
                self.score_left = score_left
                self.score_right = score_right

            case Exception():
                from client.states.menustate import MenuState

                self.game.change_state(MenuState(self.game))
                return

    def update(self, dt):
        # Handle messages sent to server for this tick
        
        if self.local_down or self.local_up:
            direction = self.local_down - self.local_up
            self.game.network_client.send(Move(self.player_id, direction))

    def draw(self, screen):
        screen.fill((20, 20, 40))
        self.draw_center_line(screen)

        self.player_paddle.draw(screen)
        self.opponent_paddle.draw(screen)
        self.ball.draw(screen)

        self.draw_scores(screen)
        self.draw_status(screen)

        # draw back button
        self.backButton.draw(screen, self.font)

    def draw_center_line(self, screen):
        for y in range(0, SCREEN_HEIGHT, 30):
            pygame.draw.rect(screen, (100, 100, 100), (SCREEN_WIDTH / 2 - 2, y, 4, 20))

    def draw_scores(self, screen):
        left_score = self.font.render(str(self.score_left), True, (255, 255, 255))
        right_score = self.font.render(str(self.score_right), True, (255, 255, 255))
        screen.blit(left_score, (SCREEN_WIDTH / 2 - 80, 20))
        screen.blit(right_score, (SCREEN_WIDTH / 2 + 60, 20))

    def draw_status(self, screen):
        lines = []
        lines.append("Local paddle controls: W/S or Up/Down")
        if getattr(self.game, 'local_test', False):
            lines.append("Mode: Local test (no server)")
        #else:
        #    lines.append("Mode: Online" if self.game.is_connected else "Mode: Offline")
        # show player id if available
        pid = getattr(self.game, 'player_id', None)
        if pid is not None:
            lines.append(f"Player ID: {pid}")

        for i, text in enumerate(lines):
            label = self.font.render(text, True, (200, 200, 200))
            screen.blit(label, (20, SCREEN_HEIGHT - 40 - (len(lines)-1-i)*22))

    def disconnect(self):
        # invoked by Back button: close network and return to menu
        try:
            if self.game.network_client._thread:
                self.game.network_client.stop_network_receiver()
        except Exception:
            pass
        # clear local_test flag
        self.game.local_test = False
        # go back to menu
        from client.states.menustate import MenuState

        self.game.change_state(MenuState(self.game))
