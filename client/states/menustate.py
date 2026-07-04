import asyncio
from websockets.sync.client import connect

import pygame
from client.states.state import State
from client.states.playstate import PlayState
from client.states.waitingstate import WaitingState
from client.ui.button import Button
from common import messages
from common.messages import Join, JoinResponse

class MenuState(State):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont(None, 48)
        self.startButton = Button((150, 120, 120, 50), "Start", self.connect_to_server)
        self.testButton = Button((150, 200, 120, 50), "Test Controls", self.test_controls)
        self.error_message = ""

    def handle_message(self, msg):
        match msg:
            case JoinResponse(player_id):
                self.game.player_id = player_id
                self.game.change_state(WaitingState(self.game))

    def handle_event(self, event):
        self.startButton.handle_event(event)
        self.testButton.handle_event(event)

    def draw(self, screen):
        screen.fill((20, 20, 40))
        self.startButton.draw(screen, self.font)
        self.testButton.draw(screen, self.font)

        if self.error_message:
            err = pygame.font.SysFont(None, 28).render(self.error_message, True, (250, 120, 120))
            screen.blit(err, (20, 60))

    def connect_to_server(self):
        try:
            self.game.network_client.start_network_receiver()
            # send Join to the server
            self.game.network_client.send(Join())
        except Exception as exc:
            # show a friendly message on screen
            self.error_message = f"Connect failed: {exc}"

    def test_controls(self):

        # Ensure we're in local-test mode
        self.game.is_connected = False
        self.game.local_test = True
        self.game.change_state(PlayState(self.game))
