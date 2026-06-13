from client.game import Game
from client.states.menustate import MenuState

game = Game()
game.change_state(MenuState(game))
game.run()
