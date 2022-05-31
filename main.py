import threading
import os
import sys
import time
import DataBase
import traceback
import utils
import math
import ast
from utils import cls, get_xp_for_lvl
from datetime import datetime, date, timedelta

sys.path.insert(1, os.path.abspath('./vime_api'))
from vime import Vime, VimeError

test_mode = False

#region Tokens
vime_token = ''
vime_test_token = ''
#endregion

if test_mode: 
	vime_token = vime_test_token

lastUsers = {}
locale = {}
cheking_stats = []
checked_matches = []
users_list = []
exceptions = []
activeUsers = []
black_list = utils.get_black_list()
delay = 30
check_players_index = 0
matches_checked_count = 0
status = ''
cycle_start_time = datetime.now()
date = datetime.now()
timestamp = datetime.now().timestamp()
last_leaderboard_check = None
last_leaderboards = {}

db_insert_data = []
db_p_insert_data = [] # For previous day

user_lb_data = {}

#region Colors
GREY    = '\33[90m'
RED    = '\33[91m'
GREEN  = '\33[92m'
YELLOW = '\33[93m'
BLUE   = '\33[94m'
VIOLET = '\33[95m'
BEIGE  = '\33[96m'
WHITE  = '\33[97m'
END    = '\33[0m'
#endregion

def make_db():
	global DB
	DB = DataBase.DataBase(f'{date.day}.{date.month}.{date.year}')

def db_insert(*args):
	global db_insert_data

	db_insert_data.append(args)

def db_p_insert(*args):
	global db_p_insert_data

	db_p_insert_data.append(args)

def db_cycle():
	global db_insert_data
	global db_p_insert_data

	date = datetime.now()
	DB = DataBase.DataBase(f'{date.day}.{date.month}.{date.year}')
	date_p = datetime.now() - timedelta(days=1)
	DB_p = DataBase.DataBase(f'{date_p.day}.{date_p.month}.{date_p.year}')
	while True:
		if date.day != datetime.now().day:
			date = datetime.now()
			DB_p = DB
			DB = DataBase.DataBase(f'{date.day}.{date.month}.{date.year}')
		while len(db_insert_data) > 0:
			args = db_insert_data.pop(0)
			DB.insert(*args)
		while len(db_p_insert_data) > 0:
			args = db_p_insert_data.pop(0)
			DB_p.insert(*args)
		time.sleep(1)

def save_active_players():
	open("players.txt", "a", encoding="utf-8")
	f = open("players.txt", "w", encoding="utf-8")
	players_list = ''
	for p in activeUsers:
		if players_list != '':
			players_list += f',{p}'
		else:
			players_list = str(p)
	f.write(players_list)
	f.close()

def load_active_players():
	global activeUsers
	try:
		f = open("players.txt", "r", encoding="utf-8")
		data = f.read().split(',')
		for d in data:
			activeUsers.append(int(d))
		f.close()
	except FileNotFoundError:
		open("players.txt", "a", encoding="utf-8")

def load_user_lb_data(DB):
	global user_lb_data
	data = DB.get('daily_activity', '*', type='all')
	if data is None: return
	for d in data:
		user_lb_data[d[0]] = ast.literal_eval(d[1])

def save_user_lb_data(DB, user_lb_data, xp_top, online_top, wins_top, games_top):
	DB.delete('daily_activity')
	DB.delete('xp_top')
	DB.delete('online_top')
	DB.delete('wins_top')
	DB.delete('games_top')
	for i in range(1000):
		n = i
		if len(xp_top) > n:
			DB.insert('xp_top', f'{list(xp_top.keys())[n]}, {list(xp_top.values())[n]}')
		if len(online_top) > n:
			DB.insert('online_top', f'{list(online_top.keys())[n]}, {list(online_top.values())[n]}')
		if len(wins_top) > n:
			DB.insert('wins_top', f'{list(wins_top.keys())[n]}, {list(wins_top.values())[n]}')
		if len(games_top) > n:
			DB.insert('games_top', f'{list(games_top.keys())[n]}, {list(games_top.values())[n]}')
	for user in user_lb_data:
		DB.insert('daily_activity', f'{user}, "{user_lb_data[user]}"')

def main_cycle():
	global activeUsers
	global locale
	global delay
	global date
	global timestamp
	global status
	init_cycle()

	while True:
		try:
			pre_start_cycle()
			check_matches()
			get_active_players()
			check_active_players()
		except Exception as e:
			exceptions.append(traceback.format_exc())

		status = 'Waiting...'
		dif = (datetime.now()-cycle_start_time).total_seconds()
		wait_time = delay - dif
		if wait_time > 0:
			time.sleep(wait_time)

