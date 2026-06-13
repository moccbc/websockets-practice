import asyncio
from websockets.sync.client import connect

import pygame
from client.states.state import State
from client.ui.button import Button
from common import messages
from common.messages import Join


class MenuState(State):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont(None, 48)
        self.startButton = Button((150, 120, 120, 50), "Start", self.connect_to_server)
        self.testButton = Button((150, 200, 120, 50), "Test Controls", self.test_controls)
        self.error_message = ""

    def handle_event(self, event):
        self.startButton.handle_event(event)
        self.testButton.handle_event(event)

    def draw(self, screen):
        screen.fill((20, 20, 40))
        self.startButton.draw(screen, self.font)
        self.testButton.draw(screen, self.font)
        # Connection status
        status = "Connected" if self.game.is_connected else "Not connected"
        status_label = self.font.render(status, True, (200, 200, 200))
        screen.blit(status_label, (20, 20))

        if self.error_message:
            err = pygame.font.SysFont(None, 28).render(self.error_message, True, (250, 120, 120))
            screen.blit(err, (20, 60))

    def connect_to_server(self):
        try:
            self.game.connection = connect("ws://localhost:32231")
            self.game.is_connected = True
            # send Join to the server
            self.game.connection.send(messages.encode(Join()))
            # start the background receiver thread on the Game
            try:
                self.game.start_network_receiver()
            except Exception:
                pass
            self.error_message = ""
            # move into PlayState immediately so the player is placed on the field
            from client.states.playstate import PlayState
            self.game.change_state(PlayState(self.game))
        except Exception as exc:
            # show a friendly message on screen
            self.error_message = f"Connect failed: {exc}"

    def test_controls(self):
        # Launch PlayState locally without connecting to server to test controls
        from client.states.playstate import PlayState

        # Ensure we're in local-test mode
        self.game.is_connected = False
        self.game.local_test = True
        self.game.change_state(PlayState(self.game))
