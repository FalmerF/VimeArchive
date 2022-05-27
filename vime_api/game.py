class Match():
	def __init__(self, match_data):
		self.id       = match_data['id']
		self.game     = match_data['game']
		self.date     = match_data['date']
		self.duration = match_data['duration']
		self.players  = match_data['players']
		self.map = (Map(match_data['map'])) if match_data['map'] is not None else (None)

	def get_fullmatch(self, vime):
		return vime.get_match(self.id)

class Map():
	def __init__(self, map_data):
		self.id            = map_data['id']
		self.name          = map_data['name']
		self.teams         = map_data['teams']
		self.playersInTeam = map_data['playersInTeam']

class FullMatch():
	def __init__(self, match_data):
		self.version = match_data['version']
		self.game    = match_data['game']
		self.server  = match_data['server']
		self.start   = match_data['start']
		self.end     = match_data['end']
		self.mapName = (match_data['mapName']) if 'mapName' in match_data else ('')
		self.mapId   = (match_data['mapId']) if 'mapId' in match_data else ('')

		self.win_team = None
		self.win_player = None
		self.win_players = []
		if 'winner' in match_data:
			winner = match_data['winner']
			if winner is not None:
				if 'team' in winner:
					self.win_team = winner['team']
					for t in match_data['teams']:
						if t['id'] == self.win_team: self.win_players = t['members']
				elif 'player' in winner:
					self.win_player = winner['player']
					self.win_players.append(self.win_player)
				elif 'players' in winner:
					self.win_players = winner['players']

		self.players = []
		self.teams   = []
		self.events  = []
		if 'players' in match_data: self.players = match_data['players']
		if 'teams' in match_data: self.teams = match_data['teams']
		if 'events' in match_data: self.events = match_data['events']

class GameStat():
	def __init__(self, stat_data):
		self.id           = stat_data['id']
		self.name         = stat_data['name']
		self.global_stats = (stat_data['global_stats']) if 'global_stats' in stat_data else (None)
		self.season_stats = (stat_data['season_stats']) if 'season_stats' in stat_data else (None)
