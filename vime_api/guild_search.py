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