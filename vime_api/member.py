from vime_api.player import Player


class Member():
	def __init__(self, member_data, guild):
		member_data['user']['guild'] = guild
		self.user       = Player(member_data['user'])
		self.status     = member_data['status']
		self.joined     = member_data['joined']
		self.guildCoins = member_data['guildCoins']
		self.guildExp   = member_data['guildExp']