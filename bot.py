import discord
import time
import requests
import data_base
import os
import sys
import threading
import ast
import traceback
import pathlib
import utils
from datetime import datetime, date, timedelta
from discord.ext import commands
from discord_components import DiscordComponents, Button, Select, SelectOption, ButtonStyle, Component
from utils import cls, get_player_stats, get_player_actions, format_date, get_xp_for_lvl

sys.path.insert(1, os.path.abspath('./vime_api'))
from vime import Vime, VimeError

test_mode = True

#region Tokens
test_token = 'OTUwODgzNzIxMzMzMDYzNzEw.YifZeQ.nIFVb3Gd62V_7of6SbC_meVwntI'
token      = 'OTQ4MTMzNDk1MDg2MTI5MTUy.Yh3YIA.gxIUNy1tDnbOGVJMAHdhD-Z5SOo'
#endregion

prefix = '.'

if test_mode: 
	token = test_token
	prefix = ';'

bot = commands.Bot(prefix, intents=discord.Intents.all())
bot.remove_command('help')
discord_components = None
vime = Vime()

last_commands = []
black_list = utils.get_black_list()
locale = utils.get_locale()
bot_name = ''

lb_sort_locale = {'level': 'Уровень', 'online': 'Онлайн', 'kills': 'Убийств', 'wins': 'Побед', 'bedBreaked': 'Кроватей сломано', 'total_wins': 'Всего побед', 'total_games': 'Всего игр', 'rate': 'Рейтинг', 'points': 'Очков', 'total_blocks': 'Всего блоков', 'earned_money': 'Заработано монет', 'wins_as_maniac': 'Побед за Маньяка', 'tamed_sheep': 'Перетащено овец'}
lb_list = vime.get_leaderboard_list()
lb_names = {}
for lb in lb_list:
	lb_names[lb['type']] = lb['description'].replace('(в этом месяце)', '(за сезон)')

top_title_locale = {'xp': 'Топ по опыту (за день)', 'online': 'Топ по онлайну (за день)', 'wins': 'Топ по победам (за день)', 'games': 'Топ по играм (за день)'}

#Analytics
commands_per_day = 0

@bot.event
async def on_ready():
	global discord_components
	global close_emoji
	global falmer
	global commands_list
	global bot_name

	bot_name = bot.user.name
	discord_components = DiscordComponents(bot)

	discord_components.add_callback(component=Button, callback=on_button_click)

	guild = await bot.fetch_guild(942022474361634887)
	close_emoji = await guild.fetch_emoji(950372815096389702)

	commands_list = []
	for command in bot.commands:
		commands_list.append(command.name)
		commands_list.extend(command.aliases)

	game = discord.Activity(name=f'{prefix}info')
	game.type = discord.ActivityType.playing
	await bot.change_presence(activity=game)
	threading.Thread(target=log_cycle).start()

@bot.event
async def on_message(message: discord.Message):
	global commands_per_day
	command = message.content[1:].split(' ')[0]
	if not message.author.bot and message.content.startswith(prefix) and command in commands_list:
		commands_per_day += 1
		if message.author.id in last_commands:
			await message.reply('Подождите немного, прежде чем использовать команды вновь...', delete_after=10)
			return
		last_commands.append(message.author.id)
		await bot.process_commands(message)

def update():
	global last_commands
	global players_lb

	players_lb = {}
	DB = data_base.DataBase('', file_name='user_lb.db')

	i = 10
	while True:
		last_commands = []
		if i >= 10:
			i = 0
			players_lb['xp'] = DB.get('xp_top', '*', type='all')
			players_lb['online'] = DB.get('online_top', '*', type='all')
			players_lb['wins'] = DB.get('wins_top', '*', type='all')
			players_lb['games'] = DB.get('games_top', '*', type='all')
		i += 1
		time.sleep(10)

