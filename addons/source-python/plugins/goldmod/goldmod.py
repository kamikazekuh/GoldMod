import os
import sys
from path import path as Path
from paths import PLUGIN_PATH
from configobj import ConfigObj
from menus import PagedOption
from messages import SayText2
from engines.server import execute_server_command, queue_command_string
from commands.server import ServerCommand
import wcs
from commands.say import SayCommand
from commands.client import ClientCommand
from menus import PagedMenu
from events import Event
from filters.players import PlayerIter
import es
import core
from cvars import ConVar
from config.manager import ConfigManager
from entities.entity import Entity
from commands.say import SayCommand
from commands.client import ClientCommand
from listeners.tick import Delay
from players.entity import Player
from filters.players import PlayerIter
import _pickle as cPickle
from mathlib import Vector
from filters.weapons import WeaponIter

from goldmod import goldadmin
from goldmod import goldfunctions
from goldmod.goldfunctions import pickle, addGold, takeGold
from goldmod import goldshow
	
items = os.path.join(PLUGIN_PATH+'/goldmod', 'items', 'items.ini')
items = ConfigObj(items)


addon_config = ConfigManager('goldmod')
gold_per_kill = addon_config.cvar('gold_per_kill', '15')
gold_per_headshot = addon_config.cvar('gold_per_headshot', '5')
gold_per_knife = addon_config.cvar('gold_per_knife', '5')
addon_config.write()

golditems = {}
maxitems = {}

for player in PlayerIter('all'):
	if player.userid not in golditems:
		golditems[player.userid] = {}
		golditems[player.userid]['all'] = {}

class itemDatabase(object):
	def __init__(self):
		self.items = items
		self.sectionlist = []
		self.itemlist = []
		self.itemtosection = {}

		for section in self.items:
			self.sectionlist.append(section)
			for item in self.items[section]:
				if item == 'desc':
					continue

				self.itemlist.append(item)
				self.itemtosection[item] = section

	def __contains__(self, item):
		return item in self.items

	def __iter__(self):
		for x in self.items:
			yield x

	def __getitem__(self, item):
		return self.items[item]

	def keys(self):
		return self.items.keys()

	def getSection(self, section):
		return dict(self.items[section])

	def getItem(self, item):
		return dict(self.items[self.getSectionFromItem(item)][item])

	def getSections(self):
		return list(self.sectionlist)

	def getItems(self):
		return list(self.itemlist)

	def getSectionFromItem(self, item):
		if item in self.itemtosection:
			return self.itemtosection[item]

		return None

	def getAll(self):
		return dict(self.items)
itemdb = itemDatabase()



def goldmenu_menu_cats_build(menu, index):
	menu.clear()
	allitems = itemdb.getSections()
	for item in allitems:
		option = PagedOption('%s' % str(item), item)
		menu.append(option)

def goldmenu_menu_cats_select(menu, index, choice):
	userid = Player(index).userid
	doCommand1(userid, choice.value)

goldmenu_menu_cats = PagedMenu(title='Goldshop Menu' , build_callback=goldmenu_menu_cats_build, select_callback=goldmenu_menu_cats_select)

def doCommand(userid):
	player = Player.from_userid(userid)
	index = player.index
	gold = pickle.keyGetValue(player.steamid,'gold')
	allitems = itemdb.getSections()
	if len(allitems):
		goldmenu_menu_cats.title = 'Goldshop Menu\nGold: %s' % gold
		goldmenu_menu_cats.send(index)
		
		
@SayCommand('showgold')
@ClientCommand('showgold')
def show_gold(command, index, team=None):
	SayText2('\x04[WCS] \x05You have \x04%s \x05Gold' % pickle.keyGetValue(Player(index).steamid,'gold')).send(index)

@SayCommand('goldshop')
@ClientCommand('goldshop')
def gold_shop(command, index, team=None):
	doCommand(Player(index).userid)
	
item_names = []

def goldmenu_menu_subcats_build(menu, index):
	menu.clear()
	userid = Player(index).userid
	section = menu.title
	goldmenu_menu_subcats.parent_menu = goldmenu_menu_cats
	items.walk(gather_subsection)
	for item in item_names:
		item_sec = itemdb.getSectionFromItem(item)
		if item_sec == section:
			iteminfo = itemdb.getItem(item)
			option = PagedOption('%s - %s$' % (str(iteminfo['name']), str(iteminfo['cost'])), item)
			menu.append(option)
				
	