def init_cycle():
	global locale
	global status

	status = 'Initializing'

def pre_start_cycle():
	global date
	global timestamp
	global status
	global cycle_start_time
	global matches_checked_count
	global users_list
	global commands_per_min

	status = 'Pre Start Cycle'
	timestamp = datetime.now().timestamp()
	cycle_start_time = datetime.now()
	matches_checked_count = 0
	users_list = []
	commands_per_min = 0
	if date.day != datetime.now().day:
		date = datetime.now()
	if datetime.now().minute % 10 == 0:
		save_active_players()
	try:
		vime.get_player(4921298)
	except:
		pass

def modify_locale_and_make_stats():
	global locale
	locale['game_stats']['bb']['points'] = 'Очков набрано'
	locale['game_stats']['bp']['aliveTime'] = 'Время жизни'
	locale['game_stats']['bw']['aliveTime'] = 'Время жизни'
	locale['game_stats']['bw']['spentGold'] = 'Потрачено золота'
	locale['game_stats']['bw']['spentBronze'] = 'Потрачено бронзы'
	locale['game_stats']['bw']['spentIron'] = 'Потрачено железа'
	locale['game_stats']['bw']['brokenBeds'] = 'Кроватей сломано'
	locale['game_stats']['cp']['spentGold'] = 'Потрачено золота'
	locale['game_stats']['cp']['rpBroken'] = 'Точек рес. сломано'
	locale['game_stats']['mw']['mobsSent'] = 'Послано мобов'
	locale['game_stats']['mw']['income'] = 'Доход'
	locale['game_stats']['bridge']['damage'] = 'Урона нанесено'
	locale['game_stats']['jumpleague']['damage'] = 'Урона нанесено'
	locale['game_stats']['tntrun']['brokenBlocks'] = 'Блоков сломано'
	locale['game_stats']['luckywars']['damage'] = 'Урона нанесено'
	locale['game_stats']['luckywars']['luckyBlocks'] = 'Сломано лаки блоков'
	locale['game_stats']['speedbuilders']['round'] = 'Раундов'
	locale['game_stats']['murder']['wins'] = 'Всего побед'
	locale['game_stats']['murder']['collectedGold'] = 'Собрано золота'
	locale['game_stats']['duels']['wins'] = 'Всего побед'
	locale['game_stats']['duels']['kills'] = 'Убийств'
	locale['game_stats']['hg']['luckyBlocks'] = 'Сломано лаки блоков'
	locale['game_stats']['hg']['aliveTime'] = 'Время жизни'
	locale['game_stats']['sw']['aliveTime'] = 'Время жизни'

	for game in locale['game_stats'].keys():
		locale['game_stats'][game]['games'] = 'Игр'
		for stat in locale['game_stats'][game]:
			if not stat in cheking_stats and stat != 'games':
				cheking_stats.append(stat)

def get_active_players():
	global check_players_index
	global users_list
	global activeUsers
	global status

	status = 'Getting Active Players'
	users = []
	requests_finish_time = datetime.now()
	while vime.limit_remaining > 0:
		n = check_players_index + 50
		while check_players_index < n and check_players_index < len(activeUsers):
			users.append(activeUsers[check_players_index])
			check_players_index += 1
		if check_players_index >= len(activeUsers):
			check_players_index = 0
			break
		elif len(users) >= 1000 or math.ceil(len(users)/50.0) == vime.limit_remaining:
			data = vime.get_sessions(users)
			users_list.extend(data)
			users.clear()
		elif math.ceil(len(users)/50.0) > vime.limit_remaining:
			check_players_index -= len(users)
			return

	if len(users) > 0:
		data = vime.get_sessions(users)
		users_list.extend(data)

