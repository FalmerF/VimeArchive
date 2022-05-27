import os
import DataBase
import ast
from datetime import datetime, date, timedelta

def cls():
	os.system('cls' if os.name=='nt' else 'clear')

def get_xp_for_lvl(lvl: int):
	return 8000+lvl*2000

def get_player_stats(playerid: int, date: str):
	DB = DataBase.DataBase(date, False)
	if DB.valid is False:
		return None
	data = DB.get('actions', '*', f'user_id={playerid}', 'all')
	if len(data) == 0: return None
	xp = 0
	played_seconds = 0
	games = {}
	for d in data:
		action = ast.literal_eval(d[2])
		for a in action.keys():
			if a == 'xp':
				xp += action['xp']
			elif a == 'playedSeconds':
				played_seconds += action['playedSeconds']
			elif a == 'match':
				match = action['match']
				game = match['game'].lower()
				if not game in games:
					games[game] = {'games': 0}
				games[game]['games'] += 1
				for stat in match.keys():
					if stat == 'game': continue
					if game == 'duels' and stat == 'winStreak':
						if 'maxstrike' in games[game]:
							if match[stat] > games[game]['maxstrike']:
								games[game]['maxstrike'] = match[stat]
						else:
							games[game]['maxstrike'] = match[stat]
					elif game == 'mw' and stat == 'income':
						if 'maxIncome' in games[game]:
							if match[stat] > games[game]['maxIncome']:
								games[game]['maxIncome'] = match[stat]
						else:
							games[game]['maxIncome'] = match[stat]
					else:
						try:
							if stat in games[game]:
								games[game][stat] += int(match[stat])
							else:
								games[game][stat] = int(match[stat])
						except:
							pass

	return {'games': games, 'xp': xp, 'played_seconds': played_seconds}

def get_player_stats_range(playerid: int, start_date, end_date):
	delta = end_date - start_date
	if delta.days < 0:
		t = start_date
		start_date = end_date
		end_date = t
	elif delta.days > 31:
		return None
	delta = end_date - start_date
	games = {}
	stats = {'games': games, 'xp': 0, 'played_seconds': 0}
	for i in range(delta.days + 1):
		date = start_date + timedelta(days=i)
		date_str = f'{date.day}.{date.month}.{date.year}'
		stats_loc = get_player_stats(playerid, date_str)
		if stats_loc is None: continue
		stats['xp'] += stats_loc['xp']
		stats['played_seconds'] += stats_loc['played_seconds']
		games_loc = stats_loc['games']

		for game in games_loc.keys():
			if game in games:
				for key in games_loc[game].keys():
					if key in games[game]:
						games[game][key] += games_loc[game][key]
					else:
						games[game][key] = games_loc[game][key]
			else:
				games[game] = games_loc[game]

	if len(games.keys()) == 0 and stats['xp'] == 0 and stats['played_seconds'] == 0:
		return None
	return stats

def get_player_actions(playerid: int, date: str):
	DB = DataBase.DataBase(date, False)
	if DB.valid is False:
		return None
	data = DB.get('actions', '*', f'user_id={playerid}', 'all')
	if len(data) == 0: return None
	return data

def get_player_actions_range(playerid: int, start_date, end_date):
	delta = end_date - start_date
	if delta.days < 0:
		t = start_date
		start_date = end_date
		end_date = t
	elif delta.days > 31:
		return None
	delta = end_date - start_date
	actions = []
	for i in range(delta.days + 1):
		date = start_date + timedelta(days=i)
		date_str = f'{date.day}.{date.month}.{date.year}'
		actions_loc = get_player_actions(playerid, date_str)
		if actions_loc is None: continue
		actions.extend(actions_loc)
	return actions

def get_player_lb_range(playerid: int, start_date, end_date):
	delta = end_date - start_date
	if delta.days < 0:
		t = start_date
		start_date = end_date
		end_date = t
	elif delta.days > 31:
		return None
	delta = end_date - start_date
	total_lb = {}
	for i in range(delta.days + 1):
		date = start_date + timedelta(days=i)
		date_str = f'{date.day}.{date.month}.{date.year}'
		actions_loc = get_player_actions(playerid, date_str)
		if actions_loc is None: continue
		for d in actions_loc:
			action = ast.literal_eval(d[2])
			if not 'leaderboard' in action: continue
			
			lb = action['leaderboard']
			lb_type = (total_lb[lb['type']]) if lb['type'] in total_lb else ({})
			lb_sort = (lb_type[lb['sort']]) if lb['sort'] in lb_type else ({'diff': 0, 'place': 0})
			lb_sort['diff'] += lb['diff']
			lb_sort['place'] = lb['place']
			lb_type[lb['sort']] = lb_sort
			total_lb[lb['type']] = lb_type
	return total_lb

def format_date(date: str):
	date_list = date.split('.')
	day = int(date_list[0])
	month = int(date_list[1])
	year = int(date_list[2])
	if day <= 0 or day > 31:
		raise Exception('bad date')
	elif month <= 0 or month > 12:
		raise Exception('bad date')
	elif year < 2000:
		if year < 100:
			year = 2000+year
		else:
			raise Exception('bad date')
	date = f'{day}.{month}.{year}'
	return date

def get_locale(path='locale.txt'):
	f = open(path, "r", encoding="utf-8")
	locale = ast.literal_eval(f.read())
	f.close()
	return locale

def get_black_list(path='black_list.txt'):
	f = open(path, "r", encoding="utf-8")
	data = f.read().split(',')
	black_list = []
	for d in data:
		black_list.append(int(d))
	f.close()
	return black_list
