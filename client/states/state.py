from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from client.game import Game

class State:
    def __init__(self, game: Game):
        self.game = game

    def handle_event(self, event):
        pass

    def handle_message(self, message):
        pass

    def update(self, dt):
        pass

    def draw(self, screen):
        pass
