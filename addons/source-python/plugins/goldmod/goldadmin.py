import os
from players.helpers import index_from_userid, userid_from_index
from configobj import ConfigObj
from commands.say import SayCommand
from commands.client import ClientCommand
from players.entity import Player
from menus import SimpleMenu
from menus import SimpleOption
from menus import Text
from filters.players import PlayerIter
from menus import PagedMenu
from menus import PagedOption
from messages import SayText2

import goldmod
from goldmod.goldfunctions import addGold,takeGold

value_1 = 'test1'
value_2 = 'test2'

def _gold_admin_menu_select(menu, index, choice):
	userid = userid_from_index(index)
	if choice.choice_index == 1:
		if has_flag(userid, 'goldadmin_givegold'):
			giveGolddoCommand(userid)
		else:
			SayText2('\x04[WCS] \x05You do not have  \x04access \x05this menu!').send(index)
			gold_admin_menu.send(index)
	if choice.choice_index == 2:
		if has_flag(userid, 'goldadmin_removegold'):
			takeGolddoCommand(userid)
		else:
			SayText2('\x04[WCS] \x05You do not have \x04access \x05this menu!').send(index)
			gold_admin_menu.send(index)

	if choice.choice_index == 9:
		menu.close(index)

gold_admin_menu = SimpleMenu(
    [
        Text('Gold Admin Menu'),
        Text('-------------------'),
        SimpleOption(1, 'Give Gold', value_1),
        SimpleOption(2, 'Remove Gold', value_2),
		Text('-------------------'),
        SimpleOption(9, 'Close', highlight=False),
    ],
    select_callback=_gold_admin_menu_select)
	
	
	

def get_addon_path():
    path = os.path.dirname(os.path.abspath(__file__))
    return path
	

@SayCommand('goldadmin')
@ClientCommand('goldadmin')
def _wcs_admin_command(command, index, team=None):
	userid = userid_from_index(index)
	if is_admin(userid):
		gold_admin_menu.send(index)
	
def is_admin(userid):
	admins = ini.getAdmins
	index = index_from_userid(userid)
	player = Player(index)
	if player.steamid in admins:
		return True
	else:
		return False
		
def has_flag(userid, flag):
	index = index_from_userid(userid)
	player = Player(index)
	if is_admin(userid):
		all_flags = admins.getAdmin(player.steamid)
		for x in all_flags:
			if x == flag:
				if all_flags[x] == '1':
					return True
				else:
					return False
	else:
		return False

	
#Ini Manager	
class InI(object):
	def __init__(self):
		self.path = get_addon_path()

		self.admins = os.path.join(self.path, 'admins', 'admins.ini')

	@property
	def getAdmins(self):
		return ConfigObj(self.admins)
		
ini = InI()

class Admins(object):
	def __init__(self):
		self.admins = ini.getAdmins
		
	def getAdmin(self, steamid):
		return self.admins[steamid]
admins = Admins()


###givegoldadmin###

def goldadmin_givegold_menu_build(menu, index):
	menu.clear()
	for player in PlayerIter():
		if player.steamid != 'BOT':
			option = PagedOption('%s' % player.name, player)
			menu.append(option)
			
def gold_amount_select(menu, index, choice):
	userid = choice.value.userid
	amount = int(choice.text)
	player = Player(index)
	addGold(userid,amount,'\x05from admin \x04%s' %player.name)
			
amount_menu = PagedMenu(title='Amount Menu', select_callback=gold_amount_select)

def goldadmin_givegold_menu_select(menu, index, choice):
	player_entity = choice.value
	amount_menu.parent_menu = menu
	amount_menu.append(PagedOption('1', player_entity))
	amount_menu.append(PagedOption('10', player_entity))
	amount_menu.append(PagedOption('50', player_entity))
	amount_menu.append(PagedOption('100', player_entity))
	amount_menu.append(PagedOption('300', player_entity))
	amount_menu.append(PagedOption('500', player_entity))
	amount_menu.send(index)
		
def giveGolddoCommand(userid):
	index = index_from_userid(userid)
	goldadmin_givegold_menu = PagedMenu(title='GiveGold Menu', build_callback=goldadmin_givegold_menu_build, select_callback=goldadmin_givegold_menu_select)
	goldadmin_givegold_menu.send(index)
	
	
###takegoldadmin###

def goldadmin_takegold_menu_build(menu, index):
	menu.clear()
	for player in PlayerIter():
		if player.steamid != 'BOT':
			option = PagedOption('%s' % player.name, player)
			menu.append(option)
			
def takegold_amount_select(menu, index, choice):
	userid = choice.value.userid
	amount = int(choice.text)
	player = Player(index)
	takeGold(userid,amount,'\x05through admin \x04%s' %player.name)
			
takeamount_menu = PagedMenu(title='Amount Menu', select_callback=takegold_amount_select)

def goldadmin_takegold_menu_select(menu, index, choice):
	player_entity = choice.value
	takeamount_menu.parent_menu = menu
	takeamount_menu.append(PagedOption('1', player_entity))
	takeamount_menu.append(PagedOption('10', player_entity))
	takeamount_menu.append(PagedOption('50', player_entity))
	takeamount_menu.append(PagedOption('100', player_entity))
	takeamount_menu.append(PagedOption('300', player_entity))
	takeamount_menu.append(PagedOption('500', player_entity))
	takeamount_menu.send(index)
		
def takeGolddoCommand(userid):
	index = index_from_userid(userid)
	goldadmin_takegold_menu = PagedMenu(title='GiveGold Menu', build_callback=goldadmin_takegold_menu_build, select_callback=goldadmin_takegold_menu_select)
	goldadmin_takegold_menu.send(index)	