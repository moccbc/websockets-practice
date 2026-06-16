import pygame
from client.states.state import State

class WaitingState(State):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont(None, 48)
        self.text_surface = self.font.render("Waiting for another player", True, (255, 255, 255))

    def draw(self, screen):
        screen.fill((20, 20, 40))
        text_rect = self.text_surface.get_rect(center=screen.get_rect().center)
        screen.blit(self.text_surface, text_rect)
