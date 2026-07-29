import pygame

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