def check_active_players():
	global users_list
	global lastUsers
	global activeUsers
	global status

	status = 'Checking Active Players'
	for user in users_list:
		if user.id in black_list: continue
		lastUser = (lastUsers[user.id]) if user.id in lastUsers else (None)
		actions = {}
		level = user.level
		levelPercentage = user.levelPercentage
		rank = user.rank
		online = user.session.value
		game = user.session.game
		if lastUser is not None:
			last_game = lastUser.session.game
			if level != lastUser.level:
				xpDif = 0
				lvl = lastUser.level+1
				xpDif = (1-lastUser.levelPercentage)*get_xp_for_lvl(lastUser.level)
				while lvl < level:
					xpDif += get_xp_for_lvl(lastUser.level)
					lvl += 1
				xpDif += levelPercentage*get_xp_for_lvl(lastUser.level)
				actions['xp'] = int(xpDif)
				actions['level'] = level - lastUser.level
			elif levelPercentage != lastUser.levelPercentage:
				xpDif = (levelPercentage-lastUser.levelPercentage)*get_xp_for_lvl(user.level)
				actions['xp'] = int(xpDif)
				add_user_lb_stat(user.id, 'xp', actions['xp'])
			# if online != lastUser.session.value:
			# 	actions['online'] = online
			# elif online and game != last_game:
			# 	actions['game'] = user.session.message
			if rank != lastUser.rank:
				actions['rank'] = rank
			dif = user.playedSeconds - lastUser.playedSeconds
			if dif > 0:
				date = datetime.now()
				seconds_in_day = date.hour*3600+date.minute*60+date.second

				if dif > seconds_in_day:
					dif_p_day = dif-seconds_in_day
					dif = seconds_in_day

					date = date - timedelta(days=1)
					date = date.replace(hour=23, minute=59, second=59)
					p_adction = {'playedSeconds': dif_p_day}
					db_p_insert('actions', f'{user.id}, "{date}", "{p_adction}"')

				actions['playedSeconds'] = dif
				add_user_lb_stat(user.id, 'online', actions['playedSeconds'])
		lastUsers[user.id] = user

		if len(actions.keys()) > 0:
			db_insert('actions', f'{user.id}, "{datetime.now()}", "{actions}"')

		if timestamp - user.lastSeen > 604800:
			activeUsers.remove(user.id)

def check_matches():
	global checked_matches
	global activeUsers
	global matches_checked_count
	global status

	status = 'Checking Matches'
	if vime.limit_remaining <= 0: return
	matches = vime.get_latest_match(count=100)
	for m in matches:
		if vime.limit_remaining <= 0: return
		if m.id in checked_matches:	continue
		match = m.get_fullmatch(vime)
		checked_matches.append(m.id)
		if len(checked_matches) > 200:	checked_matches.pop(0)
		matches_checked_count += 1

		if match.game == 'SWT': match.game = 'SW'
		if match.game == 'BWH': match.game = 'BW'
		if match.game == 'HGL': match.game = 'HG'
		for p in match.players:
			player_id = p['id']
			if player_id in black_list:
				continue
			match_action = make_match_stats_for_player(match, p)
			db_insert('actions', f'{player_id}, "{datetime.now()}", "{match_action}"')

			add_user_lb_stat(player_id, 'games', 1)
			wins = match_action['match']['wins']
			if wins > 0: add_user_lb_stat(player_id, 'wins',wins)

			if not player_id in activeUsers:
				activeUsers.append(player_id)

		if vime.limit_remaining <= 0:	break

def check_leaderboards():
	global last_leaderboard_check
	global status
	global last_leaderboards
	global next_lb_date

	next_lb_date = None
	while True:
		try:
			last_leaderboard_check = datetime.now()
			leaderboard_list = vime.get_leaderboard_list()

			for leaderboard_data in leaderboard_list:
				table_type = leaderboard_data['type']
				table_sorts = leaderboard_data['sort']
				if table_type == 'guild': continue
				for sort in table_sorts:
					name = f'{table_type}_{sort}'
					while vime.limit_remaining <= 10:
						time.sleep(1)
					leaderboard = vime.get_leaderboard(lb_type=table_type, sort=sort, size=1000)
					users_list = []
					for player in leaderboard['records']:
						user_id = (player['user']['id']) if 'user' in player else (player['id'])
						users_list.append(user_id)

					last_users_list = (last_leaderboards[name]) if name in last_leaderboards else (None)
					last_leaderboards[name] = users_list
					if last_users_list is None: 
						continue

					for user_id in users_list:
						last_index = 1000 
						index = users_list.index(user_id)
						try:
							last_index = last_users_list.index(user_id)
						except:
							pass
						diff = last_index-index
						if diff == 0: continue
						actions = {'leaderboard': {'type': table_type, 'sort': sort, 'diff': diff, 'place': (index+1)}}
						db_insert('actions', f'{user_id}, "{datetime.now()}", "{actions}"')

					for user_id in last_users_list:
						if not user_id in users_list:
							last_index = last_users_list.index(user_id) 
							index = 1000
							diff = last_index-index
							if diff == 0: continue
							actions = {'leaderboard': {'type': table_type, 'sort': sort, 'diff': diff, 'place': '>1000'}}
							db_insert('actions', f'{user_id}, "{datetime.now()}", "{actions}"')
			next_lb_date = datetime.now() + timedelta(minutes=30)
			time.sleep(1800)
		except VimeError:
			time.sleep(10)
		except Exception as e:
			exceptions.append(traceback.format_exc())
			time.sleep(10)