def gather_subsection(section, key):
	if section.depth > 1:
		if section.name not in item_names:
			item_names.append(section.name)
			
def goldmenu_menu_subcats_select(menu, index, choice):
	userid = Player(index).userid
	addItem(userid, choice.value)
	
goldmenu_menu_subcats = PagedMenu(build_callback=goldmenu_menu_subcats_build, select_callback=goldmenu_menu_subcats_select)
	
def doCommand1(userid, value):
	player = Player.from_userid(userid)
	goldmenu_menu_subcats.title = value
	goldmenu_menu_subcats.send(player.index)
	
@Event('player_activate')
def player_activate(ev):
	player = Player.from_userid(int(ev['userid']))
	if not pickle.playerExists(player.steamid):
		pickle.addPlayer(player.steamid)
		pickle.keySetValue(player.steamid,'kills', 0)
		pickle.keySetValue(player.steamid,'gold',0)
	golditems[player.userid]= {}
	golditems[player.userid]['all'] = {}
	
	
@ServerCommand('wcs_givegold')
def give_gold(command):
	userid = int(command[1])
	amount = int(command[2])
	if len(command) > 3:
		reason = str(command[3])
	else:
		reason = ''
	addGold(userid,amount,reason)
	
	
def addGold(userid, amount,reason=''):
	player = Player.from_userid(userid)
	pickle.keySetValue(player.steamid,'gold',int(pickle.keyGetValue(player.steamid,'gold'))+int(amount))
	if not reason:
		SayText2('\x04[WCS] \x05You have gained \x04%s Gold.' % amount).send(player.index)
	else:
		SayText2('\x04[WCS] \x05You have gained \x04%s Gold %s' % (amount, reason)).send(player.index)
	

		
def addItem(userid, item, pay=True, tell=True):
	section = itemdb.getSectionFromItem(item)
	userid = int(userid)
	player = Player.from_userid(userid)
	if not userid in golditems:
		golditems[userid] = {}
	c = canBuy(userid, item, pay)

	if not c:
		if pay:
			gold = int(pickle.keyGetValue(player.steamid,'gold'))
			pickle.keySetValue(player.steamid,'gold',gold-int(items[section][item]['cost']))
		if tell:
			SayText2('\x04[WCS] \x04You have purchased: \x05%s' % items[section][item]['name']).send(player.index)

		cfg = 'all'
		if not cfg in golditems[userid]:
			golditems[userid][cfg] = {}

		if not item in golditems[userid][cfg]:
			golditems[userid][cfg][item] = 0

		golditems[userid][cfg][item] += 1

		if not userid in maxitems:
			maxitems[userid] = {}

		if not section in maxitems[userid]:
			maxitems[userid][section] = 0

		maxitems[userid][section] += 1

		checkBuy(userid, item)

	elif c == 1:
		doCommand1(userid, section)
		if tell:
			SayText2('\x04[WCS] \x05Item \x04%s \x05is out of stock.' % items[section][item]['name']).send(player.index)
	elif c == 2:
		doCommand1(userid, section)
		if tell:
			payment = int(pickle.keyGetValue(player.steamid,'gold'))
			SayText2('\x04[WCS] \x05You need \x04%s \05to buy \x04%s.' % (int(items[section][item]['cost'])-payment, items[section][item]['name'])).send(player.index)
	elif c == 3:
		doCommand1(userid, section)
		if tell:
			SayText2('\x04[WCS] \x05You need \x04%s \x05more \x04kills \x05to access this item' % (int(items[section][item]['required'])-int(pickle.keyGetValue(player.steamid,'kills')))).send(player.index)
			
			
def canBuy(userid, item, pay=True):
	userid = int(userid)
	iteminfo = itemdb.getItem(item)
	player = Player.from_userid(userid)
	section = itemdb.getSectionFromItem(item)
	if not userid in maxitems:
		maxitems[userid] = {}

	if not section in maxitems[userid]:
		maxitems[userid][section] = 0
	
	cfg = 'all'
	if cfg in golditems[userid]:
		if item in golditems[userid][cfg]:
			if int(iteminfo['max_amount']) and golditems[userid][cfg][item] >= int(iteminfo['max_amount']):
				return 1
				
	if int(iteminfo['required']) > int(pickle.keyGetValue(player.steamid,'kills')):
		core.console_message('Test')
		return 3
			
	payment = int(pickle.keyGetValue(player.steamid,'gold'))

	if payment >= int(iteminfo['cost']) or not pay:
		return 0
	return 2
	
