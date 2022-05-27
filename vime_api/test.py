import os
import traceback
from vime import Vime
from player import Player, Session

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

vime1 = Vime()
vime2 = Vime('DZGulqm9XuFuLw6enugkSqZWdqLO9FW')

FalmerF_id = 4921298
Katakuri_id = 3147588
Sanrix_id = 475110
Avallacz_id = 5532335

tests = ['get_player_by_name_test', 'get_players_by_name_test', 'get_player_by_id_test', 'get_players_by_id_test', 'get_friends_test',
'get_session_test', 'get_stats_test', 'get_achievements_test', 'get_leaderboards_test', 'get_matches_test', 'get_sessions_test', 'search_guild_test',
'get_guild_test', 'get_online_test', 'get_streams_test', 'get_staff_test', 'get_match_test', 'get_latest_match_test', 'get_match_list_test',
'get_ru_locale_test', 'get_games_test', 'get_maps_test', 'get_achievements_list_test']
test_exceptions = {}
completed_tests = {}
normal_completed_times = 2

def cls():
	os.system('cls' if os.name=='nt' else 'clear')

def test(vime: Vime):
	for test in tests:
		try:
			print(f'Test "{test}"')
			globals()[test](vime)
			if test in completed_tests: completed_tests[test] += 1
			else: completed_tests[test] = 1
		except:
			test_exceptions[test] = traceback.format_exc()
		print('')

def get_player_by_name_test(vime: Vime):
	player = vime.get_player_by_name('FalmerF')
	log_player_info(player)

def get_players_by_name_test(vime: Vime):
	players = vime.get_players_by_name(['FalmerF', 'Katakuri', 'Sanrix', 'Avallacz'])
	for p in players: log_player_info(p)

def get_player_by_id_test(vime: Vime):
	player = vime.get_player(FalmerF_id)
	log_player_info(player)

def get_players_by_id_test(vime: Vime):
	players = vime.get_players([FalmerF_id, Katakuri_id, Sanrix_id, Avallacz_id])
	for p in players: log_player_info(p)

def get_friends_test(vime: Vime):
	players = vime.get_friends(FalmerF_id)
	for p in players: log_player_info(p)

def get_session_test(vime: Vime):
	player = vime.get_session(FalmerF_id)
	log_player_session(player)

def get_stats_test(vime: Vime):
	stats = vime.get_stats(FalmerF_id, ['LUCKYWARS'])
	log_player_stats(stats)

def get_achievements_test(vime: Vime):
	achievements = vime.get_achievements(FalmerF_id)
	print(f'Achievements: {len(achievements.keys())}')

def get_leaderboards_test(vime: Vime):
	leaderboards = vime.get_leaderboards(FalmerF_id)
	print(f'First Leaderboard: Type {leaderboards[0]["type"]}  Sort {leaderboards[0]["sort"]}  Place {leaderboards[0]["place"]}')

def get_matches_test(vime: Vime):
	matches = vime.get_matches(FalmerF_id, count=1, offset=5)
	log_match(matches[0])

def get_sessions_test(vime: Vime):
	players = vime.get_sessions([FalmerF_id, Katakuri_id, Sanrix_id, Avallacz_id])
	for p in players: log_player_session(p)

def search_guild_test(vime: Vime):
	guilds = vime.search_guild('leto')
	log_guild(guilds[0])

def get_guild_test(vime: Vime):
	guild = vime.get_guild(id=9658)
	log_guild(guild)

def get_online_test(vime: Vime):
	online = vime.get_online()
	print(f'Total Online: {online["total"]}')

def get_streams_test(vime: Vime):
	streams = vime.get_streams()
	print(f'Streams: {len(streams)}')

def get_staff_test(vime: Vime):
	staff = vime.get_staff()
	print(f'Staff Online: {len(staff)}')

def get_match_test(vime: Vime):
	match = vime.get_match(421318368709050368)
	log_fullmatch(match)

def get_latest_match_test(vime: Vime):
	matches = vime.get_latest_match()
	log_match(matches[0])

def get_match_list_test(vime: Vime):
	matches = vime.get_match_list(after=421318368709050368, count=1)
	log_match(matches[0])

def get_ru_locale_test(vime: Vime):
	locale = vime.get_ru_locale()
	print(f'Locale Games: {len(locale["games"].keys())}')

def get_games_test(vime: Vime):
	games = vime.get_games()
	game = games[3]
	print(f'{game.id} Global Stats: {len(game.global_stats)}')

def get_maps_test(vime: Vime):
	maps = vime.get_maps()
	game_map = maps['BW'][0]
	print(f'Map id: {game_map.id} name: {game_map.name}')

def get_achievements_list_test(vime: Vime):
	achievements = vime.get_achievements_list()
	a = achievements['DeathRun'][5]
	print(f'Achievement id: {a.id} title: {a.title} reward: {a.reward}')

# Loggers
def log_player_info(player: Player):
	print(f'{player.username} [{player.rank}] (level: {player.level}  {player.levelPercentage}%)')

def log_player_session(player: Player):
	print(f'Online: {player.session.value}  Message: {player.session.message}  Game: {player.session.game}')

def log_player_stats(stats):
	print(f"LW   Kills: {stats['LUCKYWARS']['global']['kills']}  Wins: {stats['LUCKYWARS']['global']['wins']}")

def log_match(match):
	print(f'Match id: {match.id} game: {match.game} players: {match.players}')

def log_fullmatch(match):
	print(f'Match server: {match.server} game: {match.game} players: {len(match.players)}')

def log_guild(guild):
	print(f'Guild id: {guild.id} name: {guild.name} tag: {guild.tag}')

cls()
try:
	test(vime1)
	test(vime2)
except:
	print(traceback.format_exc())

for test in tests:
	if test in completed_tests:
		times = completed_tests[test]
		if times == normal_completed_times:
			print(f'{GREEN}"{test}" completed {completed_tests[test]} times')
		else:
			print(f'{YELLOW}"{test}" completed {completed_tests[test]} times')
	else:
		print(f'{RED}"{test}" not completed')
		if test in test_exceptions:
			print(f'{GREY}Exception:\n{test_exceptions[test]}')
print(f'\n{YELLOW}Completed {len(completed_tests.keys())} of {len(tests)} tests')
input('\nЗавершить...')