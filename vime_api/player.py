from vime_api.guild_search import GuildSearch


class Player():
	def __init__(self, player_data):
		self.id              = player_data['id']
		self.username        = player_data['username']
		self.level           = player_data['level']
		self.levelPercentage = player_data['levelPercentage']
		self.rank            = player_data['rank']
		self.playedSeconds   = player_data['playedSeconds']
		self.lastSeen        = player_data['lastSeen']
		self.guild           = (GuildSearch(player_data['guild'])) if player_data['guild'] is not None else (None)
		self.session         = (Session(player_data['online'])) if 'online' in player_data else None

	def get_friends(self, vime):
		return vime.get_friends(self.id)

	def get_session(self, vime):
		return vime.get_session(self.id)

	def get_stats(self, vime, games = []):
		return vime.get_stats(self.id, games)

	def get_achievements(self, vime):
		return vime.get_achievements(self.id)

	def get_leaderboards(self, vime):
		return vime.get_leaderboards(self.id)

	def get_matches(self, vime, count=20, offset=0, after=None, before=None):
		return vime.get_matches(self.id, count, offset, after, before)

class Session():
	def __init__(self, session_data):
		self.value = session_data['value']
		self.message = (session_data['message']) if 'message' in session_data else ('')
		self.game = (session_data['game']) if 'game' in session_data else ('')

class Achievement():
	def __init__(self, achievement_data):
		self.id          = achievement_data['id']
		self.title       = achievement_data['title']
		self.reward      = achievement_data['reward']
		self.description = achievement_data['description']

class Stream():
	def __init__(self, stream_data):
		self.title    = stream_data['title']
		self.owner    = stream_data['owner']
		self.viewers  = stream_data['viewers']
		self.url      = stream_data['url']
		self.duration = stream_data['duration']
		self.platform = stream_data['platform']
		self.user     = Player(stream_data['user'])