def checkBuy(userid, item):
	userid = int(userid)
	iteminfo = items[itemdb.getSectionFromItem(item)][item]
	player = Player.from_userid(userid)
	ConVar('gold_userid').set_int(player.userid)
	block = iteminfo['block']
	es.doblock('goldmod/goldblocks/'+str(block))
		
@ServerCommand('gold_remove_item')
def gold_remove_items(command):
	userid = int(command[1])
	todo = str(command[2])
	if todo == 'all':
		removeItems(userid)
	else:
		if ";" in todo:
			todo = todo.split(";")
			for x in todo:
				removeSingleItem(userid,todo)
		else:
			removeSingleItem(userid,todo)
	
def removeSingleItem(userid, item_remove):
	if userid in golditems:
		for x in golditems[userid]:
			for q in golditems[userid][x].copy():
				item = itemdb.getItem(q)
				golditems[userid][x][q] = 0	
	
def removeItems(userid):
	if userid in golditems:
		for x in golditems[userid]:
			for q in golditems[userid][x].copy():
				item = itemdb.getItem(q)
				golditems[userid][x][q] = 0	
				
				
def showitems_menu_build(menu, index):
	menu.clear()
	player = Player(index)
	for x in golditems[player.userid]:
		for y in golditems[player.userid][x]:
			if int(golditems[player.userid][x][y]) > 0:
				for z in items:
					if y in items[z]:
						name = items[z][y]['name']
						option = PagedOption('%s' % str(name), name)
						menu.append(option)
		
					
def showitems_menu_select(menu, index, choice):
	return


@SayCommand('showgolditems')
@ClientCommand('showgolditems')
def _showitems_command(command, index, team=None):
	player = Player(index)
	count = 0
	for x in golditems[player.userid]:
		for y in golditems[player.userid][x]:
			if golditems[player.userid][x][y] > 0:
				count += 1
	if count > 0:
		showitem_menu = PagedMenu(title='Gold Inventory', build_callback=showitems_menu_build, select_callback=showitems_menu_select)
		showitem_menu.send(index)
	else:
		SayText2("\x04[WCS] \x05You don't have any goldshop items!").send(index)
		
@ServerCommand('wcs_create_fire')
def create_fire(command):
	ent = Entity.create('env_fire')
	ent.fire_size = int(command[4])
	ent.origin = Vector(float(command[1]),float(command[2]),float(command[3]))
	ent.flags = 4
	ent.spawn()
	ent.call_input('StartFire')
	Delay(float(command[5]),ent.remove)
		
@ServerCommand('poison_smoke')
def poison_smoke(command):
	#poison_smoke <x> <y> <z> <userid> <range> <damage> <delay> <duration>
	do_poison_smoke(Vector(float(command[1]),float(command[2]),float(command[3])),int(command[4]),float(command[5]),int(command[6]),float(command[7]),float(command[8]))
	
	
	
def do_poison_smoke(position,userid,range,damage,delay,duration):
	attacker = Player.from_userid(int(userid))
	duration = duration - delay
	for player in PlayerIter('all'):
		if player.origin.get_distance(position) <= range:
			player.take_damage(damage,attacker_index=attacker.index, weapon_index=None)
	if duration > 0:
		Delay(delay,do_poison_smoke,(position,userid,range,damage,delay,duration))
		
################Events#################

@Event('player_death')
def player_death(ev):
	victim = ev['userid']
	attacker = ev['attacker']
	atk_player = Player.from_userid(attacker)
	vic_player = Player.from_userid(victim)
	weapon = ev['weapon']
	if atk_player.team != vic_player.team:
		addGold(attacker,gold_per_kill.get_int(),"for making a kill")
		if 'knife' in weapon:
			addGold(attacker,gold_per_knife.get_int(),"for a knife kill")
		if ev['headshot'] == 1:
			addGold(attacker,gold_per_headshot.get_int(),"for a headshot kill")
		kills = pickle.keyGetValue(atk_player.steamid,'kills')
		kills += 1
		pickle.keySetValue(atk_player.steamid,'kills',kills)