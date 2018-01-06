from menus import PagedMenu
from menus import PagedOption
from filters.players import PlayerIter
from commands.say import SayCommand
from commands.client import ClientCommand
from players.entity import Player

from goldmod.goldfunctions import pickle


def gold_player_menu_build(menu, index):
	for player in PlayerIter('all'):
		gold = pickle.keyGetValue(player.steamid,'gold')
		option = PagedOption('%s - Gold: %s' % (player.name,gold), player)
		menu.append(option)
		
def gold_player_menu_select(menu, index, choice):
	return

@SayCommand('showplayergold')
@ClientCommand('showplayergold')
def player_gold(command, index, team=None):
	gold_player_menu = PagedMenu(title='Player Gold Menu', build_callback=gold_player_menu_build, select_callback=gold_player_menu_select)
	gold_player_menu.send(index)