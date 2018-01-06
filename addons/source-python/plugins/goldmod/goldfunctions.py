import _pickle as cPickle
import os
from players.entity import Player
from messages import SayText2


class PickleApi:
	def __init__(self):
		self.pickle_dict = {}
		self.database_name = '\database.db'
		self.file_path = self.getAddonPath() + self.database_name
		if os.path.isfile(self.file_path):
			if os.path.getsize(self.file_path) > 0:
				with open(self.file_path, 'rb') as pickle_file:
					self.pickle_dict = cPickle.load(pickle_file)
		else:
			self.pickle_dict = {'0':'0'}
			with open(self.file_path, 'wb') as pickle_file:
				cPickle.dump(self.pickle_dict, pickle_file)
				
	def addPlayer(self,steamid):
		if not self.playerExists(steamid):
			self.pickle_dict[steamid] = {}
			self.saveData()
		else:
			return
	
	def deletePlayer(self,steamid):
		if self.playerExists(steamid):
			self.pickle_dict.pop(steamid)
			self.saveData()
		else:
			return
			
	def keySetValue(self,steamid,key,value):
		if self.playerExists(steamid):
			self.pickle_dict[steamid][key] = value
			self.saveData()
		else:
			return
			
	def keyGetValue(self,steamid,key):
		if self.playerExists(steamid):
			value = self.pickle_dict[steamid][key]
			return value
		else:
			return -1
			
	def playerExists(self,key):
		if key in self.pickle_dict:
			return True
		else:
			return False

	def saveData(self):
		with open(self.file_path, 'wb') as pickle_file:
			cPickle.dump(self.pickle_dict, pickle_file)
			
	def getAddonPath(self):
		path = os.path.dirname(os.path.abspath(__file__))
		return path		


pickle = PickleApi()




def addGold(userid, amount,reason=''):
	player = Player.from_userid(userid)
	pickle.keySetValue(player.steamid,'gold',int(pickle.keyGetValue(player.steamid,'gold'))+int(amount))
	if not reason:
		SayText2('\x04[WCS] \x05You have gained \x04%s Gold.' % amount).send(player.index)
	else:
		SayText2('\x04[WCS] \x05You have gained \x04%s Gold %s' % (amount, reason)).send(player.index)
		
def takeGold(userid,amount,reason=''):
	player = Player.from_userid(userid)
	gold = pickle.keyGetValue(player.steamid,'gold')
	to_set = gold-amount
	if to_set < 0:
		to_set = 0
	pickle.keySetValue(player.steamid,'gold',to_set)
	if not reason:
		SayText2('\x04[WCS] \x05You have lost \x04%s Gold.' % amount).send(player.index)
	else:
		SayText2('\x04[WCS] \x05You have lost \x04%s Gold %s' % (amount, reason)).send(player.index)
