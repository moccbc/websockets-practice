import asyncio
from websockets.sync.client import connect

import pygame
from states.state import State
from ui.button import Button

class MenuState(State):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont(None, 48)
        self.startButton = Button((150, 120, 120, 50), "Start", self.connect_to_server)

    def handle_event(self, event):
        self.startButton.handle_event(event)

    def draw(self, screen):
        screen.fill((20, 20, 40))
        self.startButton.draw(screen, self.font)

    def connect_to_server(self):
        self.game.connection = connect("ws://localhost:32231")
        self.game.connection.send('{"type": "playerMove", "y_position": 50, "farts":"100"}')
