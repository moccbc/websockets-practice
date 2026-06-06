import pygame
from states.state import State

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pong")
        self.screen = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = None

    def change_state(self, state: State):
        self.state = state

    def run(self):
        while (self.running):
            # This is seconds since last frame
            dt = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.state.handle_event(event)

            self.state.update(dt)
            self.state.draw(self.screen)
            pygame.display.flip()

        pygame.quit()