@bot.command()
async def stats(ctx, nick: str, date: str):
	player = find_player_by_name(nick)
	if player is None:	
		await ctx.reply(content=f'Игрок с ником `{nick}` не найден.')
		return

	try:
		date = format_date(date)
	except:
		await ctx.reply(content='Укажите дату в формате `dd.mm.yyyy`.')
		return

	playerid = player.id
	if player.id in black_list:
		await ctx.reply(content='Данные этого игрока не подлежат записи, кажется он что-то натворил :(')
		return

	rank_name = locale["ranks"][player.rank.lower()]['name']
	if rank_name != '': rank_name = f'[{rank_name}]'

	player_stats = get_player_stats(player.id, date)
	if player_stats is None:
		await ctx.reply(content='Данных об игроке на указанную дату нет.')
		return

	games = player_stats['games']
	xp = player_stats['xp']
	played_seconds = player_stats['played_seconds']

	embed_obj = discord.Embed(title=f'{player.username} {rank_name} [{date}]', color=0x2F3136)
	embed_obj.set_thumbnail(url=f'https://skin.vimeworld.ru/head/{player.username}.png')
	embed_obj.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)

	embed_obj.add_field(name='Заработано опыта', value=f'{xp}<a:experienceorb:949583490960228382>')
	embed_obj.add_field(name='Наиграно минут', value=f'{int(played_seconds/60)}', inline=False)

	options = []
	for game in games.keys():
		game_data = games[game]
		description = f'Игр: {game_data["games"]}'
		description += f'\nПобед: {game_data["wins"]}'
		embed_obj.add_field(name=locale['games'][game]['name'], value=f'```{description}```')
		if len(options) < 25:
			options.append(SelectOption(label = locale['games'][game]['name'], value = game))

	button = Button(label="Удалить", custom_id=f'delete {ctx.author.id}', emoji=close_emoji, style=ButtonStyle.red)
	if len(options) > 0:
		select = Select(placeholder="Выберите режим...", options=options, custom_id=f'select_game {ctx.author.id} {player.id} {date}')
		await ctx.send(embed=embed_obj, components=[select, button], delete_after=600)
	else:
		await ctx.send(embed=embed_obj, components=[button], delete_after=600)

@stats.error
async def stats_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send(content=f'Не верно указаны аргументы: `{prefix}stats <ник> <дата в формате дд.мм.гггг>`', delete_after=60)
	else:
		if test_mode:
			if ctx.message.author.id == 452777504344899584:
				await ctx.send(content=f'Произошла не предвиденная ошибка:\n```{traceback.format_exc()}```')
			else:
				await ctx.send(content=f'Произошла не предвиденная ошибка:\n```{error}```')

@bot.event
async def on_button_click(interaction):
	interaction_data = interaction.component.custom_id.split(' ')
	if interaction_data[1] != str(interaction.user.id):
		await interaction.respond(content='Вы не можете взаимодействовать с этим сообщением.')
	elif interaction_data[0] == 'delete':
		await interaction.message.delete()

@bot.event
async def on_select_option(interaction):
	interaction_data = interaction.component.custom_id.split(' ') 
	if interaction_data[1] != str(interaction.user.id):
		await interaction.respond(content='Вы не можете взаимодействовать с этим сообщением.')
		return
	if interaction_data[0] == 'select_game':
		player_stats = get_player_stats(interaction_data[2], interaction_data[3])
		games = player_stats['games']
		xp = player_stats['xp']
		played_seconds = player_stats['played_seconds']

		game = interaction.values[0]

		embed_obj = interaction.message.embeds[0]

		embed_obj.clear_fields()
		embed_obj.add_field(name='Заработано опыта', value=f'{xp}<a:experienceorb:949583490960228382>')
		embed_obj.add_field(name='Наиграно минут', value=f'{int(played_seconds/60)}', inline=False)

		game_data = games[game]
		description = f'Игр: {game_data["games"]}'
		for stat in game_data.keys():
			try:
				if stat != 'games':
					description += f'\n{locale["game_stats"][game][stat]}: {int(game_data[stat])}'
			except:
				pass
		embed_obj.add_field(name=locale['games'][game]['name'], value=f'```{description}```')
		await interaction.message.edit(embed=embed_obj)
		await interaction.respond(type=6)

