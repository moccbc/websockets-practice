import pygame

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
