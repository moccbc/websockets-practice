from game import Game
from states.menustate import MenuState

game = Game()
game.change_state(MenuState(game))
game.run()
