from flask import Flask, render_template, request, make_response, jsonify
from datetime import datetime, timedelta
import os, sys
import time
import threading
import __main__
import random
import string
import asyncio
import ast

sys.path.insert(1, os.path.abspath('..'))
sys.path.insert(1, os.path.abspath('../vime_api'))
import data_base
import vime
import utils
import rank_calc
from utils import cls
from vime import Vime, VimeError
import logging

app=Flask(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

vime = Vime()
locale = utils.get_locale('../locale.txt')
lb_data = {}
last_status = []

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
	if user != None and user.get_param('is_admin') == True:
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

@app.route('/ranks_guide') 
def ranks_guide():
	trigger_analytics('v_ranks_guide')
	check_visitor((request.environ['HTTP_X_FORWARDED_FOR']) if 'HTTP_X_FORWARDED_FOR' in request.environ else (None))
	return render_template('ranks_guide.html')

@app.route('/auth') 
def player_auth():
	trigger_analytics('v_auth')
	check_visitor((request.environ['HTTP_X_FORWARDED_FOR']) if 'HTTP_X_FORWARDED_FOR' in request.environ else (None))
	return render_template('player_auth.html')

@app.route('/api/auth/player/<string:key>')
def api_auth_player(key):
	token = vime.get_token(key);
	if(token.valid == False or token.owner == None):
		return {'error': '?????????? ???? ????????????????????????????.'}

	user = user_manager.get_or_create_user(token.owner.username, token.owner.id)
	return {'token': user.token}

@app.route('/api/player/<string:token>')
def api_player(token):
	user = user_manager.get_user_by_token(token)
	if user == None:
		return {'error': '???? ?????????????? ????????????????????????????.'}
	else:
		return {'id': user.id, 'is_admin': user.get_param('is_admin')}

@app.route('/api/player/info/<int:id>')
def api_player_info(id):
	user = user_manager.get_user_by_id(id)
	if user == None:
		return {'error': 'No data'}
	else:
		return {'username': user.name, 'info': user.base_data}

@app.route('/api/<int:player_id>/ranks')
def api_player_ranks(player_id):
	try:
		data = asyncio.run(user_manager.users_DB.get_async('points', '*', f'id={player_id}'))
		if data == None: return {}
		ranks = ast.literal_eval(data[2])
		points = ast.literal_eval(data[1])

		result = {}
		for game in points:
			try:
				result[game] = {'rank': ranks[game], 'points': points[game]}
			except ValueError:
				pass

		return result
	except:
		return {}

@app.route('/api/player/status', methods=['POST'])
def api_player_status():
	if not request.is_json:
		return {'result': 'Not json'}

	request_data = request.json

	if not 'token' in request_data:
		return {'result': 'Bad token'}
	elif not 'user_id' in request_data:
		return {'result': 'Need user id'}
	elif not 'status' in request_data or len(request_data['status']) > 150:
		return {'result': '???????????????? ???????????? ??????????????'}

	token = request_data['token']
	status = request_data['status']
	user_id = request_data['user_id']

	user = user_manager.get_user_by_token(token)
	if user is None:
		return {'result': 'Bad token'}
	target_user = user_manager.get_user_by_id(user_id)
	if target_user is None:
		return {'result': 'Bad user id'}
	elif not user.get_param('is_admin') and target_user != user:
		return {'result': '???? ???????????? ???????????? ???????????? ???????? ????????????!'}
	user_manager.set_user_data(target_user, 'status', status)

	if target_user.id not in last_status:
		last_status.append(target_user.id)
		if len(last_status) > 50:
			last_status.pop(0)

	return {'result': 'ok'}

@app.route('/api/player/status/last')
def api_player_status_last():
	status_json = {}
	i = len(last_status)-1
	while i >= 0:
		user = user_manager.get_user_by_id(last_status[i])
		if user.base_data.get('status') != '':
			status_json[i] = {'id': last_status[i], 'status': user.base_data.get('status')}
		i -= 1
	return status_json

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
		return lb_data[f'{table}_top']
	except:
		return {}

@app.route('/api/update') 
def api_update():
	trigger_analytics('a_update')

	return {'version': '1.5', 'title': '????????????????????', 'message': 
'''??????????????????:
??? ???? ?????????????????? ???? ?????????? ????????! ???????????? ???? ?????????? ???????????????????????? VPN!
'''}

@app.route('/api/locale/<string:locales>') 
def api_locale(locales):
	trigger_analytics('a_locale')
	locale_arr = locales.split(',')
	locale_result = {}
	for loc in locale_arr:
		locale_result[loc] = locale[loc]
	return locale_result

async def update_cycle():
	global analytics
	global unique_visitors
	global lb_data

	date = datetime.now()
	while True:
		if date.day != datetime.now().day:
			date = datetime.now()
			analytics = {'v': 0, 'a': 0, 'v_main': 0, 'v_player': 0, 'v_lb': 0}
			unique_visitors = []

		DB = data_base.DataBase('', file_name='../user_lb.db')

		lb_list = await DB.get_tables_list_async()
		for d in lb_list:
			lb_name = d[0]
			if lb_name == 'daily_activity': continue
			lb_data[lb_name] = await make_top_list(DB, lb_name)

		time.sleep(600)

async def make_top_list(DB, table):
	data = await DB.get_async(table, '*', type='all')
	top_list = {}
	num = 0
	for d in data:
		top_list[num] = {'id': d[0], 'stat': d[1]}
		num += 1
	return top_list

def run_update_async_task():
    asyncio.run(update_cycle())

threading.Thread(target=run_update_async_task).start()

class UserManager:
	def __init__(self):
		self.users = {}
		asyncio.run(self.load_users())

	async def load_users(self):
		self.users_DB = data_base.DataBase('', file_name='../users.db')
		await asyncio.sleep(0.1)
		data = await self.users_DB.get_async('users', '*', type='all')
		for user in data:
			u = User(user[0], user[1], user[2], ast.literal_eval(user[3]))
			self.users[user[1]] = u

	def new_user(self, name, id, token, base_data={}):
		user = User(name, id, token, base_data)
		self.users[id] = user
		self.users_DB.insert_async('users', f'"{name}", {id}, "{token}", "{base_data}"')
		return user

	def get_or_create_user(self, name, id):
		if id not in self.users:
			auth_token = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))
			return self.new_user(name, id, auth_token)
		else:
			return self.users[id]

	def get_user_by_token(self, token):
		for id in self.users:
			if self.users[id].token == token:
				return self.users[id]
		return None

	def set_user_data(self, user, param, value):
		value = value.replace('"', '')
		user.base_data[param] = value
		self.users_DB.update_async('users', f'base_data="{str(user.base_data)}"', f'id={user.id}')

	def get_user_by_id(self, id):
		if id in self.users:
			return self.users[id]
		return None

class User:
	def __init__(self, name: str, id: int, token: str, base_data={}):
		self.name = name
		self.id = id
		self.token = token
		self.base_data = base_data

	def get_param(self, param):
		if param in self.base_data:
			return self.base_data[param]
		return None

user_manager = UserManager()

app.run(debug=False, port=8000)