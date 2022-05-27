from flask import Flask, render_template, request, make_response, jsonify
from datetime import datetime, timedelta
import os, sys
import time
import threading
import __main__
import requests
import random
import string

sys.path.insert(1, os.path.abspath('..'))
sys.path.insert(1, os.path.abspath('../vime_api'))
import DataBase
import vime
import utils
from utils import cls
from vime import Vime, VimeError
import logging

app=Flask(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

#region secret_key
admin_key = 'KMHEGQqU4fTxJNS2PZun2jXee5tr4VW26cmkt97UkjkVHJ5gGHRdRaGqK8RfAc8zAyfGaT2sWUJc9SdMAwMbU9Qwyn3DKgNvvJWQ'
app.config['SECRET_KEY'] = 'eYmud3YZP4Ms97d7'
#endregion

vime = Vime()
black_list = utils.get_black_list('../black_list.txt')
locale = utils.get_locale('../locale.txt')
lb_data = {}

analytics = {'v': 0, 'a': 0, 'v_main': 0, 'v_player': 0, 'v_lb': 0}
unique_visitors = []

def trigger_analytics(name, count=1):
	if name in analytics: analytics[name] += count
	else: analytics[name] = count
	if name.startswith('v_'): analytics['v'] += count
	elif name.startswith('a_'): analytics['a'] += count

def check_visitor(ip):
	if ip not in unique_visitors:
		unique_visitors.append(ip)

@app.route('/admin') 
def admin():
	trigger_analytics('v_admin')
	check_visitor((request.environ['HTTP_X_FORWARDED_FOR']) if 'HTTP_X_FORWARDED_FOR' in request.environ else (None))
	token = request.cookies.get('auth_token')
	user = user_manager.get_user_by_token(token)
	if user != None and user.is_admin:
		v_data = {}
		api_data = {}
		for d in analytics:
			if d.startswith('a_'):
				api_data[d] = analytics[d]
			elif d.startswith('v_'):
				v_data[d] = analytics[d]
		api_data['a_all'] = analytics['a']
		v_data['v_all'] = analytics['v']
		return render_template('admin.html', visitors=v_data, api=api_data, unique_visitors=len(unique_visitors))
	return {'error': '\_(^_^)_/'}

@app.route('/auth') 
def player_auth():
	trigger_analytics('v_auth')
	check_visitor((request.environ['HTTP_X_FORWARDED_FOR']) if 'HTTP_X_FORWARDED_FOR' in request.environ else (None))
	return render_template('player_auth.html')

@app.route('/api/auth/player/<string:key>')
def api_auth_player(key):
	users_DB = DataBase.DataBase('', file_name='users.db')
	token = vime.get_token(key);
	if(token.valid == False or token.owner == None):
		return {'error': 'Токен не действительный.'}

	user = user_manager.get_or_create_user(token.owner.id)
	return {'token': user.token}

@app.route('/api/player/<string:token>')
def api_player(token):
	user = user_manager.get_user_by_token(token)
	if user == None:
		return {'error': 'Не удалось авторизоваться.'}
	else:
		return {'id': user.id, 'is_admin': user.is_admin}

@app.route('/') 
def index():
	trigger_analytics('v_main')
	check_visitor((request.environ['HTTP_X_FORWARDED_FOR']) if 'HTTP_X_FORWARDED_FOR' in request.environ else (None))
	return render_template('index.html')

@app.route('/leaderboards') 
def leaderboards():
	trigger_analytics('v_lb')
	check_visitor((request.environ['HTTP_X_FORWARDED_FOR']) if 'HTTP_X_FORWARDED_FOR' in request.environ else (None))
	return render_template('leaderboard.html')

@app.route('/player/<string:username>') 
def players_info(username):
	trigger_analytics('v_player')
	check_visitor((request.environ['HTTP_X_FORWARDED_FOR']) if 'HTTP_X_FORWARDED_FOR' in request.environ else (None))
	return render_template('player_info.html', username=username)

@app.route('/guild/<int:id>') 
def guild(id):
	trigger_analytics('v_guild')
	check_visitor((request.environ['HTTP_X_FORWARDED_FOR']) if 'HTTP_X_FORWARDED_FOR' in request.environ else (None))
	return render_template('guild.html', id=id)

@app.route('/api/<int:player_id>/stats') 
def api_player_stats(player_id: int):
	trigger_analytics('a_player_stats')
	try:
		start_date = datetime.strptime(request.args.get('start_date'), '%d.%m.%Y')
		end_date = datetime.strptime(request.args.get('end_date'), '%d.%m.%Y')
	except:
		return {}

	stats = utils.get_player_stats_range(player_id, start_date, end_date)
	if stats == None:
		return {}
	return stats

@app.route('/api/<int:player_id>/actions') 
def api_player_actions(player_id: int):
	trigger_analytics('a_player_actions')
	try:
		start_date = datetime.strptime(request.args.get('start_date'), '%d.%m.%Y')
		end_date = datetime.strptime(request.args.get('end_date'), '%d.%m.%Y')
	except:
		return {}

	actions = utils.get_player_actions_range(player_id, start_date, end_date)
	if actions == None:
		return {}
	return {'actions': actions}

@app.route('/api/<int:player_id>/leaderboard') 
def api_player_lb(player_id: int):
	trigger_analytics('a_player_lb')
	try:
		start_date = datetime.strptime(request.args.get('start_date'), '%d.%m.%Y')
		end_date = datetime.strptime(request.args.get('end_date'), '%d.%m.%Y')
	except:
		return {}

	lb = utils.get_player_lb_range(player_id, start_date, end_date)
	if lb == None:
		return {}
	return lb

@app.route('/api/leaderboard/<string:table>') 
def api_leaderboard(table: str):
	global lb_data
	trigger_analytics('a_lb')

	try:
		return lb_data[table]
	except:
		return {}

@app.route('/api/update') 
def api_update():
	trigger_analytics('a_update')

	return {'version': '1.5', 'title': 'Информация', 'message': 
'''Изменения:
• Мы переехали на новый хост! Теперь не нужно использовать VPN!
'''}

@app.route('/api/locale') 
def api_locale():
	trigger_analytics('a_locale')
	return locale

@app.route('/api/black_list') 
def api_black_list():
	trigger_analytics('a_black_list')
	return {'ids': black_list}

def update_cycle():
	global analytics
	global unique_visitors
	global lb_data

	date = datetime.now()
	while True:
		try:
			if date.day != datetime.now().day:
				date = datetime.now()
				analytics = {'v': 0, 'a': 0, 'v_main': 0, 'v_player': 0, 'v_lb': 0}
				unique_visitors = []
			DB = DataBase.DataBase('', file_name='../user_lb.db')
			lb_data['xp'] = make_top_list(DB, 'xp')
			lb_data['online'] = make_top_list(DB, 'online')
			lb_data['games'] = make_top_list(DB, 'games')
			lb_data['wins'] = make_top_list(DB, 'wins')
			time.sleep(600)
		except:
			time.sleep(10)

def make_top_list(DB, table):
	data = DB.get(table+'_top', '*', type='all')
	top_list = {}
	num = 0
	for d in data:
		top_list[num] = {'id': d[0], 'stat': d[1]}
		num += 1
	return top_list

threading.Thread(target=update_cycle).start()

class UserManager:
	def __init__(self):
		self.users_to_add = []
		self.users = {}
		users_DB = DataBase.DataBase('', file_name='../users.db')
		data = users_DB.get('users', '*', type='all')
		for user in data:
			u = User(user[0], user[1], user[2])
			self.users[user[0]] = u
		threading.Thread(target=self.add_cycle).start()

	def add_cycle(self):
		users_DB = DataBase.DataBase('', file_name='../users.db')
		while True:
			while len(self.users_to_add) > 0:
				user = self.users_to_add.pop()
				users_DB.insert('users', f'{user[1]}, "{user[2]}", {user[3]}')
				self.users[user[1]] = user[0]
			time.sleep(1)

	def new_user(self, id, token, is_admin=False):
		user = User(id, token, is_admin)
		self.users_to_add.append([user, id, token, is_admin])
		return user

	def get_or_create_user(self, id):
		if id not in self.users:
			auth_token = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))
			return self.new_user(id, auth_token)
		else:
			return self.users[id]

	def get_user_by_token(self, token):
		for id in self.users:
			if self.users[id].token == token:
				return self.users[id]
		return None

class User:
	def __init__(self, id: int, token: str, is_admin: bool):
		self.id = id
		self.token = token
		self.is_admin = is_admin

user_manager = UserManager()

app.run(debug=False, port=8000)