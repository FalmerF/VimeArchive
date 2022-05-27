import player

class GuildSearch():
	def __init__(self, guild_data):
		self.id              = guild_data['id']
		self.name            = guild_data['name']
		self.tag             = guild_data['tag']
		self.color           = guild_data['color']
		self.level           = guild_data['level']
		self.levelPercentage = guild_data['levelPercentage']
		self.avatar_url      = guild_data['levelPercentage']

	def get_guild(self, vime, unsafe=False):
		return vime.get_guild(id=self.id, unsafe=unsafe)

class Guild():
	def __init__(self, guild_data):
		self.id              = guild_data['id']
		self.name            = guild_data['name']
		self.tag             = guild_data['tag']
		self.color           = guild_data['color']
		self.level           = guild_data['level']
		self.levelPercentage = guild_data['levelPercentage']
		self.avatar_url      = guild_data['levelPercentage']
		self.totalExp        = guild_data['totalExp']
		self.totalCoins      = guild_data['totalCoins']
		self.created         = guild_data['created']
		self.web_info        = guild_data['web_info']
		self.perks           = guild_data['perks']
		self.members         = []
		for m in guild_data['members']: self.members.append(Member(m, guild_data))

class Member():
	def __init__(self, member_data, guild):
		member_data['user']['guild'] = guild
		self.user       = player.Player(member_data['user'])
		self.status     = member_data['status']
		self.joined     = member_data['joined']
		self.guildCoins = member_data['guildCoins']
		self.guildExp   = member_data['guildExp']