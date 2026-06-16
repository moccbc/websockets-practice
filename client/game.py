import threading
import queue
import pygame
from client.states.state import State
from common import messages
from client.networkclient import NetworkClient

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pong")
        self.screen = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = None
        self.network_client = NetworkClient("ws://localhost:32231")
        self.player_id = 1
        self.local_test = False

    def change_state(self, state: State):
        self.state = state

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0

            for msg in self.network_client.poll():
                self.state.on_message(msg)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if self.state is not None:
                    self.state.handle_event(event) # Handles inputs

            if self.state is not None:
                self.state.update(dt) # Handles internal data changes
                self.state.draw(self.screen) # Render based on internal data
            
            pygame.display.flip()

        pygame.quit()
