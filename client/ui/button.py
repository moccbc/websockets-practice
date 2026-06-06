import pygame 

class Button:
    def __init__(self, rect, text, callback):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()

    def draw(self, screen, font):
        hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        color = (100, 100, 250) if hovered else (70, 70, 200)
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        label = font.render(self.text, True, (255, 255, 255))
        screen.blit(label, label.get_rect(center=self.rect.center))
