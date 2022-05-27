import requests
from player import Player, Session, Achievement, Stream
from game import Match, FullMatch, GameStat, Map
from guild import GuildSearch, Guild

api = 'https://api.vimeworld.ru'

class Token():
	def __init__(self, token_data):
		self.token = token_data['token']
		self.valid = token_data['valid']
		self.type = (token_data['type']) if 'type' in token_data else (None)
		self.limit = (token_data['limit']) if 'limit' in token_data else (0)
		self.owner = (Player(token_data['owner'])) if 'owner' in token_data else (None)

class Vime():
	token = None
	def __init__(self, token = 'xxx'):
		self.token = self.get_token(token)

	def get_token(self, token: str) -> Token:
		return Token(self.get_request(f'/misc/token/{token}'))

	def get_player_by_name(self, name: str) -> Player:
		return Player(self.get_request(f'/user/name/{name}')[0])

	def get_players_by_name(self, names: list) -> Player:
		names_str = list_to_str(names)
		data = self.get_request(f'/user/name/{names_str}')
		players = []
		for p in data: players.append(Player(p))
		return players

	def get_player(self, id: int) -> Player:
		data = self.get_request(f'/user/{id}')
		return Player(data[0])

	def get_players(self, ids: list) -> list:
		ids_str = list_to_str(ids)
		data = self.get_request(f'/user/{ids_str}')
		players = []
		for d in data: players.append(Player(d))
		return players

	def get_friends(self, id: int) -> list:
		data = self.get_request(f'/user/{id}/friends')
		friends = []
		for f in data['friends']:
			friends.append(Player(f))
		return friends

	def get_session(self, id: int) -> Session:
		data = self.get_request(f'/user/{id}/session')
		player_data = data['user']
		player_data['online'] = data['online']
		return Player(player_data)

	def get_sessions(self, ids: list) -> list:
		data = None
		if len(ids) > 50:
			data = self.post_request(f'/user/session', ids)
		else:
			ids_str = list_to_str(ids)
			data = self.get_request(f'/user/session/{ids_str}')
		sessions = []
		for s in data: sessions.append(Player(s))
		return sessions

	def get_stats(self, id: int, games = []) -> list:
		'''Return dict with all player satas
		games - return only the statistics of the specified games
		More view on https://vimeworld.github.io/api-docs/#apiuser_stats_get'''
		params = []
		if len(games) > 0:
			params = [f'games={list_to_str(games)}']
		data = self.get_request(f'/user/{id}/stats', params)
		return data['stats']

	def get_achievements(self, id: int) -> dict:
		data = self.get_request(f'/user/{id}/achievements')
		achievements = {}
		for a in data['achievements']:
			achievements[a['id']] = a['time']
		return achievements

	def get_leaderboards(self, id: int) -> dict:
		data = self.get_request(f'/user/{id}/leaderboards')
		return data['leaderboards']

	def get_matches(self, id: int, count=20, offset=0, after=None, before=None) -> list:
		params = [f'count={count}', f'offset={offset}']
		if after is not None: params.append(f'after={after}')
		if before is not None: params.append(f'before={before}')

		data = self.get_request(f'/user/{id}/matches', params)
		matches = []
		for m in data['matches']: matches.append(Match(m))
		return matches

	def get_match(self, id: int) -> FullMatch:
		return FullMatch(self.get_request(f'/match/{id}'))

	def get_latest_match(self, count=20) -> list:
		params = [f'count={count}']
		data = self.get_request(f'/match/latest', params)
		matches = []
		for m in data: matches.append(Match(m))
		return matches

	def get_match_list(self, after=None, before=None, count=20) -> list:
		params = [f'count={count}']
		if after is not None: params.append(f'after={after}')
		if before is not None: params.append(f'before={before}')
		data = self.get_request(f'/match/list', params)
		matches = []
		for m in data: matches.append(Match(m))
		return matches

	def get_ru_locale(self, parts=None) -> dict:
		params = []
		if parts is not None: params.append(f'parts={list_to_str(parts)}')
		return self.get_request(f'/locale/ru', params)

	def get_games(self) -> list:
		data = self.get_request(f'/misc/games')
		game_stats = []
		for g in data: game_stats.append(GameStat(g))
		return game_stats

	def get_maps(self) -> dict:
		data = self.get_request(f'/misc/maps')
		maps = {}
		for game in data.keys():
			maps[game] = []
			for map_id in data[game].keys():
				map_data = data[game][map_id]
				map_data['id'] = map_id
				maps[game].append(Map(map_data))
		return maps

	def get_achievements_list(self) -> dict:
		data = self.get_request(f'/misc/achievements')
		achievements = {}
		for key in data.keys():
			achievements[key] = []
			for a in data[key]:
				achievements[key].append(Achievement(a))
		return achievements

	def get_staff(self) -> list:
		data = self.get_request(f'/online/staff')
		players = []
		for d in data: players.append(Player(d))
		return players

	def get_streams(self) -> list:
		data = self.get_request(f'/online/streams')
		streams = []
		for s in data: streams.append(Stream(s))
		return streams

	def get_online(self) -> list:
		return self.get_request(f'/online')

	def search_guild(self, query: str) -> list:
		params = [f'query={query}']
		data = self.get_request(f'/guild/search', params)
		guilds = []
		for g in data: guilds.append(GuildSearch(g))
		return guilds

	def get_guild(self, id=None, name=None, tag=None, unsafe=False):
		params = [f'unsafe={unsafe}']
		if id is not None: params.append(f'id={id}')
		if name is not None: params.append(f'name={name}')
		if tag is not None: params.append(f'tag={tag}')
		return Guild(self.get_request(f'/guild/get', params))

	def get_leaderboard_list(self):
		return self.get_request(f'/leaderboard/list')

	def get_leaderboard(self, lb_type, sort="", size=None, offset=None):
		params = []
		if size is not None: params.append(f'size={size}')
		if offset is not None: params.append(f'offset={offset}')
		return self.get_request(f'/leaderboard/get/{lb_type}/{sort}', params)

	def get_request(self, method: str, params = []):
		url = f'{api}{method}?'
		if self.token is not None and self.token.valid: url += f'token={self.token.token}'
		for p in params: url += f'&{p}'
		resp = requests.get(url=url)
		try:
			self.limit_remaining = int(resp.headers['X-RateLimit-Remaining'])
		except: pass
		json = resp.json()
		check_errors(json)
		return json

	def post_request(self, method: str, json):
		url = f'{api}{method}?'
		if self.token is not None and self.token.valid: url += f'token={self.token.token}'
		resp = requests.post(url=url, json=json)
		try:
			self.limit_remaining = int(resp.headers['X-RateLimit-Remaining'])
		except: pass
		json = resp.json()
		check_errors(json)
		return json

def check_errors(json):
	if 'error' in json:
		error = json['error']
		comment = (error['comment']) if 'comment' in error else ('')
		raise VimeError(error['error_code'], error['error_msg'], comment)


def list_to_str(el_list: list) -> str:
	str_list = ''
	for el in el_list:
		if str_list == '': str_list = str(el)
		else: str_list += f',{el}'
	return str_list

class VimeError(Exception):
    def __init__(self, error_code, error_msg, comment):
        self.error_code = error_code
        self.error_msg = error_msg
        self.comment = comment
        super().__init__(self.error_msg)
