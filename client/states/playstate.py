import pygame
import queue
from client.ui.button import Button
from common import messages
from common.messages import Move, PaddlePosition
from common.messages import GameReady
from client.states.state import State

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PADDLE_WIDTH = 10
PADDLE_HEIGHT = 100
PADDLE_SPEED = 300
BALL_RADIUS = 8

class PlayState(State):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont(None, 36)
        self.large_font = pygame.font.SysFont(None, 48)
        self.local_up = False
        self.local_down = False
        self.paddle_x = 30
        self.remote_paddle_x = SCREEN_WIDTH - 30 - PADDLE_WIDTH
        self.paddle_y = (SCREEN_HEIGHT - PADDLE_HEIGHT) / 2
        self.remote_paddle_y = (SCREEN_HEIGHT - PADDLE_HEIGHT) / 2
        self.ball_x = SCREEN_WIDTH / 2
        self.ball_y = SCREEN_HEIGHT / 2
        self.score_left = 0
        self.score_right = 0
        self.player_id = self.game.player_id
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

    def on_message(self, message):
        match message:
            case GameReady():
                self.ready = True
            case PaddlePosition():
                self.paddle_y = message.y
                self.paddle_x = message.x
                pass
            case Exception():
                from client.states.menustate import MenuState

                self.game.change_state(MenuState(self.game))
                return


    def update(self, dt):
        # Handle messages sent to server for this tick
        
        #if self.game.connection is None:
        #    return
        
        if self.local_down or self.local_up:
            direction = self.local_up - self.local_down
            #message = messages.encode(Move(self.player_id, direction))
            self.game.network_client.send(Move(self.player_id, direction))

    def draw(self, screen):
        screen.fill((20, 20, 40))
        self.draw_center_line(screen)
        pygame.draw.rect(screen, (255, 255, 255), (self.paddle_x, self.paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT))
        pygame.draw.rect(screen, (255, 255, 255), (self.remote_paddle_x, self.remote_paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT))
        pygame.draw.circle(screen, (255, 255, 255), (int(self.ball_x), int(self.ball_y)), BALL_RADIUS)
        self.draw_scores(screen)
        self.draw_status(screen)
        # draw back button
        self.backButton.draw(screen, self.font)
        if not self.ready:
            # show waiting overlay while still rendering the local paddle
            label = self.large_font.render("Waiting for opponent...", True, (220, 220, 220))
            rect = label.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
            screen.blit(label, rect)

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
            if self.game.is_connected and self.game.connection is not None:
                self.game.close_connection()
        except Exception:
            pass
        # clear local_test flag
        self.game.local_test = False
        # go back to menu
        from client.states.menustate import MenuState

        self.game.change_state(MenuState(self.game))