def make_match_stats_for_player(match, player_data):
	player_id = player_data['id']
	match_action = {}
	match_action['match'] = {}
	match_action['match']['game'] = match.game
	match_action['match']['wins'] = (1) if player_id in match.win_players else (0)
	is_win = player_id in match.win_players

	if match.game == 'BW':
		match_action['match']['kills'] = player_data['kills']
		match_action['match']['bedBreaked'] = player_data['brokenBeds']
	elif match.game == 'CP':
		match_action['match']['kills'] = player_data['kills']
		match_action['match']['resourcePointsBreaked'] = player_data['rpBroken']
	elif match.game == 'DUELS':
		match_action['match']['winStreak'] = player_data['winStreak']
	elif match.game == 'HG':
		match_action['match']['kills'] = player_data['kills']
		if 'luckyBlocks' in player_data:
			match_action['match']['luckyBlocks'] = player_data['luckyBlocks']
	elif match.game == 'SW':
		match_action['match']['kills'] = (player_data['kills']) if 'kills' in player_data else (0)
	elif match.game == 'MURDER':
		match_action['match']['kills'] = (player_data['kills']) if 'kills' in player_data else (0)
		match_action['match']['wins_as_innocent'] = (1) if is_win and player_data['role'] == 'innocent' else (0)
		match_action['match']['wins_as_maniac'] = (1) if is_win and player_data['role'] == 'maniac' else (0)
		match_action['match']['wins_as_detective'] = (1) if is_win and player_data['role'] == 'detective' else (0)
	else:
		for key in player_data.keys():
			if key != 'id':
				match_action['match'][key] = player_data[key]
	return match_action

def update_user_lb_cycle():
	global user_lb_data
	DB = DataBase.DataBase('', file_name='user_lb.db')
	load_user_lb_data(DB)
	date = datetime.now()

	while True:
		try:
			xp_top = {}
			online_top = {}
			wins_top = {}
			games_top = {}
			if date.day != datetime.now().day:
				date = datetime.now()
				user_lb_data = {}

			lb_data_copy = user_lb_data.copy()
			for user in lb_data_copy:
				xp_top[user] = lb_data_copy[user]['xp']
				online_top[user] = lb_data_copy[user]['online']
				wins_top[user] = lb_data_copy[user]['wins']
				games_top[user] = lb_data_copy[user]['games']

			xp_top = dict(sorted(xp_top.items(), key=lambda item: item[1], reverse=True))
			online_top = dict(sorted(online_top.items(), key=lambda item: item[1], reverse=True))
			wins_top = dict(sorted(wins_top.items(), key=lambda item: item[1], reverse=True))
			games_top = dict(sorted(games_top.items(), key=lambda item: item[1], reverse=True))
			save_user_lb_data(DB, lb_data_copy, xp_top, online_top, wins_top, games_top)
		except Exception as e:
			exceptions.append(traceback.format_exc())
			time.sleep(10)
		time.sleep(600)

def add_user_lb_stat(user_id: int, stat_name: str, count: int):
	if user_id not in user_lb_data:
		user_lb_data[user_id] = {'xp': 0, 'online': 0, 'wins': 0, 'games': 0}
		
	user_lb_data[user_id][stat_name] += count

def log_cycle():
	global cycle_start_time
	global delay
	while True:
		cls()
		dif = (datetime.now()-cycle_start_time).total_seconds()
		wait_time = delay - dif

		progress_bar = f'{GREY}[{GREEN}'
		progress = int((delay-wait_time)/delay*10)
		progress_bar += '■'*progress
		progress_bar += WHITE
		progress_bar += '■'*(10-progress)
		progress_bar += f'{GREY}]'

		print(f'{YELLOW}Current Status: {WHITE}{status}')
		print(f'{YELLOW}Checked Players: {WHITE}{len(users_list)}')
		print(f'{YELLOW}Checked Matches: {WHITE}{matches_checked_count}')
		print(f'{YELLOW}Next LB check: {WHITE}{next_lb_date}')
		print(f'\n{YELLOW}Limit Remaining: {WHITE}{vime.limit_remaining}')
		print(f'{YELLOW}Active Players: {WHITE}{len(activeUsers)}\n')
		# print(progress_bar)

		print('\n\nExceptions')
		for e in exceptions: print(e)
		if len(exceptions) > 2:
			exceptions.pop(0)
		time.sleep(1)

load_active_players()

vime = Vime(vime_token)
locale = utils.get_locale()

threading.Thread(target=main_cycle).start()
threading.Thread(target=check_leaderboards).start()
threading.Thread(target=db_cycle).start()
threading.Thread(target=update_user_lb_cycle).start()
threading.Thread(target=log_cycle).start()