@bot.command()
async def info(ctx):
	embed_obj = discord.Embed(title=f'Обо мне', color=0x2F3136)
	embed_obj.set_thumbnail(url=bot.user.avatar_url)
	description = 'Привет! Я записываю все матчи и некоторую статистику игроков в свой собственный архив, чтобы любой пользователь в любой момент мог им воспользоваться. Зачем это нужно? Например узнать точное количество побед, которое ты сделал за сегодня или любой другой день, но если это не интересует, то я уверен, ты найдешь применение моему архиву.\n\n'
	description += '**Как начать пользоваться?**\n'
	description += 'Все очень просто, достаточно ввести эту команду:\n'
	description += '`.stats <Ник> <Дата>`\n'
	description += 'Где `<Ник>` - это ник игрока, статистику которого хочешь увидеть, `<Дата>` - дата в формате `дд.мм.гггг`.\n'
	description += 'Пример:\n'
	description += '`.stats FalmerF 09.03.2022`\n\n'
	description += '**Сайт**\n'
	description += 'Да-да, у меня есть свой сайт, так что если тебе удобней смотреть статистику на нем, то пользуйся: [VimeArchive.ru](https://vimearchive.ru)\n\n'
	description += '**Благодарность**\n'
	description += 'Спасибо всем, кто заинтересован в моем архиве и активно им пользуется, для меня и моего разработчика это многое значит :heart:'
	embed_obj.description = description
	embed_obj.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
	await ctx.reply(embed=embed_obj, delete_after=600)

# @bot.command()
async def actions(ctx, nick: str, date: str):
	player = find_player_by_name(nick)
	if player is None:	
		await ctx.reply(content=f'Игрок с ником `{nick}` не найден.')
		return

	try:
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
	except:
		await ctx.reply(content='Укажите дату в формате `dd.mm.yyyy`.')
		return

	playerid = player.id
	if player.id in black_list:
		await ctx.reply(content='Данные этого игрока не подлежат записи, кажется он что-то натворил :(')
		return

	rank_name = locale["ranks"][player.rank.lower()]['name']
	if rank_name != '': rank_name = f'[{rank_name}]'

	embed_obj = discord.Embed(title=f'{player.username} {rank_name} [{date}]', color=0x2F3136)
	embed_obj.set_thumbnail(url=f'https://skin.vimeworld.ru/head/{player.username}.png')
	embed_obj.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)

	player_actions = get_player_actions(player.id, date)
	if player_actions is None:
		await ctx.reply(content='Данных об игроке на указанную дату нет.')
		return

	i = 1
	for action_data in player_actions:
		actions = ast.literal_eval(action_data[2])
		date = datetime.fromisoformat(action_data[1])
		date_str = date.strftime("%H:%M:%S")

		if 'match' in actions:
			match = actions['match']
			game = match['game'].lower()
			stats = get_match_stats(match, game)
			embed_obj.add_field(name=f"[{date_str}] {locale['games'][game]['name']}", value=f'```{stats}```')
			i += 1
		if 'xp' in actions:
			xp = actions['xp']
			embed_obj.add_field(name=f"[{date_str}] Добавлено опыта", value=str(xp))
			i += 1
		if 'online' in actions:
			online = actions['online']
			embed_obj.add_field(name=f"[{date_str}] Статус онлайн", value=str(online))
			i += 1
		if 'game' in actions:
			game = actions['game']
			embed_obj.add_field(name=f"[{date_str}] Статус активности", value=game)
			i += 1
		if 'playedSeconds' in actions:
			playedSeconds = actions['playedSeconds']
			embed_obj.add_field(name=f"[{date_str}] Наиграно секунд", value=playedSeconds)
			i += 1

	if len(embed_obj.fields) >= 20:
		with open("result.txt", "w") as file:
			desc = ''
			for field in embed_obj.fields:
				desc += f'{field.name}\n{field.value}\n\n'.replace('```', '')
			embed_obj.clear_fields()
			file.write(desc)
		with open("result.txt", "rb") as file:
			await ctx.send(embed=embed_obj, file=discord.File(file, "result.txt"))
	else:
		await ctx.send(embed=embed_obj)

def find_player_by_name(player_name: str):
	try:
		return vime.get_player_by_name(player_name) 
	except:
		return None

def get_match_stats(match, game):
	description = ''
	for stat in match.keys():
		try:
			if stat != 'game':
				description += f'{locale["game_stats"][game][stat]}: {match[stat]}\n'
		except:
			pass
	return description

# @actions.error
async def actions_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send(content=f'Не верно указаны аргументы: `{prefix}actions <ник> <дата в формате дд.мм.гггг>`')
	else:
		if test_mode:
			if ctx.message.author.id == 452777504344899584:
				await ctx.send(content=f'Произошла не предвиденная ошибка:\n```{traceback.format_exc()}```')
			else:
				await ctx.send(content=f'Произошла не предвиденная ошибка:\n```{error}```')

@bot.command()
async def lb(ctx, nick: str, date: str):
	player = find_player_by_name(nick)
	date_str = ''
	if player is None:	
		await ctx.reply(content=f'Игрок с ником `{nick}` не найден.')
		return

	try:
		date_str = format_date(date)
		date = datetime.strptime(date_str, '%d.%m.%Y')
	except Exception as e:
		await ctx.reply(content='Укажите дату в формате `dd.mm.yyyy`.')
		return

	playerid = player.id
	if player.id in black_list:
		await ctx.reply(content='Данные этого игрока не подлежат записи, кажется он что-то натворил :(')
		return

	rank_name = locale["ranks"][player.rank.lower()]['name']
	if rank_name != '': rank_name = f'[{rank_name}]'

	player_lb = utils.get_player_lb_range(player.id, date, date)
	if player_lb is None:
		await ctx.reply(content='Данных об игроке на указанную дату нет.')
		return

	embed_obj = discord.Embed(title=f'{player.username} {rank_name} [{date_str}]', color=0x2F3136)
	embed_obj.set_thumbnail(url=f'https://skin.vimeworld.ru/head/{player.username}.png')
	embed_obj.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)

	for lb in player_lb:
		description = ''
		lb_name = lb_names[lb]
		for sort in player_lb[lb]:
			diff = player_lb[lb][sort]['diff']
			if diff < 0:
				diff = str(diff)
			else:
				diff = f'+{diff}'
			place = player_lb[lb][sort]['place']
			sort_name = lb_sort_locale[sort]
			description += f'{sort_name} - {place} ({diff})\n'
		embed_obj.add_field(name=lb_name, value=f'```{description}```', inline=False)

	button = Button(label="Удалить", custom_id=f'delete {ctx.author.id}', emoji=close_emoji, style=ButtonStyle.red)
	await ctx.send(embed=embed_obj, components=[button], delete_after=600)

@lb.error
async def lb_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send(content=f'Не верно указаны аргументы: `{prefix}lb <ник> <дата в формате дд.мм.гггг>`', delete_after=60)
	else:
		if test_mode:
			if ctx.message.author.id == 452777504344899584:
				await ctx.send(content=f'Произошла не предвиденная ошибка:\n```{traceback.format_exc()}```')
			else:
				await ctx.send(content=f'Произошла не предвиденная ошибка:\n```{error}```')

@bot.command()
async def top(ctx, table: str):
	if table != 'xp' and table != 'online' and table != 'wins' and table != 'games':
		await ctx.send(content=f'Не верно указаны аргументы: `{prefix}top [xp/online/games/wins]`', delete_after=60)
		return

	embed_obj = discord.Embed(title=top_title_locale[table], color=0x2F3136)
	embed_obj.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
	embed_obj.description = make_top_description(table, 0)

	button = Button(label="Удалить", custom_id=f'delete {ctx.author.id}', emoji=close_emoji, style=ButtonStyle.red)
	await ctx.send(embed=embed_obj, components=[button], delete_after=600)

def make_top_description(table: str, page: int):
	description = ''
	top_list = players_lb[table]
	start_element = 25*page
	i = start_element
	while i < start_element+25:
		data = top_list[i]
		description += f'{(i+1)}. `{data[0]}` — {data[1]}'
		i += 1
	return description

@lb.error
async def top_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send(content=f'Не верно указаны аргументы: `{prefix}top [xp/online/games/wins]`', delete_after=60)
	else:
		if test_mode:
			if ctx.message.author.id == 452777504344899584:
				await ctx.send(content=f'Произошла не предвиденная ошибка:\n```{traceback.format_exc()}```')
			else:
				await ctx.send(content=f'Произошла не предвиденная ошибка:\n```{error}```')

def log_cycle():
	global commands_per_day

	date = datetime.now()
	while True:
		cls()
		if date.day != datetime.now().day:
			commands_per_day = 0

		print(f'Bot Name: {bot_name}')
		print(f'Guilds Count: {len(bot.guilds)}')
		print(f'Commands Run Count: {commands_per_day}')
		time.sleep(10)

threading.Thread(target=update).start()

while True:
	bot.run(token, bot=True)
	time.sleep(60)